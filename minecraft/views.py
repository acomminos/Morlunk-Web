from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.template import RequestContext, Template
from django.shortcuts import render_to_response, redirect
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from minecraft.models import MinecraftAccount, MinecraftItem, PaosoCoupon, MinecraftServer, MinecraftStash, MinecraftStashItem
from minecraft.forms import MinecraftAccountForm, GriefReportForm
import datetime
import traceback
from decimal import Decimal

# Constants

INVALID_REQUEST_RESPONSE = "invalid_request"
INSUFFICIENT_FUNDS_RESPONSE = "insufficient_funds"
INVALID_KEY_RESPONSE = "invalid_key"
NO_MINECRAFT_ACCOUNT_RESPONSE = "no_minecraft_account"
NO_AUTH_RESPONSE = "no_auth"
NO_USER_RESPONSE = "no_user"
SUCCESS_RESPONSE = "success"
ERROR_RESPONSE = "error"

# Utility methods

def get_minecraft_stash(account):
    """Obtains the passed minecraft account's minecraft stash or creates an empty one."""
    if MinecraftStash.objects.filter(owner=account).count() == 0:
        # Create a stash.
        stash = MinecraftStash.objects.create(owner=account)
        stash.save()
    else:
        # Retrieve existing stash.
        stash = MinecraftStash.objects.get(owner=account)
    return stash

def is_server_authorized(api_key):
    return MinecraftServer.objects.filter(api_key=api_key).count() > 0

# Views

""" So we can serialize the paoso values in simplejson. """
class DecimalEncoder(simplejson.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)

def minecraft_link(request):
    # Make sure user is logged in
    if request.user.is_authenticated() is False:
        return redirect("/account/login/")

    # If user already has minecraft account, go away.
    if MinecraftAccount.objects.filter(user=request.user).count() != 0:
        return redirect("/account/")

    if request.method == 'POST':
        form = MinecraftAccountForm(request.POST)
        if form.is_valid():
            #account = form.save() Don't save form, create object manually so we can make sure the authorize user gets to add it.
            account = MinecraftAccount.objects.create(minecraft_username=form.cleaned_data['minecraft_username'],
                                                      screen_name=form.cleaned_data['screen_name'],
                                                     user=request.user)
            account.save()
            # Redirect back to account page
            return redirect("/account/")
    else:
        form = MinecraftAccountForm(initial={'user': request.user})
    
    return render_to_response('minecraft_link.html',
                                  { 'form': form },
                                  RequestContext(request))

def minecraft_update(request):
    try:
        api_key = request.REQUEST["key"]

        if is_server_authorized(api_key):
            minecraft_username = request.REQUEST["minecraft_username"]
            screen_name = request.REQUEST["screen_name"]
            banned = request.REQUEST["banned"]
            #paosos = request.REQUEST["paosos"] DO NOT ALLOW UPDATE OF PAOSOS WITH UPDATE, PERIOD!

            minecraft_user = MinecraftAccount.objects.get(minecraft_username=minecraft_username) # Get user associated with account name

            minecraft_user.minecraft_username = minecraft_username
            minecraft_user.screen_name = screen_name
            minecraft_user.banned = banned.lower() == 'true'

            minecraft_user.save()

            response = {"result": SUCCESS_RESPONSE}
        else:
            response = {"result": INVALID_KEY_RESPONSE}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response))

def minecraft_grief(request):
    # Make sure user is logged in
    if request.user.is_authenticated() is False:
        return redirect("/account/")

    if request.method == 'POST':
        form = GriefReportForm(request.POST)
        if form.is_valid():
            form.save()
            # Mail me
            send_mail("Grief report",
                        "There has been a new grief report from "+form.cleaned_data["grief_submitter"].username+". Please check it at the Morlunk Co. admin interface.",
                        "grief@morlunk.com",
                        ['andrewcomminos@gmail.com'])
            return redirect("/account/")
    else:
        form = GriefReportForm(initial={'grief_submitter': request.user,
                                        'grief_date': datetime.date.today})
    
    return render_to_response('minecraft_grief.html',
                                  { 'form': form },
                                  RequestContext(request))

@require_http_methods(["GET", "POST"])
def minecraft_get(request):
    try:
        mineuser = request.REQUEST["username"]

        # Check if there is a linked username in the database, also share owner info
        accounts = MinecraftAccount.objects.filter(minecraft_username=mineuser)
        if accounts.count() > 0:
            account = MinecraftAccount.objects.get(minecraft_username=mineuser)
            accountdict = model_to_dict(account)
            donatordict = model_to_dict(account.donator_level)
            response = {"result": SUCCESS_RESPONSE, "user": accountdict, "donator": donatordict}
        else:
            response = {"result": NO_MINECRAFT_ACCOUNT_RESPONSE}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response))

def minecraft_user_get(request):
    """Used by Morlunk Android app. Only retrieves the MinecraftAccount object."""
    if request.user.is_authenticated() is False:
        return HttpResponse(simplejson.dumps({'result': NO_AUTH_RESPONSE}), mimetype="application/json")

    try:
        account = MinecraftAccount.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(simplejson.dumps({'result': NO_MINECRAFT_ACCOUNT_RESPONSE}), mimetype="application/json")

    accountdict = model_to_dict(account)
    return HttpResponse(simplejson.dumps({'result': 'success', 'user': accountdict}), mimetype="application/json")

@require_http_methods(["GET", "POST"])
def minecraft_give(request):
    try:

        api_key = request.REQUEST["key"]

        if is_server_authorized(api_key):
            fromname = request.REQUEST["from"]
            toname = request.REQUEST["to"]
            amount = int(request.REQUEST["amount"])

            fromuser = MinecraftAccount.objects.get(minecraft_username=fromname)
            touser = MinecraftAccount.objects.get(minecraft_username=toname)

            if fromuser.paosos < amount:
                return HttpResponse(simplejson.dumps({"result": INSUFFICIENT_FUNDS_RESPONSE}))

            fromuser.paosos -= amount
            touser.paosos += amount
            
            fromuser.save()
            touser.save()

            response = {"result": SUCCESS_RESPONSE}
        else:
            response = {"result": INVALID_KEY_RESPONSE}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response), mimetype="application/json")

"""
@require_http_methods(["POST"])
def minecraft_give_web(request):
    if request.user.is_authenticated() is False:
        return redirect("/account/")

    try:
        account = MinecraftAccount.objects.get(user=request.user)
        request.POST["from"] = account.minecraft_username # Override "from" field with user name.
        minecraft_give(request)
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response))
"""

def minecraft_rates(request):
    return render_to_response('rates.html',
                                { 'minecraft_items': MinecraftItem.objects.filter(sell_value__gt=0) },
                                RequestContext(request))

def minecraft_store(request, format='html'):

    items = MinecraftItem.objects.filter(buy_value__gt=0)

    if format == 'html':
        if request.user.is_authenticated() is False:
            return redirect("/account/")

        user = request.user

        if MinecraftAccount.objects.filter(user=user).count() == 0:
            return redirect("/minecraft/link/")

        minecraft_account = MinecraftAccount.objects.get(user=user)

        return render_to_response('store.html',
                                    { 'minecraft_account': minecraft_account,
                                      'minecraft_items': items},
                                    RequestContext(request))
    elif format == 'json':
        itemlist = []
        for item in items:
            itemlist.append(model_to_dict(item, exclude='icon'))
        return HttpResponse(simplejson.dumps({'result': SUCCESS_RESPONSE, 'items': itemlist}), mimetype="application/json")


def minecraft_buy(request):
    if request.user.is_authenticated() is False:
        return HttpResponse(simplejson.dumps({'result': NO_AUTH_RESPONSE}))

    user = request.user

    if MinecraftAccount.objects.filter(user=user).count() == 0:
        return HttpResponse(simplejson.dumps({'result': NO_MINECRAFT_ACCOUNT_RESPONSE}))

    minecraft_account = MinecraftAccount.objects.get(user=user)

    # TODO except errors
    item_id = int(request.GET['item'])
    item = MinecraftItem.objects.get(id=item_id)
    cost = item.buy_value
    if minecraft_account.paosos >= cost:
        minecraft_account.paosos -= cost
        minecraft_account.save()
        stash = get_minecraft_stash(minecraft_account)
        stash_item = MinecraftStashItem.objects.create(item=item, stash=stash, amount=item.buy_sell_quantity, damage_value=item.damage_value)
        stash_item.save()
        response = SUCCESS_RESPONSE
    else:
        response = INSUFFICIENT_FUNDS_RESPONSE
    return HttpResponse(simplejson.dumps({'result': response}))

def minecraft_paoso_redeem(request):
    response = ""

    if request.user.is_authenticated() is False:
        return redirect("/account/")

    if request.method == 'POST':
        try:
            key = request.POST['key']
            user = request.user
            minecraft_account = MinecraftAccount.objects.get(user=user)
            voucher = PaosoCoupon.objects.get(key=key)

            if voucher.redeemed:
                response = "Coupon already claimed!"
            else:
                minecraft_account.paosos+=voucher.value
                voucher.redeemed = True
                voucher.redeemer = minecraft_account
                voucher.redemption_date = datetime.datetime.now()

                minecraft_account.save()
                voucher.save()
                # TODO maybe a form approach?
                response = "Success! Granted "+minecraft_account.screen_name+" "+str(voucher.value)+" paosos."
        except:
            response = "Key not found!"
    return render_to_response('coupon.html',
                                { 'minecraft_accounts': MinecraftAccount.objects.all(),
                                  'response': response },
                                RequestContext(request))

@require_http_methods(["GET", "POST"])
def minecraft_sell_value(request):
    try:
        data_value = request.REQUEST["data"]
        damage_value = request.REQUEST["damage"]
        amount = request.REQUEST["amount"] # TODO remove amount all together

        item = MinecraftItem.objects.get(data_value=data_value, damage_value=damage_value)

        # Get individual rate and multiply by amount
        value = Decimal(Decimal(item.sell_value)/Decimal(item.buy_sell_quantity)) * Decimal(amount)
        response = {"result": SUCCESS_RESPONSE, "value": value}
    except ObjectDoesNotExist:
        response = {"result": "item_not_found"}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response, cls=DecimalEncoder))


# Stash code

def minecraft_stash(request, user_name):
    account = MinecraftAccount.objects.get(minecraft_username=user_name)
    stash = MinecraftStash.objects.get(owner=account)

    stash_items = MinecraftStashItem.objects.filter(stash=stash)

    return render_to_response('stash.html',
                              { 'stash_items': stash_items },
                              RequestContext(request))

@require_http_methods(["GET", "POST"])
def minecraft_stash_get(request):
    try:
        account_name = request.REQUEST["username"]
        account = MinecraftAccount.objects.get(minecraft_username=account_name)

        # Get/create stash
        stash = get_minecraft_stash(account)

        stash_items = MinecraftStashItem.objects.filter(stash=stash)

        stash_data = { 'name': stash.name, 
                       'size': stash.size,
                       'items': [] }

        for stash_item in stash_items:
            item_data = { 'name': stash_item.item.name,
                          'data_value': stash_item.item.data_value,
                          'damage_value': stash_item.damage_value, # use stash item's item value
                          'amount': stash_item.amount }
            stash_data['items'].append(item_data)

        response = {"result": SUCCESS_RESPONSE, "stash": stash_data}
    except ObjectDoesNotExist:
        response = {"result": NO_USER_RESPONSE}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}
    return HttpResponse(simplejson.dumps(response))

# Disable CSRF so we don't have any complications.
@csrf_exempt
def minecraft_stash_update(request):
    try:
        api_key = request.REQUEST["key"]

        if is_server_authorized(api_key):
            mineuser = request.REQUEST["username"]

            minecraft_account = MinecraftAccount.objects.get(minecraft_username=mineuser)

            item_data = request.REQUEST["items"]
            parsed_contents = simplejson.loads(item_data)

            # Get and clear stash
            stash = get_minecraft_stash(minecraft_account)
            # Remove old stash items
            MinecraftStashItem.objects.filter(stash=stash).delete()

            for item in parsed_contents:
                data_value = item['data_value']
                damage_value = item['damage_value']
                amount = item['amount']

                # Make sure there is minecraft item with its data_value in DB for it. Create item if not that'll have to be identified by Shayan. Do NOT create for individual damage values.
                if MinecraftItem.objects.filter(data_value=data_value, damage_value=damage_value).count() > 0:
                    minecraft_item = MinecraftItem.objects.get(data_value=data_value, damage_value=damage_value)
                elif MinecraftItem.objects.filter(data_value=data_value).count() > 0:
                    minecraft_item = MinecraftItem.objects.get(data_value=data_value)
                else: # No item exists for this data value
                    minecraft_item = MinecraftItem.objects.create(data_value=data_value, damage_value=0)
                    minecraft_item.save()

                # Create stash item
                stash_item = MinecraftStashItem.objects.create(item=minecraft_item, stash=stash, amount=amount, damage_value=damage_value)
                stash_item.save()

            # Add new items
            stash.save()
            response = {"result": SUCCESS_RESPONSE}
        else:
            response = {"result": INVALID_KEY_RESPONSE}
    except KeyError:
        response = {"result": INVALID_REQUEST_RESPONSE}
    except:
        response = {"result": ERROR_RESPONSE}

    return HttpResponse(simplejson.dumps(response))
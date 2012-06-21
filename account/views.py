from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.template import RequestContext, Template
from django.shortcuts import render_to_response, redirect
from account.forms import RegisterForm

from minecraft.models import MinecraftAccount

# Create your views here.

def control_panel(request):
    # Make sure user is authenticated
    if request.user.is_authenticated():
        # Get linked minecraft account if applicable
        minecraft_account = None
        if MinecraftAccount.objects.filter(user=request.user).count() > 0:
            minecraft_account = MinecraftAccount.objects.get(user=request.user)
        # Display panel
        return render_to_response('control_panel.html',
                                  { 'user': request.user,
                                    'minecraft_account': minecraft_account },
                                  RequestContext(request))
    else:
        # Go to login page
        return redirect("/account/login/")

def user_login(request):
    # Handle login requests
    if request.POST:
        # Attempt to log in with post data
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Go to control panel
                return redirect("/account/")
            else:
                # Invalid credentials
                return render_to_response('login.html',
                                          { 'error': True },
                                          RequestContext(request))
        except KeyError:
            # Return the login page with the error message displayed
            return render_to_response('login.html',
                                  { 'error': True },
                                  RequestContext(request))

    # Do something, dunno what
    if request.user.is_authenticated() is False:
        return render_to_response('login.html',
                                  { },
                                  RequestContext(request))
    else:
        # Redirect to control panel if logged in
        return redirect("/account/")

def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
        # TODO show logout message
        return redirect("/")

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Log user in
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password'])
            login(request, user)
            return redirect('/account/') # Redirect to account control panel
    else:
        form = RegisterForm()
    return render_to_response('register.html',
                              { 'form':  form },
                              RequestContext(request))
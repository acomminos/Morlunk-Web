from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import random
import string

# Create your models here.

class MinecraftServer(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    api_key = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.name

class MinecraftServerAdmin(admin.ModelAdmin):
    exclude = ['api_key']
    list_display = ('name', 'description', 'api_key')

    def save_model(self, request, obj, form, change):
        obj.api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(64)) # Generate 64 character alphanumeric string
        obj.save()

class DonatorLevel(models.Model):
    MINE_COLOR_CODES = (
            (0, 'Black'),
            (1, 'Dark Blue'),
            (2, 'Dark Green'),
            (3, 'Dark Aqua'),
            (4, 'Dark Red'),
            (5, 'Purple'),
            (6, 'Gold'),
            (7, 'Gray'),
            (8, 'Dark Gray'),
            (9, 'Indigo'),
            (10, 'Bright Green'),
            (11, 'Aqua'),
            (12, 'Red'),
            (13, 'Pink'),
            (14, 'Yellow'),
            (15, 'White'),
            )

    name = models.CharField(max_length=16)
    description = models.CharField(max_length=200)
    colorcode = models.IntegerField(max_length=2, choices=MINE_COLOR_CODES)

    def __unicode__(self):
        return self.name

class DonatorLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'colorcode')

class MinecraftAccount(models.Model):
    minecraft_username = models.CharField(max_length=16, unique=True)
    screen_name = models.CharField(max_length=16)
    paosos = models.IntegerField(default=0)
    #creation_date = models.DateField()
    banned = models.BooleanField(default=False)
    user = models.ForeignKey(User)
    donator_level = models.ForeignKey(DonatorLevel) # default commoner, TODO make more reliable

    def __unicode__(self):
        return self.minecraft_username

class MinecraftAccountAdmin(admin.ModelAdmin):
    list_display = ('minecraft_username', 'screen_name', 'user', 'paosos', 'donator_level', 'banned')

class MinecraftItem(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=50, default="Unknown")
    icon = models.ImageField(upload_to="minecraft_icons/", blank=True)
    data_value = models.IntegerField(max_length=4)
    damage_value = models.IntegerField(max_length=4)
    # These values can be null for stash purposes.
    stack_size = models.IntegerField(max_length=2, blank=True, null=True, default=64)
    buy_value = models.IntegerField(max_length=7, blank=True, null=True, default=0)
    sell_value = models.IntegerField(max_length=7, blank=True, null=True, default=0)
    buy_sell_quantity = models.IntegerField(max_length=3, blank=True, null=True, default=0)

    def __unicode__(self):
        return self.name+" ("+str(self.data_value)+","+str(self.damage_value)+")"

class MinecraftItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_value', 'damage_value', 'stack_size', 'buy_value', 'sell_value', 'buy_sell_quantity')

class MinecraftStash(models.Model):
    name = models.CharField(max_length=50, default="Morlunk Co. Stash")
    owner = models.ForeignKey(MinecraftAccount)
    contents = models.ManyToManyField(MinecraftItem, through='MinecraftStashItem')
    size = models.IntegerField(max_length=2, default=54)

    def __unicode__(self):
        return self.owner.screen_name+"'s stash"

class MinecraftStashItem(models.Model):
    amount = models.IntegerField(max_length=2)
    item = models.ForeignKey(MinecraftItem)
    damage_value = models.IntegerField(max_length=4)
    stash = models.ForeignKey(MinecraftStash)

    def __unicode__(self):
        return self.stash.owner.screen_name+"'s "+str(self.amount)+" "+self.item.__unicode__()

class GriefReport(models.Model):
    grief_submitter = models.ForeignKey(User, related_name='grief_submitter_user')
    grief_date = models.DateField()
    grief_location = models.CharField(max_length=100)
    stolen_items_or_damage = models.TextField()
    paoso_value = models.IntegerField(max_length=10, blank=True)
    suspects = models.ManyToManyField(User, related_name='grief_suspect_users')
    comments = models.TextField()

class GriefReportAdmin(admin.ModelAdmin):
    list_display = ('grief_submitter', 'grief_date', 'paoso_value')

class PaosoCoupon(models.Model):
    key = models.CharField(max_length=14)
    value = models.IntegerField(max_length=8)
    redeemed = models.BooleanField()
    redeemer = models.ForeignKey(MinecraftAccount, blank=True, null=True)
    redemption_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.key

class PaosoCouponAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'redeemed', 'redeemer', 'redemption_date')
    exclude = ['key']

    def save_model(self, request, obj, form, change):
        obj.key = ''.join(random.sample(string.uppercase, 14)) # Generate 14 character key
        obj.save()
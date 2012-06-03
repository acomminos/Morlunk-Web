from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.

class PaomanAccount(models.Model):
	user = models.ForeignKey(User)
	creation_date = models.DateField()

class PaomanAccountAdmin(admin.ModelAdmin):
	list_display = ('user', 'creation_date')
from django import forms
from django.db import models
from django.forms import ModelForm
from minecraft.models import MinecraftAccount, GriefReport

class MinecraftAccountForm(ModelForm):
	class Meta:
		model = MinecraftAccount
		fields = ["minecraft_username", "screen_name"]

class GriefReportForm(ModelForm):
	class Meta:
		model = GriefReport
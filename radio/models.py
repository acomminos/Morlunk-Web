from django.db import models
from django.contrib import admin

class Radio(models.Model):
	name = models.CharField(max_length=50)
	playing = models.BooleanField(default=False)

# Create your models here.
class RadioItem(models.Model):
	user_title = models.CharField(max_length=200)
	video_id = models.CharField(max_length=20)
	submission_date = models.DateField()
	played = models.BooleanField(default=False)

class RadioItemManager(admin.ModelAdmin):
	list_display = ('user_title', 'video_id', 'submission_date', 'played')
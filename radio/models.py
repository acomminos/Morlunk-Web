from django.db import models
from django.contrib import admin

# Create your models here.

class RadioItem(models.Model):
	user_title = models.CharField(max_length=200)
	video_id = models.CharField(max_length=20)
	queue_time = models.DateTimeField(auto_now=True) # Time it was queued- used to manage order of replayed items
	played = models.BooleanField(default=False)

class Radio(models.Model):
	name = models.CharField(max_length=50)
	playing = models.BooleanField(default=False)
	vlc_pid = models.IntegerField()
	#queue = models.ManyToManyField(RadioItem)

class RadioItemManager(admin.ModelAdmin):
	list_display = ('user_title', 'video_id', 'queue_time', 'played')
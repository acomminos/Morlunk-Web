from django.db import models
from django.contrib import admin

class Page(models.Model):
    identifier = models.CharField(max_length=10)
    title = models.CharField(max_length=20)
    body = models.TextField()

    def __unicode__(self):
    	return self.title

class PageAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'body')

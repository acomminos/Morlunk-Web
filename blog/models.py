from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.
class BlogPost(models.Model):
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=50)
	body = models.TextField()
	author = models.ForeignKey(User)
	post_date = models.DateField()
	tags = models.ManyToManyField('BlogTag')

	def __unicode__(self):
		return self.title;

class BlogPostAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'description', 'author', 'post_date')

class BlogTag(models.Model):
	name = models.CharField(max_length=25)

	def __unicode__(self):
		return self.name
from blog.models import *
from django.contrib import admin

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogTag)
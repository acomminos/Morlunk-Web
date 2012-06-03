from blog.models import BlogPost
from django.template import RequestContext, Template
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

def blog(request):
	posts = BlogPost.objects.order_by('-post_date') # Sort by date, descending.
	return render_to_response('blog.html',
								{ 'posts': posts },
								RequestContext(request))

def blog_post(request, post_id):
	post = BlogPost.objects.get(id=post_id)
	return render_to_response('blog_post.html',
								{ 'post': post },
								RequestContext(request))
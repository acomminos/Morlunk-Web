from blog.models import BlogPost
from django.template import RequestContext, Template
from django.template.loader import get_template
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.utils import simplejson
from django.forms.models import model_to_dict

def blog(request, format="html"):
	posts = BlogPost.objects.order_by('-post_date') # Sort by date, descending.
	if format == "html":
		return render_to_response('blog.html',
								{ 'posts': posts },
								RequestContext(request))
	elif format == "json":
		# JSONify everything
		post_list = []
		try:
			for post in posts:
				# TODO switch to model_to_dict later.
				post_list.append({"title": post.title, "description": post.description, "body": post.body})
			result = 'success'
		except:
			result = 'error'
		return HttpResponse(simplejson.dumps({"posts" : post_list, "result" : result }), mimetype="application/json")

def blog_post(request, post_id):
	post = BlogPost.objects.get(id=post_id)
	return render_to_response('blog_post.html',
								{ 'post': post },
								RequestContext(request))
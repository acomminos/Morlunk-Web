from pages.models import Page
from django.template import RequestContext, Template
from django.shortcuts import render_to_response, redirect
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.utils import simplejson

# Loads 'home' if there is no page_id passed.
def get_page(request, page_id='home', format='html'):
    page = Page.objects.get(identifier=page_id)
    
    if format == 'html':
        # TODO: Dynamic captions for fun!
        return HttpResponse(render_to_response('page.html',
            {"page": page, "caption": "newly redesigned for great justice"},
            RequestContext(request)))
    elif format == 'json':
        return HttpResponse(simplejson.dumps({"result": "success", "page": model_to_dict(page)}), mimetype="application/json")
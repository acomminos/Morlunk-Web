from pages.models import Page
from django.template import RequestContext, Template
from django.template.loader import get_template
from django.http import HttpResponse

# Loads 'home' if there is no page_id passed.
def get_page(request, page_id='home'):
    page = Page.objects.get(identifier=page_id)
    template = get_template('page.html')
    # TODO: Dynamic captions for fun!
    data = {"page": page, "caption": "newly redesigned for great justice"}
    context = RequestContext(request, data)
    return HttpResponse(template.render(context))

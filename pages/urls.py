from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pages.views',
        (r'^(?P<page_id>.*)/$', 'get_page'),
        )

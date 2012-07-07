from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('account.views',
        (r'^$', 'control_panel'),
        (r'^login/$', 'user_login'),
        (r'^login/json$', 'user_login', {'format': 'json'}),
        (r'^logout/$', 'user_logout'),
        (r'^register/$', 'user_register'),
        )

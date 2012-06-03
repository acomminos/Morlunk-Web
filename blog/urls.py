from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('blog.views',
		(r'^$', 'blog'),
        (r'^(?P<post_id>.*)/$', 'blog_post'),
        )

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('radio.views',
        (r'^$', 'show_radio'),
        (r'^start', 'start_playing'),
        (r'^stop', 'start_playing'),
        (r'^queue', 'queue_song'),
        )

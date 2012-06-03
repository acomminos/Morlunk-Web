from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('paoman.views',
        (r'^play/', 'play_game'),
        )

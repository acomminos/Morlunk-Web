from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^$', 'Morlunk.blog.views.blog'), # Homepage is blog

    url(r'^minecraft/', include('Morlunk.minecraft.urls')),
    url(r'^page/', include('Morlunk.pages.urls')),
    url(r'^blog/', include('Morlunk.blog.urls')),
    url(r'^account/', include('Morlunk.account.urls')),
    url(r'^paoman/', include('Morlunk.paoman.urls')),
    url(r'^radio/', include('Morlunk.radio.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

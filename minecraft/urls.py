from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('minecraft.views',
        (r'^link/', 'minecraft_link'),
        (r'^grief/', 'minecraft_grief'),
        (r'^rates/', 'minecraft_rates'),
        (r'^redeem/', 'minecraft_paoso_redeem'),
        (r'^stash/(?P<user_name>.*)/$', 'minecraft_stash'),
        
		(r'^update$', 'minecraft_update'),
        (r'^account$', 'minecraft_get'),
        (r'^give$', 'minecraft_give'),
        (r'^value$', 'minecraft_sell_value'),
        (r'^stash/update$', 'minecraft_stash_update'),
        )

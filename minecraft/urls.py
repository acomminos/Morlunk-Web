from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('minecraft.views',
        (r'^link/$', 'minecraft_link'),
        (r'^grief/$', 'minecraft_grief'),
        (r'^rates/$', 'minecraft_rates'),
        (r'^store/buy/$', 'minecraft_buy'),
        (r'^store/$', 'minecraft_store'),
        (r'^store/json$', 'minecraft_store', {'format': 'json'}),
        (r'^redeem/$', 'minecraft_paoso_redeem'),
        (r'^stash/(?P<user_name>.*)/$', 'minecraft_stash'),
        
        (r'^update$', 'minecraft_update'),
        (r'^account$', 'minecraft_get'),
        (r'^account/json$', 'minecraft_user_get'), #TODO rename this
        (r'^give$', 'minecraft_give'),
        (r'^value$', 'minecraft_sell_value'),
        (r'^stash/update$', 'minecraft_stash_update'),
        (r'^stash/get$', 'minecraft_stash_get'),
        )

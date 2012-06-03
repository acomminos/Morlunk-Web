from minecraft.models import *
from django.contrib import admin

admin.site.register(MinecraftServer, MinecraftServerAdmin)
admin.site.register(DonatorLevel, DonatorLevelAdmin)
admin.site.register(MinecraftAccount, MinecraftAccountAdmin)
admin.site.register(GriefReport, GriefReportAdmin)
admin.site.register(MinecraftItem, MinecraftItemAdmin)
admin.site.register(PaosoCoupon, PaosoCouponAdmin)
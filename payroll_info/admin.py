from django.contrib import admin
from .models import *

# password myNameIsOzymandias
# Register your models here.
admin.site.register(InterbankUSDRate)
admin.site.register(NEC)
admin.site.register(Rates)
admin.site.register(Grades)

admin.sites.site.site_url = "Adaski.co.zw"
admin.sites.site.name = "Adaski"
admin.sites.site.site_title = "Adaski"
admin.sites.site.site_header = "Adaski"
admin.site.index_title = 'Database Admin'

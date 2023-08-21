from django.contrib import admin
from .models import *

# password myNameIsOzymandias
# Register your models here.
admin.site.register(InterbankUSDRate)
admin.site.register(NEC)
admin.site.register(Rates)
admin.site.register(Grades)

admin.site.site_header = 'Softrite API'
admin.site.site_title = 'Softrite API'
admin.site.index_title = 'Database Admin'

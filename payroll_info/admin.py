from django.contrib import admin
from .models import *

# password myNameIsOzymandias
# Register your models here.
admin.site.register(InterbankUSDRate)
admin.site.register(NEC)
admin.site.register(Rates)
admin.site.register(Grades)

admin.site.site_header = 'Payroll Info'
admin.site.site_title = 'Payroll Info'
admin.site.index_title = 'Admin'

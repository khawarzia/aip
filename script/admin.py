from django.contrib import admin
from .models import inputdata,currentdebt,regularexpenseddata,regularincomedata,lumpsumexpense,lumpsumincome

admin.site.register(inputdata)
admin.site.register(currentdebt)
admin.site.register(regularexpenseddata)
admin.site.register(regularincomedata)
admin.site.register(lumpsumexpense)
admin.site.register(lumpsumincome)
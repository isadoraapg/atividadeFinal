from django.contrib import admin
from .models import Corretor, Imovel, FotoImovel, Cliente

class FotoImovelInline(admin.TabularInline):
    model = FotoImovel
    extra = 5 
    max_num = 5

class ImovelAdmin(admin.ModelAdmin):
    inlines = [FotoImovelInline]

admin.site.register(Corretor)
admin.site.register(Imovel, ImovelAdmin)
admin.site.register(Cliente)

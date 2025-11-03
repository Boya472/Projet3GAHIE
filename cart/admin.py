from django.contrib import admin
from .models import Panier, ItemPanier

class ItemPanierInline(admin.TabularInline):
    model = ItemPanier
    extra = 0
    readonly_fields = ['date_ajout']

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'nombre_items', 'total', 'date_creation']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['date_creation', 'date_modification']
    inlines = [ItemPanierInline]
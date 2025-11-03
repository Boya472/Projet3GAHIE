from django.contrib import admin
from .models import Categorie, Etiquette, Produit, ImageProduit

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'ordre', 'nombre_produits']
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ['nom']
    ordering = ['ordre', 'nom']

@admin.register(Etiquette)
class EtiquetteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'couleur']
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ['nom']

class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 3
    fields = ['image', 'ordre']

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'vendeur', 'categorie', 'prix', 'stock', 'statut', 'visibilite', 'date_ajout', 'vues']
    list_filter = ['statut', 'visibilite', 'categorie', 'date_ajout']
    search_fields = ['nom', 'description', 'vendeur__nom_boutique']
    prepopulated_fields = {'slug': ('nom',)}
    filter_horizontal = ['etiquettes']
    inlines = [ImageProduitInline]
    actions = ['approuver_produits', 'refuser_produits', 'archiver_produits']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('vendeur', 'nom', 'slug', 'description', 'prix')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'etiquettes')
        }),
        ('Stock et tailles', {
            'fields': ('stock', 'tailles_disponibles')
        }),
        ('Images', {
            'fields': ('image_principale',)
        }),
        ('Statut', {
            'fields': ('statut', 'visibilite')
        }),
    )
    
    def approuver_produits(self, request, queryset):
        queryset.update(statut='publie')
        self.message_user(request, f"{queryset.count()} produit(s) approuvé(s)")
    approuver_produits.short_description = "Approuver les produits"
    
    def refuser_produits(self, request, queryset):
        queryset.update(statut='refuse')
        self.message_user(request, f"{queryset.count()} produit(s) refusé(s)")
    refuser_produits.short_description = "Refuser les produits"
    
    def archiver_produits(self, request, queryset):
        queryset.update(statut='archive', visibilite=False)
        self.message_user(request, f"{queryset.count()} produit(s) archivé(s)")
    archiver_produits.short_description = "Archiver les produits"
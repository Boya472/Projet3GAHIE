from django.contrib import admin
from .models import Commande, LigneCommande

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['sous_total']
    fields = ['produit', 'quantite', 'prix_unitaire', 'sous_total', 'taille']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero_commande', 'client', 'montant_total', 'statut', 'mode_paiement', 'paiement_valide', 'date_commande']
    list_filter = ['statut', 'mode_paiement', 'paiement_valide', 'date_commande']
    search_fields = ['numero_commande', 'client__user__username', 'client__user__email']
    readonly_fields = ['numero_commande', 'date_commande', 'date_modification']
    inlines = [LigneCommandeInline]
    actions = ['marquer_confirmee', 'marquer_expediee', 'marquer_livree']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('client', 'numero_commande')
        }),
        ('Montants', {
            'fields': ('montant_produits', 'frais_livraison', 'montant_total')
        }),
        ('Livraison', {
            'fields': ('adresse_livraison', 'ville', 'code_postal', 'telephone_livraison')
        }),
        ('Paiement', {
            'fields': ('mode_paiement', 'paiement_valide', 'reference_paiement')
        }),
        ('Statut', {
            'fields': ('statut', 'notes')
        }),
        ('Dates', {
            'fields': ('date_commande', 'date_modification')
        }),
    )
    
    def marquer_confirmee(self, request, queryset):
        queryset.update(statut='confirmee')
        self.message_user(request, f"{queryset.count()} commande(s) confirmée(s)")
    marquer_confirmee.short_description = "Marquer comme confirmée"
    
    def marquer_expediee(self, request, queryset):
        queryset.update(statut='expediee')
        self.message_user(request, f"{queryset.count()} commande(s) expédiée(s)")
    marquer_expediee.short_description = "Marquer comme expédiée"
    
    def marquer_livree(self, request, queryset):
        queryset.update(statut='livree')
        self.message_user(request, f"{queryset.count()} commande(s) livrée(s)")
    marquer_livree.short_description = "Marquer comme livrée"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Client, Vendeur, Administrateur

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'date_inscription']
    list_filter = ['role', 'is_active', 'is_staff', 'date_inscription']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telephone']
    ordering = ['-date_inscription']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('telephone', 'role', 'avatar')}),
    )

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'nombre_commandes', 'nombre_favoris']
    search_fields = ['user__username', 'user__email']
    
    def nombre_commandes(self, obj):
        return obj.commandes.count()
    nombre_commandes.short_description = 'Commandes'
    
    def nombre_favoris(self, obj):
        return obj.favoris.count()
    nombre_favoris.short_description = 'Favoris'

@admin.register(Vendeur)
class VendeurAdmin(admin.ModelAdmin):
    list_display = ['nom_boutique', 'user', 'statut_validation', 'commission_taux', 'total_produits', 'date_validation']
    list_filter = ['statut_validation', 'date_validation']
    search_fields = ['nom_boutique', 'user__username', 'user__email']
    actions = ['valider_vendeurs', 'suspendre_vendeurs']
    
    def valider_vendeurs(self, request, queryset):
        from django.utils import timezone
        queryset.update(statut_validation=True, date_validation=timezone.now())
        self.message_user(request, f"{queryset.count()} vendeur(s) validé(s)")
    valider_vendeurs.short_description = "Valider les vendeurs sélectionnés"
    
    def suspendre_vendeurs(self, request, queryset):
        queryset.update(statut_validation=False)
        self.message_user(request, f"{queryset.count()} vendeur(s) suspendu(s)")
    suspendre_vendeurs.short_description = "Suspendre les vendeurs sélectionnés"

@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ['user', 'user__date_joined']
    search_fields = ['user__username', 'user__email']
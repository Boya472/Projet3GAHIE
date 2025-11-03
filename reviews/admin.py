from django.contrib import admin
from .models import Avis, ReponseAvis

class ReponseAvisInline(admin.StackedInline):
    model = ReponseAvis
    extra = 0
    readonly_fields = ['date_reponse']

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['client', 'produit', 'note', 'statut', 'date_publication']
    list_filter = ['statut', 'note', 'date_publication']
    search_fields = ['client__user__username', 'produit__nom', 'commentaire']
    readonly_fields = ['date_publication', 'date_modification']
    inlines = [ReponseAvisInline]
    actions = ['approuver_avis', 'refuser_avis']
    
    def approuver_avis(self, request, queryset):
        queryset.update(statut='approuve')
        self.message_user(request, f"{queryset.count()} avis approuvé(s)")
    approuver_avis.short_description = "Approuver les avis"
    
    def refuser_avis(self, request, queryset):
        queryset.update(statut='refuse')
        self.message_user(request, f"{queryset.count()} avis refusé(s)")
    refuser_avis.short_description = "Refuser les avis"
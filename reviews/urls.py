from django.urls import path
from . import views

urlpatterns = [
    path('laisser/<int:produit_id>/', views.laisser_avis, name='laisser_avis'),
    path('modifier/<int:avis_id>/', views.modifier_avis, name='modifier_avis'),
    path('supprimer/<int:avis_id>/', views.supprimer_avis, name='supprimer_avis'),
    path('repondre/<int:avis_id>/', views.repondre_avis, name='repondre_avis'),
    path('mes-avis/', views.mes_avis, name='mes_avis'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.voir_panier, name='voir_panier'),
    path('ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('modifier/<int:item_id>/', views.modifier_quantite_panier, name='modifier_quantite_panier'),
    path('supprimer/<int:item_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('vider/', views.vider_panier, name='vider_panier'),
    path('api/nombre-items/', views.nombre_items_panier, name='nombre_items_panier'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('passer-commande/', views.passer_commande, name='passer_commande'),
    path('paiement/<int:commande_id>/', views.traiter_paiement, name='traiter_paiement'),
    path('confirmation/<int:commande_id>/', views.confirmation_commande, name='confirmation_commande'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
    path('annuler/<int:commande_id>/', views.annuler_commande, name='annuler_commande'),
]
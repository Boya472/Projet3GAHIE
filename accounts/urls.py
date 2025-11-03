
from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('inscription/client/', views.inscription_client, name='inscription_client'),
    path('inscription/vendeur/', views.inscription_vendeur, name='inscription_vendeur'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Profil
    path('profil/', views.profil, name='profil'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    
    # Dashboard vendeur

    path('dashboard/', views.dashboard_vendeur, name='dashboard_vendeur'),
    
    # Gestion des produits
    path('vendeur/produits/', views.liste_produits_vendeur, name='liste_produits_vendeur'),
    path('vendeur/produits/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('vendeur/produits/<int:produit_id>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('vendeur/produits/<int:produit_id>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    path('vendeur/produits/<int:produit_id>/toggle/', views.activer_desactiver_produit, name='activer_desactiver_produit'),
    path('vendeur/images/<int:image_id>/supprimer/', views.supprimer_image_produit, name='supprimer_image_produit'),
    
    # Commandes et statistiques
    path('vendeur/commandes/', views.commandes_vendeur, name='commandes_vendeur'),
    path('vendeur/statistiques/', views.statistiques_vendeur, name='statistiques_vendeur'),
]
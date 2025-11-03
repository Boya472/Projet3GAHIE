from django.urls import path
from . import views

urlpatterns = [
    path('', views.CatalogueProduits.as_view(), name='catalogue'),
    path('recherche/', views.recherche, name='recherche'),
    path('categorie/<slug:slug>/', views.categorie_detail, name='categorie_detail'),
    path('<slug:slug>/', views.DetailProduit.as_view(), name='detail_produit'),
    
]
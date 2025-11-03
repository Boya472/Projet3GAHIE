from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg
from django.contrib import messages
from .models import Produit, Categorie, Etiquette
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    """
    Page d'accueil - Affiche les produits vedettes
    """
    produits_recents = Produit.objects.filter(
        statut='publie', 
        visibilite=True
    ).order_by('-date_ajout')[:8]
    
    produits_populaires = Produit.objects.filter(
        statut='publie', 
        visibilite=True
    ).order_by('-vues')[:8]
    
    categories = Categorie.objects.all()[:6]
    
    context = {
        'produits_recents': produits_recents,
        'produits_populaires': produits_populaires,
        'categories': categories,
    }
    return render(request, 'home.html', context)


class CatalogueProduits(ListView):
    """
    Page catalogue - Liste tous les produits avec filtres
    """
    model = Produit
    template_name = 'catalogue.html'
    context_object_name = 'produits'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Produit.objects.filter(statut='publie', visibilite=True)
        
        # Recherche par mot-clé
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(vendeur__nom_boutique__icontains=search_query)
            )
        
        # Filtre par catégorie
        categorie_slug = self.request.GET.get('categorie')
        if categorie_slug:
            queryset = queryset.filter(categorie__slug=categorie_slug)
        
        # Filtre par étiquette
        etiquette_slug = self.request.GET.get('etiquette')
        if etiquette_slug:
            queryset = queryset.filter(etiquettes__slug=etiquette_slug)
        
        # Filtre par prix
        prix_min = self.request.GET.get('prix_min')
        prix_max = self.request.GET.get('prix_max')
        if prix_min:
            queryset = queryset.filter(prix__gte=prix_min)
        if prix_max:
            queryset = queryset.filter(prix__lte=prix_max)
        
        # Tri
        sort_by = self.request.GET.get('sort', '-date_ajout')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        context['etiquettes'] = Etiquette.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_categorie'] = self.request.GET.get('categorie', '')
        return context


class DetailProduit(DetailView):
    """
    Page détail d'un produit
    """
    model = Produit
    template_name = 'detail.html'
    context_object_name = 'produit'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Produit.objects.filter(statut='publie', visibilite=True)
    
    def get_object(self):
        obj = super().get_object()
        # Incrémenter le nombre de vues
        obj.vues += 1
        obj.save(update_fields=['vues'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produit = self.object
        
        # Images supplémentaires
        context['images_supplementaires'] = produit.images.all()
        
        # Avis du produit
        context['avis'] = produit.avis.filter(statut='approuve').order_by('-date_publication')[:5]
        context['note_moyenne'] = produit.note_moyenne()
        context['nombre_avis'] = produit.nombre_avis()
        
        # Produits similaires
        context['produits_similaires'] = Produit.objects.filter(
            categorie=produit.categorie,
            statut='publie',
            visibilite=True
        ).exclude(id=produit.id)[:4]
        
        return context


def categorie_detail(request, slug):
    """
    Afficher les produits d'une catégorie
    """
    categorie = get_object_or_404(Categorie, slug=slug)
    produits = Produit.objects.filter(
        categorie=categorie,
        statut='publie',
        visibilite=True
    ).order_by('-date_ajout')
    
    context = {
        'categorie': categorie,
        'produits': produits,
    }
    return render(request, 'categorie.html', context)


def recherche(request):
    """
    Page de résultats de recherche
    """
    query = request.GET.get('q', '')
    produits = []
    
    if query:
        produits = Produit.objects.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query) |
            Q(categorie__nom__icontains=query) |
            Q(etiquettes__nom__icontains=query) |
            Q(vendeur__nom_boutique__icontains=query),
            statut='publie',
            visibilite=True
        ).distinct()
    
    context = {
        'query': query,
        'produits': produits,
        'count': produits.count() if produits else 0,
    }
    return render(request, 'recherche.html', context)



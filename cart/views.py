from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Panier, ItemPanier
from products.models import Produit

def get_or_create_panier(request):
    """
    Récupérer ou créer un panier pour l'utilisateur
    """
    if request.user.is_authenticated:
        panier, created = Panier.objects.get_or_create(user=request.user)
    else:
        # Panier basé sur la session pour les visiteurs
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        panier, created = Panier.objects.get_or_create(session_key=session_key)
    
    return panier


def voir_panier(request):
    """
    Afficher le contenu du panier
    """
    panier = get_or_create_panier(request)
    items = panier.items.all()
    
    context = {
        'panier': panier,
        'items': items,
        'total': panier.total(),
        'nombre_items': panier.nombre_items(),
    }
    return render(request, 'panier.html', context)


def ajouter_au_panier(request, produit_id):
    """
    Ajouter un produit au panier
    """
    produit = get_object_or_404(Produit, id=produit_id, statut='publie', visibilite=True)
    panier = get_or_create_panier(request)
    
    quantite = int(request.POST.get('quantite', 1))
    taille = request.POST.get('taille', '')
    
    # Vérifier le stock
    if quantite > produit.stock:
        messages.error(request, "Stock insuffisant pour ce produit.")
        return redirect('detail_produit', slug=produit.slug)
    
    # Ajouter ou mettre à jour l'item
    item, created = ItemPanier.objects.get_or_create(
        panier=panier,
        produit=produit,
        taille=taille,
        defaults={'quantite': quantite}
    )
    
    if not created:
        # Si l'item existe déjà, augmenter la quantité
        nouvelle_quantite = item.quantite + quantite
        if nouvelle_quantite > produit.stock:
            messages.error(request, "Stock insuffisant pour cette quantité.")
            return redirect('detail_produit', slug=produit.slug)
        item.quantite = nouvelle_quantite
        item.save()
        messages.success(request, f"Quantité mise à jour dans le panier.")
    else:
        messages.success(request, f"{produit.nom} a été ajouté au panier.")
    
    return redirect('voir_panier')


def modifier_quantite_panier(request, item_id):
    """
    Modifier la quantité d'un produit dans le panier
    """
    panier = get_or_create_panier(request)
    item = get_object_or_404(ItemPanier, id=item_id, panier=panier)
    
    action = request.POST.get('action')
    
    if action == 'increase':
        if item.quantite < item.produit.stock:
            item.quantite += 1
            item.save()
            messages.success(request, "Quantité augmentée.")
        else:
            messages.error(request, "Stock insuffisant.")
    
    elif action == 'decrease':
        if item.quantite > 1:
            item.quantite -= 1
            item.save()
            messages.success(request, "Quantité diminuée.")
        else:
            messages.info(request, "La quantité minimale est 1.")
    
    elif action == 'set':
        quantite = int(request.POST.get('quantite', 1))
        if quantite > 0 and quantite <= item.produit.stock:
            item.quantite = quantite
            item.save()
            messages.success(request, "Quantité mise à jour.")
        else:
            messages.error(request, "Quantité invalide ou stock insuffisant.")
    
    return redirect('voir_panier')


def supprimer_du_panier(request, item_id):
    """
    Supprimer un produit du panier
    """
    panier = get_or_create_panier(request)
    item = get_object_or_404(ItemPanier, id=item_id, panier=panier)
    
    produit_nom = item.produit.nom
    item.delete()
    
    messages.success(request, f"{produit_nom} a été retiré du panier.")
    return redirect('voir_panier')


def vider_panier(request):
    """
    Vider complètement le panier
    """
    panier = get_or_create_panier(request)
    panier.vider()
    
    messages.success(request, "Votre panier a été vidé.")
    return redirect('voir_panier')


def nombre_items_panier(request):
    """
    API pour récupérer le nombre d'items dans le panier (AJAX)
    """
    panier = get_or_create_panier(request)
    return JsonResponse({
        'nombre_items': panier.nombre_items(),
        'total': float(panier.total())
    })
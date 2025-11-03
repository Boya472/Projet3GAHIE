from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Commande, LigneCommande
from cart.views import get_or_create_panier

@login_required
def checkout(request):
    """
    Page de paiement / finalisation de commande
    """
    # Vérifier que l'utilisateur est un client
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Vous devez être un client pour passer commande.")
        return redirect('home')
    
    panier = get_or_create_panier(request)
    items = panier.items.all()
    
    if not items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('voir_panier')
    
    # Calculer les frais de livraison (à personnaliser selon vos besoins)
    frais_livraison = 2000  # Exemple : 2000 FCFA
    total = panier.total() + frais_livraison
    
    context = {
        'items': items,
        'sous_total': panier.total(),
        'frais_livraison': frais_livraison,
        'total': total,
    }
    
    return render(request, 'checkout.html', context)


@login_required
def passer_commande(request):
    """
    Créer une nouvelle commande
    """
    if request.method != 'POST':
        return redirect('checkout')
    
    # Vérifier que l'utilisateur est un client
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Vous devez être un client pour passer commande.")
        return redirect('home')
    
    client = request.user.client_profile
    panier = get_or_create_panier(request)
    items = panier.items.all()
    
    if not items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect('voir_panier')
    
    # Récupérer les données du formulaire
    adresse_livraison = request.POST.get('adresse_livraison')
    ville = request.POST.get('ville')
    code_postal = request.POST.get('code_postal', '')
    telephone_livraison = request.POST.get('telephone_livraison')
    mode_paiement = request.POST.get('mode_paiement')
    
    # Validation
    if not all([adresse_livraison, ville, telephone_livraison, mode_paiement]):
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return redirect('checkout')
    
    # Calculer les montants
    frais_livraison = 2000  # À personnaliser
    montant_produits = panier.total()
    montant_total = montant_produits + frais_livraison
    
    # Créer la commande
    commande = Commande.objects.create(
        client=client,
        adresse_livraison=adresse_livraison,
        ville=ville,
        code_postal=code_postal,
        telephone_livraison=telephone_livraison,
        mode_paiement=mode_paiement,
        montant_produits=montant_produits,
        frais_livraison=frais_livraison,
        montant_total=montant_total,
        statut='en_attente'
    )
    
    # Créer les lignes de commande
    for item in items:
        LigneCommande.objects.create(
            commande=commande,
            produit=item.produit,
            quantite=item.quantite,
            prix_unitaire=item.produit.prix,
            sous_total=item.sous_total(),
            taille=item.taille
        )
        
        # Réduire le stock du produit
        produit = item.produit
        produit.stock -= item.quantite
        produit.save()
    
    # Vider le panier
    panier.vider()
    
    # Si paiement à la livraison, marquer comme confirmée
    if mode_paiement == 'a_la_livraison':
        commande.statut = 'confirmee'
        commande.save()
    
    messages.success(request, f"Votre commande {commande.numero_commande} a été créée avec succès !")
    
    # Rediriger vers la page de paiement ou confirmation
    if mode_paiement in ['mobile_money', 'wave', 'carte_bancaire']:
        return redirect('traiter_paiement', commande_id=commande.id)
    else:
        return redirect('confirmation_commande', commande_id=commande.id)


@login_required
def traiter_paiement(request, commande_id):
    """
    Page de traitement du paiement
    """
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client_profile)
    
    if request.method == 'POST':
        # Ici, vous intégrerez l'API de paiement (CinetPay, Fedapay, etc.)
        # Pour l'instant, simulation de paiement
        reference_paiement = request.POST.get('reference_paiement', 'SIMULATED')
        
        commande.paiement_valide = True
        commande.reference_paiement = reference_paiement
        commande.statut = 'confirmee'
        commande.save()
        
        messages.success(request, "Votre paiement a été validé avec succès !")
        return redirect('confirmation_commande', commande_id=commande.id)
    
    context = {
        'commande': commande,
    }
    return render(request, 'paiement.html', context)


@login_required
def confirmation_commande(request, commande_id):
    """
    Page de confirmation de commande
    """
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client_profile)
    
    context = {
        'commande': commande,
    }
    return render(request, 'confirmation.html', context)


@login_required
def mes_commandes(request):
    """
    Liste des commandes du client
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    commandes = request.user.client_profile.commandes.all().order_by('-date_commande')
    
    context = {
        'commandes': commandes,
    }
    return render(request, 'mes_commande.html', context)


@login_required
def detail_commande(request, commande_id):
    """
    Détail d'une commande
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client_profile)
    
    context = {
        'commande': commande,
        'lignes': commande.lignes.all(),
    }
    return render(request, 'detail_commande.html', context)


@login_required
def annuler_commande(request, commande_id):
    """
    Annuler une commande (si elle n'est pas encore expédiée)
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    commande = get_object_or_404(Commande, id=commande_id, client=request.user.client_profile)
    
    if commande.statut in ['en_attente', 'confirmee']:
        # Remettre les produits en stock
        for ligne in commande.lignes.all():
            produit = ligne.produit
            produit.stock += ligne.quantite
            produit.save()
        
        commande.statut = 'annulee'
        commande.save()
        messages.success(request, "Votre commande a été annulée.")
    else:
        messages.error(request, "Cette commande ne peut plus être annulée.")
    
    return redirect('detail_commande', commande_id=commande.id)
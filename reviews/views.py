from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Avis, ReponseAvis
from products.models import Produit

@login_required
def laisser_avis(request, produit_id):
    """
    Laisser un avis sur un produit
    """
    # Vérifier que l'utilisateur est un client
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Seuls les clients peuvent laisser des avis.")
        return redirect('home')
    
    produit = get_object_or_404(Produit, id=produit_id)
    client = request.user.client_profile
    
    # Vérifier si le client a déjà laissé un avis
    avis_existant = Avis.objects.filter(client=client, produit=produit).first()
    
    if request.method == 'POST':
        note = int(request.POST.get('note'))
        commentaire = request.POST.get('commentaire')
        
        # Validation
        if not (1 <= note <= 5):
            messages.error(request, "La note doit être entre 1 et 5.")
            return redirect('detail_produit', slug=produit.slug)
        
        if not commentaire:
            messages.error(request, "Le commentaire est obligatoire.")
            return redirect('detail_produit', slug=produit.slug)
        
        if avis_existant:
            # Modifier l'avis existant
            avis_existant.note = note
            avis_existant.commentaire = commentaire
            avis_existant.statut = 'en_attente'  # Remettre en modération
            avis_existant.save()
            messages.success(request, "Votre avis a été modifié et sera modéré à nouveau.")
        else:
            # Créer un nouvel avis
            Avis.objects.create(
                client=client,
                produit=produit,
                note=note,
                commentaire=commentaire,
                statut='en_attente'
            )
            messages.success(request, "Votre avis a été soumis et sera publié après modération.")
        
        return redirect('detail_produit', slug=produit.slug)
    
    context = {
        'produit': produit,
        'avis_existant': avis_existant,
    }
    return render(request, 'laisser_avis.html', context)


@login_required
def modifier_avis(request, avis_id):
    """
    Modifier un avis existant
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    avis = get_object_or_404(Avis, id=avis_id, client=request.user.client_profile)
    
    if request.method == 'POST':
        note = int(request.POST.get('note'))
        commentaire = request.POST.get('commentaire')
        
        if 1 <= note <= 5 and commentaire:
            avis.note = note
            avis.commentaire = commentaire
            avis.statut = 'en_attente'  # Remettre en modération
            avis.save()
            messages.success(request, "Votre avis a été modifié.")
            return redirect('detail_produit', slug=avis.produit.slug)
        else:
            messages.error(request, "Données invalides.")
    
    context = {
        'avis': avis,
    }
    return render(request, 'modifier_avis.html', context)


@login_required
def supprimer_avis(request, avis_id):
    """
    Supprimer un avis
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    avis = get_object_or_404(Avis, id=avis_id, client=request.user.client_profile)
    produit_slug = avis.produit.slug
    
    avis.delete()
    messages.success(request, "Votre avis a été supprimé.")
    
    return redirect('detail_produit', slug=produit_slug)


@login_required
def repondre_avis(request, avis_id):
    """
    Répondre à un avis (vendeur uniquement)
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Seuls les vendeurs peuvent répondre aux avis.")
        return redirect('home')
    
    avis = get_object_or_404(Avis, id=avis_id)
    
    # Vérifier que le vendeur est bien le propriétaire du produit
    if avis.produit.vendeur != request.user.vendeur_profile:
        messages.error(request, "Vous ne pouvez répondre qu'aux avis de vos produits.")
        return redirect('home')
    
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        
        if not contenu:
            messages.error(request, "La réponse ne peut pas être vide.")
            return redirect('detail_produit', slug=avis.produit.slug)
        
        # Créer ou modifier la réponse
        reponse, created = ReponseAvis.objects.get_or_create(
            avis=avis,
            defaults={'contenu': contenu}
        )
        
        if not created:
            reponse.contenu = contenu
            reponse.save()
            messages.success(request, "Votre réponse a été modifiée.")
        else:
            messages.success(request, "Votre réponse a été publiée.")
        
        return redirect('detail_produit', slug=avis.produit.slug)
    
    context = {
        'avis': avis,
    }
    return render(request, 'repondre_avis.html', context)


@login_required
def mes_avis(request):
    """
    Liste des avis laissés par le client
    """
    if not hasattr(request.user, 'client_profile'):
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    avis = Avis.objects.filter(client=request.user.client_profile).order_by('-date_publication')
    
    context = {
        'avis': avis,
    }
    return render(request, 'mes_avis.html', context)
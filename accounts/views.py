from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User, Client, Vendeur
from django.contrib.auth.forms import AuthenticationForm
from products.models import Produit, Categorie, Etiquette, ImageProduit
from django.db import transaction

def inscription_client(request):
    """
    Inscription d'un nouveau client
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        
        # Validation
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription_client')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect('inscription_client')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('inscription_client')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            telephone=telephone,
            role='client'
        )
        
        messages.success(request, "Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.")
        return redirect('connexion')
    
    return render(request, 'inscription_client.html')


def inscription_vendeur(request):
    """
    Inscription d'un nouveau vendeur
    """
    if request.method == 'POST':
        # Informations utilisateur
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        telephone = request.POST.get('telephone')
        
        # Informations boutique
        nom_boutique = request.POST.get('nom_boutique')
        description_boutique = request.POST.get('description_boutique')
        coordonnees_paiement = request.POST.get('coordonnees_paiement')
        
        # Validation
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription_vendeur')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect('inscription_vendeur')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('inscription_vendeur')
        
        # Créer l'utilisateur vendeur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            telephone=telephone,
            role='vendeur'
        )
        
        # Mettre à jour les informations de la boutique
        vendeur = user.vendeur_profile
        vendeur.nom_boutique = nom_boutique
        vendeur.description_boutique = description_boutique
        vendeur.coordonnees_paiement = coordonnees_paiement
        vendeur.save()
        
        messages.success(request, "Votre compte vendeur a été créé ! Il sera activé après validation par l'administrateur.")
        return redirect('connexion')
    
    return render(request, 'inscription_vendeur.html')


def connexion(request):
    """
    Connexion d'un utilisateur
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")
            
            # Redirection selon le rôle
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            elif user.role == 'vendeur':
                return redirect('dashboard_vendeur')
            elif user.role == 'admin':
                return redirect('admin:index')
            else:
                return redirect('home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'connexion.html')


@login_required
def deconnexion(request):
    """
    Déconnexion d'un utilisateur
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')


@login_required
def profil(request):
    """
    Page profil utilisateur
    """
    user = request.user
    
    if user.role == 'client':
        commandes = user.client_profile.commandes.all().order_by('-date_commande')[:5]
        context = {
            'commandes': commandes,
        }
    elif user.role == 'vendeur':
        vendeur = user.vendeur_profile
        produits = vendeur.produits.all()[:5]
        context = {
            'vendeur': vendeur,
            'produits': produits,
        }
    else:
        context = {}
    
    return render(request, 'profil.html', context)


# Remplacer la fonction modifier_profil existante dans accounts/views.py par celle-ci :

@login_required
def modifier_profil(request):
    """
    Modifier les informations du profil
    """
    user = request.user
    
    if request.method == 'POST':
        # Informations de base
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email')
        user.telephone = request.POST.get('telephone', '')
        
        # Avatar
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        # Si vendeur, mettre à jour les infos boutique
        if user.role == 'vendeur':
            vendeur = user.vendeur_profile
            vendeur.nom_boutique = request.POST.get('nom_boutique', vendeur.nom_boutique)
            vendeur.description_boutique = request.POST.get('description_boutique', '')
            
            if 'logo_boutique' in request.FILES:
                vendeur.logo_boutique = request.FILES['logo_boutique']
            
            vendeur.save()
        
        # Changement de mot de passe (optionnel)
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        
        if old_password and new_password:
            if user.check_password(old_password):
                if new_password == new_password2:
                    user.set_password(new_password)
                    messages.success(request, "Votre mot de passe a été modifié. Veuillez vous reconnecter.")
                    user.save()
                    logout(request)
                    return redirect('connexion')
                else:
                    messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
                    return redirect('modifier_profil')
            else:
                messages.error(request, "Le mot de passe actuel est incorrect.")
                return redirect('modifier_profil')
        
        user.save()
        messages.success(request, "Vos informations ont été mises à jour.")
        return redirect('profil')
    
    return render(request, 'modifier_profil.html')


@login_required
def dashboard_vendeur(request):
    """
    Dashboard du vendeur
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    
    # Vérifier si le compte est validé
    if not vendeur.statut_validation:
        messages.warning(request, "Votre compte est en attente de validation par l'administrateur.")
    
    # Statistiques
    total_produits = vendeur.produits.count()
    produits_publies = vendeur.produits.filter(statut='publie').count()
    produits_en_attente = vendeur.produits.filter(statut='en_attente').count()
    
    # Derniers produits
    derniers_produits = vendeur.produits.all().order_by('-date_ajout')[:5]
    
    context = {
        'vendeur': vendeur,
        'total_produits': total_produits,
        'produits_publies': produits_publies,
        'produits_en_attente': produits_en_attente,
        'derniers_produits': derniers_produits,
    }
    
    return render(request, 'dashboard_vendeur.html', context)

@login_required
def liste_produits_vendeur(request):
    """
    Liste de tous les produits du vendeur
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    produits = vendeur.produits.all().order_by('-date_ajout')
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        produits = produits.filter(statut=statut)
    
    context = {
        'produits': produits,
        'vendeur': vendeur,
    }
    return render(request, 'liste_produits.html', context)


@login_required
def ajouter_produit(request):
    """
    Ajouter un nouveau produit
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    
    # Vérifier si le compte est validé
    if not vendeur.statut_validation:
        messages.error(request, "Votre compte doit être validé avant de pouvoir ajouter des produits.")
        return redirect('dashboard_vendeur')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        prix = request.POST.get('prix')
        stock = request.POST.get('stock')
        categorie_id = request.POST.get('categorie')
        etiquettes_ids = request.POST.getlist('etiquettes')
        tailles = request.POST.getlist('tailles')
        image_principale = request.FILES.get('image_principale')
        
        # Validation
        if not all([nom, description, prix, stock, categorie_id, image_principale]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('ajouter_produit')
        
        try:
            with transaction.atomic():
                # Créer le produit
                produit = Produit.objects.create(
                    vendeur=vendeur,
                    nom=nom,
                    description=description,
                    prix=prix,
                    stock=stock,
                    categorie_id=categorie_id,
                    image_principale=image_principale,
                    tailles_disponibles=tailles,
                    statut='en_attente',
                    visibilite=True
                )
                
                # Ajouter les étiquettes
                if etiquettes_ids:
                    produit.etiquettes.set(etiquettes_ids)
                
                # Ajouter les images supplémentaires
                images_supplementaires = request.FILES.getlist('images_supplementaires')
                for i, image in enumerate(images_supplementaires):
                    ImageProduit.objects.create(
                        produit=produit,
                        image=image,
                        ordre=i
                    )
                
                messages.success(request, f"Le produit '{nom}' a été ajouté avec succès et est en attente de modération.")
                return redirect('liste_produits_vendeur')
                
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout du produit : {str(e)}")
            return redirect('ajouter_produit')
    
    # GET request
    categories = Categorie.objects.all()
    etiquettes = Etiquette.objects.all()
    
    context = {
        'categories': categories,
        'etiquettes': etiquettes,
        'tailles_choices': ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
    }
    return render(request, 'ajouter_produit.html', context)


@login_required
def modifier_produit(request, produit_id):
    """
    Modifier un produit existant
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    produit = get_object_or_404(Produit, id=produit_id, vendeur=vendeur)
    
    if request.method == 'POST':
        # Récupérer les données
        produit.nom = request.POST.get('nom')
        produit.description = request.POST.get('description')
        produit.prix = request.POST.get('prix')
        produit.stock = request.POST.get('stock')
        produit.categorie_id = request.POST.get('categorie')
        tailles = request.POST.getlist('tailles')
        produit.tailles_disponibles = tailles
        
        # Image principale (optionnel)
        if 'image_principale' in request.FILES:
            produit.image_principale = request.FILES['image_principale']
        
        # Étiquettes
        etiquettes_ids = request.POST.getlist('etiquettes')
        if etiquettes_ids:
            produit.etiquettes.set(etiquettes_ids)
        
        try:
            produit.save()
            
            # Ajouter de nouvelles images supplémentaires
            images_supplementaires = request.FILES.getlist('images_supplementaires')
            if images_supplementaires:
                # Récupérer le dernier ordre
                dernier_ordre = produit.images.count()
                for i, image in enumerate(images_supplementaires):
                    ImageProduit.objects.create(
                        produit=produit,
                        image=image,
                        ordre=dernier_ordre + i
                    )
            
            messages.success(request, f"Le produit '{produit.nom}' a été modifié avec succès.")
            return redirect('liste_produits_vendeur')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    # GET request
    categories = Categorie.objects.all()
    etiquettes = Etiquette.objects.all()
    images_supplementaires = produit.images.all()
    
    context = {
        'produit': produit,
        'categories': categories,
        'etiquettes': etiquettes,
        'images_supplementaires': images_supplementaires,
        'tailles_choices': ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
    }
    return render(request, 'modifier_produit.html', context)


@login_required
def supprimer_produit(request, produit_id):
    """
    Supprimer un produit
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    produit = get_object_or_404(Produit, id=produit_id, vendeur=vendeur)
    
    if request.method == 'POST':
        nom_produit = produit.nom
        produit.delete()
        messages.success(request, f"Le produit '{nom_produit}' a été supprimé.")
        return redirect('liste_produits_vendeur')
    
    context = {
        'produit': produit,
    }
    return render(request, 'supprimer_produit.html', context)


@login_required
def supprimer_image_produit(request, image_id):
    """
    Supprimer une image supplémentaire d'un produit
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    image = get_object_or_404(ImageProduit, id=image_id)
    
    # Vérifier que le vendeur est bien le propriétaire du produit
    if image.produit.vendeur != request.user.vendeur_profile:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette image.")
        return redirect('dashboard_vendeur')
    
    produit_id = image.produit.id
    image.delete()
    messages.success(request, "Image supprimée avec succès.")
    
    return redirect('modifier_produit', produit_id=produit_id)


@login_required
def activer_desactiver_produit(request, produit_id):
    """
    Activer ou désactiver la visibilité d'un produit
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    produit = get_object_or_404(Produit, id=produit_id, vendeur=vendeur)
    
    # Toggle visibilité
    produit.visibilite = not produit.visibilite
    produit.save()
    
    statut = "activé" if produit.visibilite else "désactivé"
    messages.success(request, f"Le produit '{produit.nom}' a été {statut}.")
    
    return redirect('liste_produits_vendeur')


@login_required
def commandes_vendeur(request):
    """
    Liste des commandes contenant les produits du vendeur
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    
    # Récupérer toutes les lignes de commande des produits du vendeur
    from orders.models import LigneCommande
    lignes_commandes = LigneCommande.objects.filter(
        produit__vendeur=vendeur
    ).select_related('commande', 'produit').order_by('-commande__date_commande')
    
    # Regrouper par commande
    commandes_dict = {}
    for ligne in lignes_commandes:
        commande = ligne.commande
        if commande.id not in commandes_dict:
            commandes_dict[commande.id] = {
                'commande': commande,
                'lignes': []
            }
        commandes_dict[commande.id]['lignes'].append(ligne)
    
    context = {
        'commandes_dict': commandes_dict.values(),
    }
    return render(request, 'commandes.html', context)


@login_required
def statistiques_vendeur(request):
    """
    Statistiques du vendeur
    """
    if request.user.role != 'vendeur':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    vendeur = request.user.vendeur_profile
    from orders.models import LigneCommande
    from django.db.models import Sum, Count
    
    # Statistiques générales
    total_produits = vendeur.produits.count()
    produits_publies = vendeur.produits.filter(statut='publie').count()
    produits_en_attente = vendeur.produits.filter(statut='en_attente').count()
    
    # Statistiques de vente
    lignes = LigneCommande.objects.filter(produit__vendeur=vendeur)
    total_ventes = lignes.count()
    revenu_brut = lignes.aggregate(total=Sum('sous_total'))['total'] or 0
    commission_plateforme = revenu_brut * (vendeur.commission_taux / 100)
    revenu_net = revenu_brut - commission_plateforme
    
    # Produits les plus vendus
    produits_populaires = vendeur.produits.annotate(
        nb_ventes=Count('lignes_commande')
    ).order_by('-nb_ventes')[:5]
    
    # Produits les plus vus
    produits_vus = vendeur.produits.order_by('-vues')[:5]
    
    context = {
        'total_produits': total_produits,
        'produits_publies': produits_publies,
        'produits_en_attente': produits_en_attente,
        'total_ventes': total_ventes,
        'revenu_brut': revenu_brut,
        'commission_plateforme': commission_plateforme,
        'revenu_net': revenu_net,
        'produits_populaires': produits_populaires,
        'produits_vus': produits_vus,
    }
    return render(request, 'statistiques.html', context)

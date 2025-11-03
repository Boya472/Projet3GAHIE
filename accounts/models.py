from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Modèle utilisateur personnalisé (abstrait)
    Hérite de AbstractUser pour utiliser le système d'auth Django
    """
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('vendeur', 'Vendeur'),
        ('admin', 'Administrateur'),
    ]
    
    telephone = models.CharField(_('Téléphone'), max_length=20, blank=True)
    role = models.CharField(_('Rôle'), max_length=10, choices=ROLE_CHOICES, default='client')
    date_inscription = models.DateTimeField(_('Date d\'inscription'), auto_now_add=True)
    avatar = models.ImageField(_('Photo de profil'), upload_to='profiles/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Client(models.Model):
    """
    Modèle Client - Utilisateur qui achète
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    adresses = models.TextField(_('Adresses de livraison'), blank=True, help_text='Format JSON')
    favoris = models.ManyToManyField('products.Produit', blank=True, related_name='favoris_par')
    
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
    
    def __str__(self):
        return f"Client: {self.user.get_full_name() or self.user.username}"


class Vendeur(models.Model):
    """
    Modèle Vendeur - Utilisateur qui vend des produits
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendeur_profile')
    nom_boutique = models.CharField(_('Nom de la boutique'), max_length=200)
    description_boutique = models.TextField(_('Description'), blank=True)
    logo_boutique = models.ImageField(_('Logo'), upload_to='boutiques/logos/', blank=True, null=True)
    coordonnees_paiement = models.TextField(_('Coordonnées de paiement'), help_text='Mobile Money, RIB, etc.')
    statut_validation = models.BooleanField(_('Compte validé'), default=False)
    date_validation = models.DateTimeField(_('Date de validation'), blank=True, null=True)
    commission_taux = models.DecimalField(_('Taux de commission'), max_digits=5, decimal_places=2, default=10.00, help_text='En pourcentage')
    
    class Meta:
        verbose_name = _('Vendeur')
        verbose_name_plural = _('Vendeurs')
    
    def __str__(self):
        return f"{self.nom_boutique} - {self.user.get_full_name()}"
    
    def total_produits(self):
        return self.produits.count()
    
    def total_ventes(self):
        from orders.models import LigneCommande
        return LigneCommande.objects.filter(produit__vendeur=self).count()


class Administrateur(models.Model):
    """
    Modèle Administrateur - Gestion complète du site
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    privileges = models.JSONField(_('Privilèges'), default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Administrateur')
        verbose_name_plural = _('Administrateurs')
    
    def __str__(self):
        return f"Admin: {self.user.get_full_name() or self.user.username}"


# Signals pour créer automatiquement les profils
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement le profil selon le rôle"""
    if created:
        if instance.role == 'client':
            Client.objects.create(user=instance)
        elif instance.role == 'vendeur':
            Vendeur.objects.create(user=instance, nom_boutique=f"Boutique {instance.username}")
        elif instance.role == 'admin':
            Administrateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil automatiquement"""
    if instance.role == 'client' and hasattr(instance, 'client_profile'):
        instance.client_profile.save()
    elif instance.role == 'vendeur' and hasattr(instance, 'vendeur_profile'):
        instance.vendeur_profile.save()
    elif instance.role == 'admin' and hasattr(instance, 'admin_profile'):
        instance.admin_profile.save()
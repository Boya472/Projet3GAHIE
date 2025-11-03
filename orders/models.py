from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import Client
from products.models import Produit
import uuid

class Commande(models.Model):
    """
    Modèle Commande
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    MODE_PAIEMENT_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('wave', 'Wave'),
        ('carte_bancaire', 'Carte Bancaire'),
        ('a_la_livraison', 'Paiement à la livraison'),
    ]
    
    # Identifiants
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes', verbose_name=_('Client'))
    numero_commande = models.CharField(_('Numéro de commande'), max_length=50, unique=True, blank=True)
    
    # Dates
    date_commande = models.DateTimeField(_('Date de commande'), auto_now_add=True)
    date_modification = models.DateTimeField(_('Dernière modification'), auto_now=True)
    
    # Montants
    montant_produits = models.DecimalField(_('Montant produits'), max_digits=10, decimal_places=2, default=0)
    frais_livraison = models.DecimalField(_('Frais de livraison'), max_digits=10, decimal_places=2, default=0)
    montant_total = models.DecimalField(_('Montant total'), max_digits=10, decimal_places=2, default=0)
    
    # Livraison
    adresse_livraison = models.TextField(_('Adresse de livraison'))
    ville = models.CharField(_('Ville'), max_length=100)
    code_postal = models.CharField(_('Code postal'), max_length=20, blank=True)
    telephone_livraison = models.CharField(_('Téléphone'), max_length=20)
    
    # Paiement
    mode_paiement = models.CharField(_('Mode de paiement'), max_length=20, choices=MODE_PAIEMENT_CHOICES)
    paiement_valide = models.BooleanField(_('Paiement validé'), default=False)
    reference_paiement = models.CharField(_('Référence paiement'), max_length=100, blank=True)
    
    # Statut
    statut = models.CharField(_('Statut'), max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes = models.TextField(_('Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Commande')
        verbose_name_plural = _('Commandes')
        ordering = ['-date_commande']
    
    def save(self, *args, **kwargs):
        if not self.numero_commande:
            self.numero_commande = f"CMD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_commande} - {self.client.user.get_full_name()}"
    
    def calculer_total(self):
        """Calculer le montant total de la commande"""
        self.montant_produits = sum(ligne.sous_total for ligne in self.lignes.all())
        self.montant_total = self.montant_produits + self.frais_livraison
        self.save()


class LigneCommande(models.Model):
    """
    Ligne de commande - Produits dans une commande
    """
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes', verbose_name=_('Commande'))
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_commande', verbose_name=_('Produit'))
    
    quantite = models.PositiveIntegerField(_('Quantité'), default=1)
    prix_unitaire = models.DecimalField(_('Prix unitaire'), max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(_('Sous-total'), max_digits=10, decimal_places=2)
    taille = models.CharField(_('Taille'), max_length=10, blank=True)
    
    class Meta:
        verbose_name = _('Ligne de commande')
        verbose_name_plural = _('Lignes de commande')
    
    def save(self, *args, **kwargs):
        self.sous_total = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
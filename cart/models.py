from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from products.models import Produit

class Panier(models.Model):
    """
    Panier d'achat
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='panier', verbose_name=_('Utilisateur'), null=True, blank=True)
    session_key = models.CharField(_('Clé de session'), max_length=40, blank=True, null=True, unique=True)
    date_creation = models.DateTimeField(_('Date de création'), auto_now_add=True)
    date_modification = models.DateTimeField(_('Dernière modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('Panier')
        verbose_name_plural = _('Paniers')
    
    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier session {self.session_key}"
    
    def total(self):
        """Calculer le total du panier"""
        return sum(item.sous_total() for item in self.items.all())
    
    def nombre_items(self):
        """Nombre total d'articles"""
        return sum(item.quantite for item in self.items.all())
    
    def vider(self):
        """Vider le panier"""
        self.items.all().delete()


class ItemPanier(models.Model):
    """
    Article dans le panier
    """
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='items', verbose_name=_('Panier'))
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name=_('Produit'))
    quantite = models.PositiveIntegerField(_('Quantité'), default=1)
    taille = models.CharField(_('Taille'), max_length=10, blank=True)
    date_ajout = models.DateTimeField(_('Date d\'ajout'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Article du panier')
        verbose_name_plural = _('Articles du panier')
        unique_together = ['panier', 'produit', 'taille']
    
    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
    
    def sous_total(self):
        """Calculer le sous-total"""
        return self.produit.prix * self.quantite
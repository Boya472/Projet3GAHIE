from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import Client
from products.models import Produit

class Avis(models.Model):
    """
    Avis/Commentaires sur les produits
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente de modération'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='avis', verbose_name=_('Client'))
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis', verbose_name=_('Produit'))
    
    note = models.IntegerField(_('Note'), validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(_('Commentaire'))
    
    date_publication = models.DateTimeField(_('Date de publication'), auto_now_add=True)
    date_modification = models.DateTimeField(_('Dernière modification'), auto_now=True)
    
    statut = models.CharField(_('Statut'), max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    class Meta:
        verbose_name = _('Avis')
        verbose_name_plural = _('Avis')
        ordering = ['-date_publication']
        unique_together = ['client', 'produit']  # Un client ne peut laisser qu'un avis par produit
    
    def __str__(self):
        return f"Avis de {self.client.user.username} sur {self.produit.nom} - {self.note}★"


class ReponseAvis(models.Model):
    """
    Réponse du vendeur à un avis
    """
    avis = models.OneToOneField(Avis, on_delete=models.CASCADE, related_name='reponse', verbose_name=_('Avis'))
    contenu = models.TextField(_('Réponse'))
    date_reponse = models.DateTimeField(_('Date de réponse'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Réponse à un avis')
        verbose_name_plural = _('Réponses aux avis')
    
    def __str__(self):
        return f"Réponse à l'avis #{self.avis.id}"
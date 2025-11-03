from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from accounts.models import Vendeur

class Categorie(models.Model):
    """
    Catégories de produits (Vêtements Homme, Femme, Enfant, Sacs, Chaussures)
    """
    nom = models.CharField(_('Nom'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True, null=True)
    ordre = models.IntegerField(_('Ordre d\'affichage'), default=0)
    
    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['ordre', 'nom']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    def nombre_produits(self):
        return self.produits.filter(visibilite=True).count()


class Etiquette(models.Model):
    """
    Tags/Étiquettes pour les produits (wax, dashiki, moderne, traditionnel, etc.)
    """
    nom = models.CharField(_('Nom'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    couleur = models.CharField(_('Couleur'), max_length=7, default='#007bff', help_text='Code hexadécimal')
    
    class Meta:
        verbose_name = _('Étiquette')
        verbose_name_plural = _('Étiquettes')
        ordering = ['nom']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom


class Produit(models.Model):
    """
    Modèle Produit - Produits vendus sur la plateforme
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente de modération'),
        ('publie', 'Publié'),
        ('refuse', 'Refusé'),
        ('archive', 'Archivé'),
    ]
    
    TAILLE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    ]
    
    # Informations de base
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, related_name='produits', verbose_name=_('Vendeur'))
    nom = models.CharField(_('Nom du produit'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    description = models.TextField(_('Description'))
    prix = models.DecimalField(_('Prix'), max_digits=10, decimal_places=2)
    
    # Catégorisation
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='produits', verbose_name=_('Catégorie'))
    etiquettes = models.ManyToManyField(Etiquette, blank=True, related_name='produits', verbose_name=_('Étiquettes'))
    
    # Stock et tailles
    stock = models.PositiveIntegerField(_('Stock disponible'), default=0)
    tailles_disponibles = models.JSONField(_('Tailles disponibles'), default=list, blank=True, help_text='Liste des tailles')
    
    # Images
    image_principale = models.ImageField(_('Image principale'), upload_to='produits/')
    
    # Statut et visibilité
    statut = models.CharField(_('Statut'), max_length=20, choices=STATUT_CHOICES, default='en_attente')
    visibilite = models.BooleanField(_('Visible sur le site'), default=True)
    
    # Dates
    date_ajout = models.DateTimeField(_('Date d\'ajout'), auto_now_add=True)
    date_modification = models.DateTimeField(_('Dernière modification'), auto_now=True)
    
    # Statistiques
    vues = models.PositiveIntegerField(_('Nombre de vues'), default=0)
    
    class Meta:
        verbose_name = _('Produit')
        verbose_name_plural = _('Produits')
        ordering = ['-date_ajout']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categorie', 'statut']),
            models.Index(fields=['-date_ajout']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            counter = 1
            while Produit.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nom} - {self.vendeur.nom_boutique}"
    
    def prix_avec_commission(self):
        """Prix incluant la commission plateforme"""
        commission = self.prix * (self.vendeur.commission_taux / 100)
        return self.prix + commission
    
    def est_en_stock(self):
        return self.stock > 0
    
    def note_moyenne(self):
        from reviews.models import Avis
        avis = Avis.objects.filter(produit=self, statut='approuve')
        if avis.exists():
            return round(avis.aggregate(models.Avg('note'))['note__avg'], 1)
        return 0
    
    def nombre_avis(self):
        from reviews.models import Avis
        return Avis.objects.filter(produit=self, statut='approuve').count()


class ImageProduit(models.Model):
    """
    Images supplémentaires pour un produit
    """
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='images', verbose_name=_('Produit'))
    image = models.ImageField(_('Image'), upload_to='produits/galerie/')
    ordre = models.PositiveIntegerField(_('Ordre'), default=0)
    date_ajout = models.DateTimeField(_('Date d\'ajout'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Image de produit')
        verbose_name_plural = _('Images de produit')
        ordering = ['ordre', 'date_ajout']
    
    def __str__(self):
        return f"Image {self.ordre} - {self.produit.nom}"
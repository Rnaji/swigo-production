# Importations nécessaires
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models import F
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import to_stock_units, price_per_stock_unit


# Choix pour les taux de TVA
TAUX_TVA_CHOICES = [
    (5.5, '5,5%'),
    (10, '10%'),
    (20, '20%')
]

# Définir GROUPE_CHOICES au niveau du module
GROUPE_CHOICES = [
    ('fruits', 'Fruits'),
    ('legumes', 'Légumes'),
    ('feculents', 'Féculents'),
    ('vpo', 'Viande, Poissons, Oeufs (VPO)'),
    ('laitiers', 'Lait et produits laitiers'),
    ('gras', 'Matières grasses ajoutées'),
    ('sucres', 'Produits sucrés ou sucrés et gras'),
    ('boissons', 'Boissons'),
    ('epicerie', 'Epicerie'),
    ('epices', 'Epices'),
    ('herbes', 'Herbes'),
    ('melanges', 'melanges'),

]

class Categorie(models.Model):
    SPECIALITES = [
        ('menu', 'Menu'),
        ('burger', 'Burger'),
        ('salade', 'Salade'),
        ('crousty', 'Crousty'),
        ('couscous/tajine', 'Couscous/Tajine'),
        ('poulet', 'Poulet'),
        ('sides', 'Sides'),
        ('boisson', 'Boisson'),
        ('dessert', 'Dessert'),
        ('traiteur', 'Traiteur'),

    ]

    nom = models.CharField(max_length=100, choices=SPECIALITES, unique=True)
    icone = models.CharField(max_length=100, blank=True, help_text="Classe CSS de l'icône (ex : flaticon-hamburger-1)")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage dans le menu")

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return dict(self.SPECIALITES).get(self.nom, self.nom)

# Modèle Client
class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero_telephone = models.CharField(max_length=15)
    adresse_facturation = models.TextField()
    email = models.EmailField()
    date_creation = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)

    # ✅ Nouveaux champs pour les consentements
    consent_sms = models.BooleanField(default=False)
    consent_email = models.BooleanField(default=False)
    consent_cookies = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# Modèle AdresseLivraison
class AdresseLivraison(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.CASCADE, related_name='adresses_livraison')
    adresse = models.TextField()  # Seulement la rue ici !
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    zone = models.IntegerField()
    localisation = models.CharField(max_length=5)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    DELAIS_ZONES = {
        0: 30,
        1: 35,
        2: 40,
        3: 50,
    }

    def __str__(self):
        return f"{self.adresse_complete} (Zone {self.zone})"

    @property
    def adresse_complete(self):
        return f"{self.adresse}, {self.code_postal} {self.ville}"

    @property
    def delai_livraison_estime(self):
        return self.DELAIS_ZONES.get(self.zone, 30)

class ClientBlacklist(models.Model):
    email = models.EmailField(blank=True, null=True)
    numero_telephone = models.CharField(max_length=15, blank=True, null=True)
    raison = models.TextField(blank=True, null=True)
    date_blocage = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email or self.numero_telephone

# Modèle VilleDesservie
class VilleDesservie(models.Model):
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    nombre_habitants = models.IntegerField()
    distance_gisors = models.FloatField()
    temps_gisors = models.IntegerField()
    zone = models.IntegerField()
    panier_minimal = models.FloatField()
    localisation = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.ville} ({self.code_postal})"

class JourFermeture(models.Model):
    date_debut = models.DateField()
    date_fin = models.DateField()
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        if self.date_debut == self.date_fin:
            return f"{self.date_debut} - {self.description}"
        return f"{self.date_debut} → {self.date_fin} - {self.description}"

    @staticmethod
    def est_ferme(date):
        return JourFermeture.objects.filter(date_debut__lte=date, date_fin__gte=date).exists()

    @staticmethod
    def toutes_les_dates_fermees():
        fermetures = JourFermeture.objects.all()
        dates = set()
        for fermeture in fermetures:
            d = fermeture.date_debut
            while d <= fermeture.date_fin:
                dates.add(d)
                d += timedelta(days=1)
        return sorted(dates)

# models.py

class HoraireDisponible(models.Model):
    JOURS_CHOIX = [
        ('LUN', 'Lundi'),
        ('MAR', 'Mardi'),
        ('MER', 'Mercredi'),
        ('JEU', 'Jeudi'),
        ('VEN', 'Vendredi'),
        ('SAM', 'Samedi'),
        ('DIM', 'Dimanche'),
    ]

    SERVICE_CHOIX = [
        ('MIDI', 'Midi'),
        ('SOIR', 'Soir'),
    ]

    jour = models.CharField(max_length=3, choices=JOURS_CHOIX)
    service = models.CharField(max_length=4, choices=SERVICE_CHOIX)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    intervalle = models.IntegerField(default=15)  # minutes

    # Champs supplémentaires pour la capacité
    capacite_max = models.PositiveIntegerField(default=10)
    nombre_commandes = models.PositiveIntegerField(default=0)

    def get_horaires(self):
        horaires = []
        current = datetime.combine(datetime.today(), self.heure_debut)
        end_time = datetime.combine(datetime.today(), self.heure_fin)
        interval = timedelta(minutes=self.intervalle)

        while current <= end_time:
            horaires.append(current.strftime("%H:%M"))
            current += interval

        return horaires

    def __str__(self):
        return f"{self.get_jour_display()} - {self.get_service_display()} - {self.heure_debut.strftime('%H:%M')} → {self.heure_fin.strftime('%H:%M')}"



# models.py
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

# Helpers à placer dans utils.py (déjà proposés) puis importés ici :
# from .utils import to_stock_units, price_per_stock_unit

class Ingredient(models.Model):
    """
    Ingrédient de base. Le stock est toujours conservé en ENTIER selon unite_stock :
      - 'g'  => stock en grammes (int)
      - 'l'  => stock en millilitres (int)
      - 'u'  => stock en unités (int)

    prix_unitaire_achat est exprimé dans l'unité de stock (€/g, €/ml, €/u).
    """

    nom = models.CharField(max_length=100)
    quantite_stock = models.PositiveIntegerField(default=0)  # g / ml / u selon unite_stock
    unite_stock = models.CharField(
        max_length=10,
        choices=[('g', 'grammes'), ('l', 'litres'), ('u', 'unités')],
        default='u'
    )

    # Prix exprimés à l'unité de STOCK (€/g, €/ml, €/u)
    prix_unitaire_achat = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Prix d'achat moyen par unité de stock (€/g, €/ml ou €/u)"
    )
    prix_unitaire_vente = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Prix de vente par unité de stock (€/g, €/ml ou €/u)",
        null=True, blank=True
    )

    prix_supplement_salade = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    groupe = models.CharField(max_length=20, choices=GROUPE_CHOICES, default='fruits')
    vendable_directement = models.BooleanField(
        default=False,
        help_text="Indique si l'ingrédient est vendable directement."
    )
    taux_tva_achat = models.DecimalField(
        max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES, default=5.5,
        help_text="TVA sur prix d'achat (%)"
    )
    taux_tva_vente = models.DecimalField(
        max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES, default=10,
        help_text="TVA sur prix de vente (%)"
    )
    
    # NOUVEAU : Lien vers ProduitTransforme pour les ingrédients qui sont eux-mêmes des produits transformés
    produit_transforme = models.ForeignKey(
        'ProduitTransforme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Si cet ingrédient est un produit transformé, lien vers sa recette"
    )

    class Meta:
        ordering = ['nom']
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['groupe']),
        ]

    def __str__(self):
        return f"{self.nom} - {self.get_groupe_display()}"

    # ---------- Calculs TTC ----------
    def calculer_prix_achat_ttc(self, quantite: Decimal | int | float) -> Decimal:
        """
        quantite : exprimée dans l'unité de STOCK (g/ml/u)
        """
        q = Decimal(str(quantite))
        prix_ht = q * (self.prix_unitaire_achat or Decimal('0'))
        return prix_ht * (Decimal('1') + (Decimal(str(self.taux_tva_achat)) / Decimal('100')))

    def calculer_prix_vente_ttc(self, quantite: Decimal | int | float) -> Decimal:
        """
        quantite : exprimée dans l'unité de STOCK (g/ml/u)
        """
        q = Decimal(str(quantite))
        pu_vente = self.prix_unitaire_vente or Decimal('0')
        prix_ht = q * pu_vente
        return prix_ht * (Decimal('1') + (Decimal(str(self.taux_tva_vente)) / Decimal('100')))

    # ---------- Stock (legacy) ----------
    def mettre_a_jour_stock(self, quantite: int, prix_unitaire: Decimal):
        """
        Méthode legacy : ajuste directement le stock (déjà dans l'unité de STOCK) et le prix unitaire d'achat.
        Préfère utiliser .achat(...) pour saisir une facture fournisseur avec conversions.
        """
        self.quantite_stock = (self.quantite_stock or 0) + int(quantite)
        self.prix_unitaire_achat = prix_unitaire
        self.save(update_fields=['quantite_stock', 'prix_unitaire_achat'])

    # ---------- Flux réels (recommandé) ----------
    def achat(self, quantite: Decimal | int | float, unite_achat: str, prix_total_eur: Decimal | float | int) -> int:
        """
        Enregistre un ACHAT fournisseur :
          - Convertit la quantité achetée (kg/l/u...) vers l'unité de STOCK (g/ml/u) -> ENTIER
          - Met à jour le stock
          - Met à jour le prix_unitaire_achat en €/unité de STOCK via le prix total

        Exemple :
          farine.unite_stock='g' ; achat(25, 'kg', 37.50) => +25_000 g ; p.u. = 37.50 / 25_000 = 0.0015 €/g
          lait.unite_stock='l'   ; achat(10, 'l', 11.00)  => +10_000 ml ; p.u. = 11.00 / 10_000 = 0.0011 €/ml
        """
        from .utils import to_stock_units, price_per_stock_unit  # import local pour éviter import cycles
        ajout_stock = to_stock_units(quantite, unite_achat, self.unite_stock)
        self.quantite_stock = (self.quantite_stock or 0) + int(ajout_stock)
        self.prix_unitaire_achat = price_per_stock_unit(prix_total_eur, quantite, unite_achat, self.unite_stock)
        self.save(update_fields=['quantite_stock', 'prix_unitaire_achat'])
        return int(ajout_stock)

    def retirer_pour_recette(self, quantite: Decimal | int | float, unite_recette: str) -> int:
        """
        Déduit du stock pour une RECETTE :
          - Convertit la quantité recette (g/ml/u) vers l'unité de STOCK (g/ml/u) -> ENTIER
          - Contrôle le stock suffisant
          - Déduit et sauvegarde

        Exemple :
          lait.unite_stock='l' ; retirer_pour_recette(0.03, 'l') => -30 ml
          jaune.unite_stock='g'; retirer_pour_recette(18, 'g')   => -18 g
        """
        from .utils import to_stock_units  # import local pour éviter import cycles
        q_stock = to_stock_units(quantite, unite_recette, self.unite_stock)
        if self.quantite_stock < q_stock:
            raise ValueError(f"Stock insuffisant pour {self.nom} ({self.quantite_stock} < {q_stock})")
        self.quantite_stock -= int(q_stock)
        self.save(update_fields=['quantite_stock'])
        return int(q_stock)



class Fournisseur(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom



class ListeDeCourses(models.Model):
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name='listes_de_courses')
    date = models.DateField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    nom = models.CharField(max_length=100, unique=True, blank=True)  # Champ ajouté pour nom unique

    def __str__(self):
        return self.nom

    def archive(self):
        self.archived = True
        self.archived_at = timezone.now()
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['fournisseur', 'date'],
                condition=models.Q(archived=False),
                name='unique_active_list_per_fournisseur_and_date'
            )
        ]
    
class ArticleListeDeCourses(models.Model):
    liste = models.ForeignKey(ListeDeCourses, on_delete=models.CASCADE, related_name='articles')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    unite = models.CharField(
        max_length=10,
        choices=[
            ('g', 'grammes'),
            ('l', 'litres'),
            ('u', 'unités')
        ],
        default='u'
    )
    est_achete = models.BooleanField(default=False, help_text="Indique si l'article a été acheté.")
    prix_unitaire_achat = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix d'achat au moment de l'ajout à la liste")

    def save(self, *args, **kwargs):
        print(f"Sauvegarde de l'article : {self.ingredient.nom} pour {self.liste.fournisseur.nom}")
        print(f"Quantité : {self.quantite} {self.get_unite_display()}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite} {self.get_unite_display()} de {self.ingredient.nom} pour {self.liste.fournisseur.nom}"




# models.py
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.apps import apps  # 👈 AJOUTE-LE
from .utils import to_stock_units

class ProduitTransforme(models.Model):
    CATEGORIES = [
    ("boulangerie", "Boulangerie"),
    ("sauces", "Sauces & Condiments"),
    ("viandes", "Viandes Poulets & Oeufs"),
    ("legumes", "Légumes Préparés"),
    ("fromage", "Produits Fromager"),
    ("desserts", "Desserts Préparés"),
    ("feculents", "Féculents"),
]

    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=50, choices=CATEGORIES, default="boulangerie")
    quantite_disponible = models.PositiveIntegerField(default=0)
    unite = models.CharField(
        max_length=10,
        choices=[('g', 'grammes'), ('l', 'litres'), ('u', 'unités')],
        default='u'
    )

    # AJOUTEZ CETTE MÉTHODE __str__
    def __str__(self):
        return f"{self.nom} ({self.quantite_disponible} {self.get_unite_display()} disponible)"

    class Meta:
        ordering = ['nom']  # Optionnel : pour un tri par défaut par nom


class PouletOption(models.Model):
    CATEGORIE_CHOICES = [
        ('assaisonnement', 'Assaisonnement'),
        ('accompagnement', 'Accompagnement'),
        ('sauce', 'Sauce au choix'),
        ('supplement', 'Supplément'),




    ]
    
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    prix_supplement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['categorie', 'ordre', 'nom']
        verbose_name = "Option Poulet"
        verbose_name_plural = "Options Poulet"
    
    def __str__(self):
        if self.prix_supplement > 0:
            return f"{self.nom} (+{self.prix_supplement}€)"
        return self.nom

from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils.html import linebreaks


class Plat(models.Model):
    TAUX_TVA_CHOICES = [
        (Decimal('5.5'), '5.5%'),
        (Decimal('10.0'), '10.0%'),
        (Decimal('20.0'), '20.0%'),
    ]
    
    TYPE_PLAT_CHOICES = [
        ('burger', 'Burger'),
        ('couscous', 'Couscous'),
        ('crousty', 'Crousty'),
        ('autre', 'Autre'),
        ('poulet','Poulet')
    ]
    
    TYPE_BURGER_CHOICES = [
        ('classique', 'Classique - Potato Buns'),
        ('gourmet', 'Gourmet - Buns Boulanger'),
        ('non_burger', 'Non applicable'),
    ]

    # Champs de base
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description_courte = models.TextField()
    description_longue = models.TextField()
    prix_unitaire_ttc = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix unitaire TTC du plat")
    taux_tva = models.DecimalField(max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES, default=Decimal('10.0'), help_text="TVA en pourcentage")
    photo = models.ImageField(upload_to='plats/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    
    # NOUVEAU : Type de plat pour gérer les options spécifiques
    type_plat = models.CharField(
        max_length=20, 
        choices=TYPE_PLAT_CHOICES, 
        default='autre',
        help_text="Type de plat pour gérer les options spécifiques"
    )
    
    # Champ pour les burgers
    type_burger = models.CharField(
        max_length=20, 
        choices=TYPE_BURGER_CHOICES, 
        default='non_burger',
        help_text="Type de burger (uniquement pour les burgers)"
    )
    
    # Liens avec le système de recettes et produits transformés
    recette = models.ForeignKey(
        'Recette', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Recette principale du plat (si le plat est un produit transformé complexe)"
    )
    produit_transforme = models.ForeignKey(
        'ProduitTransforme',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Produit transformé principal du plat (si applicable)"
    )
    est_compose = models.BooleanField(
        default=True,
        help_text="Si True, le plat est composé d'ingrédients et/ou produits transformés. Si False, c'est un produit simple."
    )

    def __str__(self):
        return self.nom


    def get_crousty_options_par_categorie(self):
        """Retourne les options Crousty groupées par catégorie"""
        if self.type_plat != 'crousty':
            return {}
        
        options = CroustyOption.objects.filter(disponible=True)
        options_par_categorie = {}
        
        for option in options:
            if option.categorie not in options_par_categorie:
                options_par_categorie[option.categorie] = []
            options_par_categorie[option.categorie].append({
                'id': option.id,
                'nom': option.nom,
                'prix_supplement': float(option.prix_supplement),
                'categorie': option.categorie
            })
        
        return options_par_categorie
    
    def get_poulet_options_par_categorie(self):
        """Retourne les options Poulet groupées par catégorie"""
        if self.type_plat != 'poulet':
            return {}
        
        options = PouletOption.objects.filter(disponible=True)
        options_par_categorie = {}
        
        for option in options:
            if option.categorie not in options_par_categorie:
                options_par_categorie[option.categorie] = []
            options_par_categorie[option.categorie].append({
                'id': option.id,
                'nom': option.nom,
                'prix_supplement': float(option.prix_supplement),
                'categorie': option.categorie
            })
        
        return options_par_categorie
    

    @property
    def prix_unitaire_ht(self):
        """Calcule et retourne le prix HT en fonction du prix TTC et du taux de TVA avec un arrondi strict à 2 décimales."""
        taux_tva_decimal = Decimal(self.taux_tva) / Decimal('100')
        prix_ht = self.prix_unitaire_ttc / (Decimal('1') + taux_tva_decimal)
        return prix_ht.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        """Arrondir le prix TTC à 2 décimales avant d'enregistrer pour éviter les erreurs de précision."""
        if self.prix_unitaire_ttc:
            self.prix_unitaire_ttc = self.prix_unitaire_ttc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Validation cohérence
        if self.recette and self.produit_transforme:
            if self.recette.produit != self.produit_transforme:
                raise ValueError("Le produit transformé de la recette doit correspondre au produit transformé du plat")
        
        super().save(*args, **kwargs)

    # Méthodes pour la gestion de production

    def get_tous_les_composants(self):
        """
        Retourne tous les composants du plat :
        - Ingrédients directs (via Cuisson)
        - Produits transformés directs (via Cuisson)  
        - Ingrédients de la recette (si le plat a une recette)
        """
        composants = []
        
        # Composants directs via Cuisson
        for cuisson in self.cuissons.all():
            if cuisson.ingredient:
                composants.append({
                    'type': 'ingredient_direct',
                    'objet': cuisson.ingredient,
                    'quantite': cuisson.quantite,
                    'unite': cuisson.unite,
                    'mode_cuisson': cuisson.mode_cuisson
                })
            elif cuisson.produit_transforme:
                composants.append({
                    'type': 'produit_transforme_direct',
                    'objet': cuisson.produit_transforme,
                    'quantite': cuisson.quantite,
                    'unite': cuisson.unite,
                    'mode_cuisson': cuisson.mode_cuisson
                })
        
        # Composants de la recette (ingrédients et produits transformés)
        if self.recette:
            for ing_recette in self.recette.ingredients.all():
                if ing_recette.ingredient:
                    composants.append({
                        'type': 'ingredient_recette',
                        'objet': ing_recette.ingredient,
                        'quantite': ing_recette.quantite,
                        'unite': ing_recette.unite,
                        'recette': self.recette
                    })
                elif ing_recette.produit_transforme:
                    composants.append({
                        'type': 'produit_transforme_recette', 
                        'objet': ing_recette.produit_transforme,
                        'quantite': ing_recette.quantite,
                        'unite': ing_recette.unite,
                        'recette': self.recette
                    })
        
        return composants

    def verifier_disponibilite_complete(self, quantite=1):
        """
        Vérifie la disponibilité de tous les composants pour produire X quantités du plat
        """
        messages_erreur = []
        
        for composant in self.get_tous_les_composants():
            if composant['type'] in ['ingredient_direct', 'ingredient_recette']:
                ingredient = composant['objet']
                quantite_requise = composant['quantite'] * quantite
                
                # Conversion vers l'unité de stock si nécessaire
                if composant['unite'] != ingredient.unite_stock:
                    from .utils import to_stock_units
                    try:
                        quantite_requise_stock = to_stock_units(
                            quantite_requise, 
                            composant['unite'], 
                            ingredient.unite_stock
                        )
                    except Exception as e:
                        messages_erreur.append(f"Erreur conversion {ingredient.nom}: {e}")
                        continue
                else:
                    quantite_requise_stock = quantite_requise
                
                if ingredient.quantite_stock < quantite_requise_stock:
                    messages_erreur.append(
                        f"{ingredient.nom}: stock {ingredient.quantite_stock} {ingredient.unite_stock} "
                        f"< requis {quantite_requise_stock} {ingredient.unite_stock}"
                    )
            
            elif composant['type'] in ['produit_transforme_direct', 'produit_transforme_recette']:
                produit = composant['objet']
                quantite_requise = composant['quantite'] * quantite
                
                if produit.quantite_disponible < quantite_requise:
                    messages_erreur.append(
                        f"{produit.nom}: stock {produit.quantite_disponible} {produit.unite} "
                        f"< requis {quantite_requise} {produit.unite}"
                    )
        
        return len(messages_erreur) == 0, messages_erreur

    def calculer_cout_revient(self, quantite=1):
        """
        Calcule le coût de revient du plat basé sur tous ses composants
        """
        cout_total = Decimal('0.00')
        
        for composant in self.get_tous_les_composants():
            if composant['type'] in ['ingredient_direct', 'ingredient_recette']:
                ingredient = composant['objet']
                quantite_calc = composant['quantite'] * quantite
                
                # Utiliser le prix d'achat de l'ingrédient
                if ingredient.prix_unitaire_achat:
                    cout_total += quantite_calc * ingredient.prix_unitaire_achat
            
            elif composant['type'] in ['produit_transforme_direct', 'produit_transforme_recette']:
                produit = composant['objet']
                quantite_calc = composant['quantite'] * quantite
                
                # Utiliser le prix de revient du produit transformé si disponible
                if hasattr(produit, 'recette') and produit.recette and produit.recette.prix_revient_unitaire_ttc:
                    cout_total += quantite_calc * produit.recette.prix_revient_unitaire_ttc
                # Sinon, utiliser un prix par défaut ou estimé
                elif hasattr(produit, 'prix_revient_estime'):
                    cout_total += quantite_calc * produit.prix_revient_estime
        
        return cout_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def produire_plat(self, quantite=1):
        """
        Déduit les stocks pour produire X quantités du plat
        """
        # Vérifier d'abord la disponibilité
        disponible, erreurs = self.verifier_disponibilite_complete(quantite)
        if not disponible:
            raise ValueError(f"Stock insuffisant: {', '.join(erreurs)}")
        
        # Déduire les stocks
        for composant in self.get_tous_les_composants():
            if composant['type'] in ['ingredient_direct', 'ingredient_recette']:
                ingredient = composant['objet']
                quantite_requise = composant['quantite'] * quantite
                
                # Conversion vers l'unité de stock
                if composant['unite'] != ingredient.unite_stock:
                    from .utils import to_stock_units
                    quantite_requise_stock = to_stock_units(
                        quantite_requise, 
                        composant['unite'], 
                        ingredient.unite_stock
                    )
                else:
                    quantite_requise_stock = quantite_requise
                
                ingredient.quantite_stock -= quantite_requise_stock
                ingredient.save()
            
            elif composant['type'] in ['produit_transforme_direct', 'produit_transforme_recette']:
                produit = composant['objet']
                quantite_requise = composant['quantite'] * quantite
                
                produit.quantite_disponible -= quantite_requise
                produit.save()
        
        return True

    @property
    def marge_brute(self):
        """Calcule la marge brute du plat"""
        cout = self.calculer_cout_revient(1)
        return (self.prix_unitaire_ttc - cout).quantize(Decimal('0.01'))

    @property 
    def taux_marge(self):
        """Calcule le taux de marge"""
        cout = self.calculer_cout_revient(1)
        if cout > 0:
            return ((self.prix_unitaire_ttc - cout) / cout * 100).quantize(Decimal('0.1'))
        return Decimal('0.0')


class CroustyOption(models.Model):
    CATEGORIE_CHOICES = [
        ('fromage', 'Fromage au choix'),
        ('sauce_rouge', 'Sauce Rouge Signature'),
        ('sauce_erc', 'Sauce ERC au choix'),
        ('supplement', 'Supplément'),
        ('prot_veggie', 'Protéine Végétarienne'),
    ]
    
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    prix_supplement = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['categorie', 'ordre', 'nom']
        verbose_name = "Option Crousty"
        verbose_name_plural = "Options Crousty"
    
    def __str__(self):
        if self.prix_supplement > 0:
            return f"{self.nom} (+{self.prix_supplement}€)"
        return self.nom

class Menu(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    prix_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES, default=10)
    disponible = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='menus/', blank=True, null=True)  # ✅ ajout du champ photo

    def __str__(self):
        return self.nom

    @property
    def prix_ht(self):
        return (self.prix_ttc / (1 + Decimal(self.taux_tva) / 100)).quantize(Decimal("0.01"))

class ComposantMenuFixe(models.Model):
    ROLE_CHOICES = [
        ('entree', 'Entrée'),
        ('plat', 'Plat'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
        ('salade', 'Salade personnalisée'),
        ('couscous', 'Couscous personnalisé'),
    ]

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='composants_fixes')
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, null=True, blank=True)
    salade = models.BooleanField(default=False)
    couscous = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        if self.plat:
            nom = self.plat.nom
        elif self.salade:
            nom = "Salade personnalisée"
        elif self.couscous:
            nom = "Couscous personnalisé"
        else:
            nom = "Inconnu"
        return f"{nom} ({self.get_role_display()}) dans {self.menu.nom}"

class ChoixMenu(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='choix')
    role = models.CharField(max_length=20, choices=ComposantMenuFixe.ROLE_CHOICES)

    plats_possibles = models.ManyToManyField(Plat, blank=True, related_name='choix_de_menu')
    autorise_salade_personnalisee = models.BooleanField(default=False)
    autorise_couscous_personnalise = models.BooleanField(default=False)

    # ✅ Ajouts pour le couscous personnalisé
    nombre_viandes_incluses = models.PositiveIntegerField(default=1)
    viandes_possibles = models.ManyToManyField('ViandeCouscous', blank=True, related_name='choixmenu_autorises')

    nombre_elements_inclus = models.IntegerField(default=1)


    def __str__(self):
        types = []
        if self.plats_possibles.exists():
            types.append(f"{self.plats_possibles.count()} plats")
        if self.autorise_salade_personnalisee:
            types.append("salade personnalisée")
        if self.autorise_couscous_personnalise:
            viande_txt = f"{self.nombre_viandes_incluses} viande{'s' if self.nombre_viandes_incluses > 1 else ''}"
            types.append(f"couscous personnalisé ({viande_txt})")

        return f"{self.menu.nom} - Choix {self.get_role_display()} : {', '.join(types)}"



# Modèle Option pour les options des plats
# Modèle Option pour les options des plats
class Option(models.Model):
    CATEGORIE_OPTION_CHOICES = [
        ('supp_viande', 'Extra viande'),
        ('supp_fromage', 'Extra fromage'),
        ('supp_croustillant', 'Extra Croustillant'),
        ('supp_sauce', 'Extra Sauce'),
        ('autre', 'Autre'),
    ]
    
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    nom_option = models.CharField(max_length=100)
    prix_unitaire_ttc = models.DecimalField(max_digits=5, decimal_places=2, help_text="Prix unitaire TTC de l'option")
    taux_tva = models.DecimalField(max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES, default=10, help_text="TVA sur prix de vente")
    
    # NOUVEAUX CHAMPS pour la catégorisation
    categorie = models.CharField(
        max_length=20, 
        choices=CATEGORIE_OPTION_CHOICES, 
        default='autre',
        help_text="Catégorie de l'option pour l'affichage groupé"
    )
    ordre = models.PositiveIntegerField(
        default=0, 
        help_text="Ordre d'affichage dans la catégorie"
    )

    class Meta:
        ordering = ['categorie', 'ordre', 'nom_option']

    def __str__(self):
        return f"{self.nom_option} pour {self.plat.nom}"

    @property
    def prix_unitaire_ht(self):
        """Calcule et retourne le prix HT en fonction du prix TTC et du taux de TVA."""
        return self.prix_unitaire_ttc / (1 + (self.taux_tva / 100))

    def verifier_disponibilite(self):
        ingredients_disponibles = all(
            ingredient_option.ingredient.quantite_stock >= ingredient_option.quantite_necessaire
            for ingredient_option in self.ingredient_options.all()
        )
        produits_transformes_disponibles = all(
            produit_transforme_option.produit_transforme.quantite_disponible >= produit_transforme_option.quantite_necessaire
            for produit_transforme_option in self.produit_transforme_options.all()
        )
        return ingredients_disponibles and produits_transformes_disponibles




# Modèle ProduitVenteDirecte pour les produits vendus directement
class ProduitVenteDirecte(models.Model):
    ingredient = models.OneToOneField(
        'Ingredient', 
        on_delete=models.CASCADE, 
        related_name='produit_vente_directe'
    )
    prix_unitaire_vente_ttc = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Prix de vente TTC du produit"
    )
    taux_tva_vente = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        choices=TAUX_TVA_CHOICES, 
        default=10, 
        help_text="TVA en pourcentage"
    )

    def __str__(self):
        return f"{self.ingredient.nom} - {self.prix_unitaire_vente_ttc} € TTC"

    @property
    def prix_unitaire_vente_ht(self):
        """
        Calcule le prix HT à partir du prix TTC et du taux de TVA, arrondi à deux décimales.
        """
        prix_ht = self.prix_unitaire_vente_ttc / (1 + Decimal(self.taux_tva_vente) / 100)
        return prix_ht.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# Modèle Cuisson
class Cuisson(models.Model):
    MODE_CUISSON_CHOICES = [
        ('grill', 'Grill'),
        ('josper', 'Josper'),
        ('friteuse', 'Friteuse'),
        ('cuiseur', 'Cuiseur'),
        ('four', 'Four'),
        ('cuit_vapeur', 'Cuit vapeur'),
        ('sans_cuisson', 'Sans cuisson'),
    ]

    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='cuissons', null=True, blank=True)
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='cuissons', null=True, blank=True)
    
    # Composants : soit ingrédient, soit produit transformé
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=True, blank=True)
    produit_transforme = models.ForeignKey(ProduitTransforme, on_delete=models.CASCADE, null=True, blank=True)
    
    # AMÉLIORATION : Quantité avec unité précise
    quantite = models.DecimalField(max_digits=10, decimal_places=3, help_text="Quantité nécessaire")
    unite = models.CharField(
        max_length=10,
        choices=[('g', 'grammes'), ('kg', 'kilogrammes'), ('l', 'litres'), ('ml', 'millilitres'), ('u', 'unités')],
        default='g'
    )
    
    mode_cuisson = models.CharField(max_length=50, choices=MODE_CUISSON_CHOICES, default='sans_cuisson')
    temps_cuisson = models.PositiveIntegerField(null=True, blank=True, help_text="Temps de cuisson en minutes")
    temperature = models.PositiveIntegerField(null=True, blank=True, help_text="Température de cuisson en °C")
    
    # Instructions spécifiques
    instructions = models.TextField(blank=True, help_text="Instructions particulières pour cette cuisson")
    ordre_preparation = models.PositiveIntegerField(default=1, help_text="Ordre de préparation dans le plat")

    class Meta:
        ordering = ['plat', 'ordre_preparation']
        verbose_name_plural = "Cuissons"

    def __str__(self):
        if self.ingredient:
            nom_composant = self.ingredient.nom
        elif self.produit_transforme:
            nom_composant = self.produit_transforme.nom
        else:
            nom_composant = "Composant non spécifié"
            
        plat_nom = self.plat.nom if self.plat else f"Option {self.option.nom_option}" if self.option else "Sans plat"
        
        return f"{self.quantite} {self.unite} {nom_composant} pour {plat_nom} ({self.mode_cuisson})"

    def clean(self):
        """Validation de cohérence"""
        from django.core.exceptions import ValidationError
        
        if not self.ingredient and not self.produit_transforme:
            raise ValidationError("Une cuisson doit avoir soit un ingrédient, soit un produit transformé.")
        
        if self.ingredient and self.produit_transforme:
            raise ValidationError("Une cuisson ne peut avoir qu'un seul type de composant (ingrédient OU produit transformé).")
        
        if not self.plat and not self.option:
            raise ValidationError("Une cuisson doit être liée à un plat ou une option.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_quantite_stock_unite(self):
        """
        Convertit la quantité dans l'unité de stock du composant
        """
        if self.ingredient:
            unite_cible = self.ingredient.unite_stock
        elif self.produit_transforme:
            unite_cible = self.produit_transforme.unite
        else:
            return self.quantite, self.unite
            
        from .utils import to_stock_units
        try:
            quantite_convertie = to_stock_units(self.quantite, self.unite, unite_cible)
            return quantite_convertie, unite_cible
        except Exception as e:
            # En cas d'erreur de conversion, retourner la quantité originale
            return self.quantite, self.unite

    def verifier_disponibilite(self):
        """
        Vérifie si le composant est disponible en stock
        """
        if self.ingredient:
            quantite_requise, unite = self.get_quantite_stock_unite()
            return self.ingredient.quantite_stock >= quantite_requise
        elif self.produit_transforme:
            return self.produit_transforme.quantite_disponible >= self.quantite
        return False

    @property
    def cout_composant(self):
        """
        Calcule le coût de ce composant
        """
        if self.ingredient and self.ingredient.prix_unitaire_achat:
            quantite_stock, _ = self.get_quantite_stock_unite()
            return quantite_stock * self.ingredient.prix_unitaire_achat
        elif self.produit_transforme and hasattr(self.produit_transforme, 'recette'):
            if self.produit_transforme.recette and self.produit_transforme.recette.prix_revient_unitaire_ttc:
                return self.quantite * self.produit_transforme.recette.prix_revient_unitaire_ttc
        return Decimal('0.00')


# Modèle CodePromo
class CodePromo(models.Model):
    REDUCTION_TYPE_CHOICES = [
        ('P', 'Pourcentage'),
        ('E', 'Euros'),
    ]

    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    reduction_amount = models.PositiveIntegerField()
    reduction_type = models.CharField(max_length=1, choices=REDUCTION_TYPE_CHOICES)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()

    def __str__(self):
        return self.code

    def est_valide(self):
        maintenant = timezone.now()
        return self.date_debut <= maintenant <= self.date_fin

# Modèle Panier
from decimal import Decimal
from django.db import models

class Panier(models.Model):
    session_key = models.CharField(max_length=255)
    commande = models.OneToOneField('Commande', on_delete=models.SET_NULL, null=True, blank=True, related_name='panier_associe')
    created_at = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)  # ✅ Ajout ici
    frais_livraison = models.DecimalField(max_digits=5, decimal_places=2, default=3.50)
    frais_gestion = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    code_promo = models.ForeignKey('CodePromo', on_delete=models.SET_NULL, null=True, blank=True)
    promotion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_locked = models.BooleanField(default=False)


    def __str__(self):
        return f"Panier {self.id} - Session: {self.session_key}"

    def calculate_sous_total(self):
        self.sous_total = sum(article.prix_total for article in self.articlepanier_set.all())
        self.save()
        return self.sous_total

    def appliquer_frais_gestion(self):
        if self.commande and self.commande.moyen_paiement and self.commande.moyen_paiement.startswith('ticket_restaurant'):
            self.frais_gestion = Decimal('1.00')
        else:
            self.frais_gestion = Decimal('0.00')
        self.save()

    def calculate_totals(self):
        """Alias pour calculate_total_price() - pour compatibilité"""
        return self.calculate_total_price()

    def calculate_total_price(self):
        self.calculate_sous_total()

        if self.commande and self.commande.is_commande_a_emporter:
            frais_livraison_decimal = Decimal(0)
        else:
            frais_livraison_decimal = Decimal(self.frais_livraison)

        # 🔴 C'est ici que le frais de gestion doit être calculé
        if self.commande and self.commande.moyen_paiement and 'ticket' in self.commande.moyen_paiement:
            self.frais_gestion = Decimal('1.00')
            print(f"[PRINT] Frais de gestion appliqué pour commande {self.commande.id}")
        else:
            self.frais_gestion = Decimal('0.00')
            print(f"[PRINT] Aucun frais de gestion appliqué pour commande {self.commande.id if self.commande else '??'}")

        self.promotion = Decimal(0)

        total = self.sous_total + frais_livraison_decimal + self.frais_gestion

        if self.code_promo and self.code_promo.est_valide():
            if self.code_promo.reduction_type == 'P':
                self.promotion = (total * Decimal(self.code_promo.reduction_amount)) / 100
            else:
                self.promotion = Decimal(self.code_promo.reduction_amount)
            total -= self.promotion

        self.prix_total = total
        self.save()

        print(f"[PRINT] Total panier = {self.prix_total}, Sous-total = {self.sous_total}, Livraison = {frais_livraison_decimal}, Gestion = {self.frais_gestion}, Réduction = {self.promotion}")
        return self.prix_total


    def apply_code_promo(self, code_promo_code):
        try:
            code_promo = CodePromo.objects.get(code=code_promo_code)
            if code_promo.est_valide():
                self.code_promo = code_promo
                self.calculate_total_price()
                return code_promo
        except CodePromo.DoesNotExist:
            self.code_promo = None
            self.promotion = Decimal(0)
            self.calculate_total_price()
        return None

    @property
    def frais_livraison_effectif(self):
        if self.commande and self.commande.is_commande_a_emporter:
            return Decimal(0)
        return self.frais_livraison

    def save(self, *args, **kwargs):
        if self.commande and self.commande.is_paid:
            raise ValueError("Le panier ne peut plus être modifié après le paiement de la commande.")
        super().save(*args, **kwargs)


from django.db import models
from decimal import Decimal, ROUND_HALF_UP

# Modèle SaladePersonnalisee
from decimal import Decimal, ROUND_HALF_UP

from decimal import Decimal, ROUND_HALF_UP
from django.db import models

class SaladePersonnalisee(models.Model):
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)

    base = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='salade_bases')
    sauce = models.ForeignKey('Ingredient', on_delete=models.CASCADE, related_name='salade_sauces')

    proteines = models.ManyToManyField('Ingredient', related_name='salade_proteines', blank=True)
    garnitures = models.ManyToManyField('Ingredient', related_name='salade_garnitures', blank=True)
    toppings = models.ManyToManyField('Ingredient', related_name='salade_toppings', blank=True)
    supplement = models.ManyToManyField('Ingredient', related_name='salade_supplements', blank=True)

    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    MAX_GARNITURES = 5
    MAX_TOPPINGS = 2
    PRIX_BASE = Decimal('13.00')

    def __str__(self):
        nom_client = self.client if self.client else "client anonyme"
        return f"Salade personnalisée de {nom_client}"

    def calculate_prix_total(self):
        prix_total = self.PRIX_BASE

        # ➕ Protéines
        for p in self.proteines.all():
            prix = getattr(p, 'prix_supplement_salade', Decimal('0.00')) or Decimal('0.00')
            prix_total += prix

        # ➕ Garnitures (toutes payantes si prix > 0)
        for g in self.garnitures.all():
            prix = getattr(g, 'prix_supplement_salade', Decimal('0.00')) or Decimal('0.00')
            if prix > 0:
                prix_total += prix

        # ➕ Toppings
        for t in self.toppings.all():
            prix = getattr(t, 'prix_supplement_salade', Decimal('0.00')) or Decimal('0.00')
            if prix > 0:
                prix_total += prix

        # ➕ Suppléments
        for s in self.supplement.all():
            prix_total += getattr(s, 'prix_supplement_salade', Decimal('0.00')) or Decimal('0.00')

        # ➕ Sauce
        if self.sauce:
            prix_total += getattr(self.sauce, 'prix_supplement_salade', Decimal('0.00')) or Decimal('0.00')

        self.prix_total = prix_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.prix_total


    def save(self, *args, **kwargs):
        # On ne calcule pas ici car les M2M ne sont pas encore disponibles à ce stade
        super().save(*args, **kwargs)

    def verifier_disponibilite_ingredients(self):
        """
        Vérifie que tous les ingrédients sont disponibles en stock.
        """
        ingredients = [self.base, self.sauce] \
                      + list(self.proteines.all()) \
                      + list(self.garnitures.all()) \
                      + list(self.toppings.all()) \
                      + list(self.supplement.all())

        return all(i.quantite_stock > 0 for i in ingredients)

    def deduire_ingredients_stock(self):
        """
        Déduit 1 unité de chaque ingrédient utilisé.
        """
        ingredients = [self.base, self.sauce] \
                      + list(self.proteines.all()) \
                      + list(self.garnitures.all()) \
                      + list(self.toppings.all()) \
                      + list(self.supplement.all())

        for i in ingredients:
            if i.quantite_stock > 0:
                i.quantite_stock -= 1
                i.save()
            else:
                raise ValueError(f"Stock insuffisant pour {i.nom}")



from decimal import Decimal
from django.db import models
from django.conf import settings

from django.db import models
from decimal import Decimal

# -----------------------------------
# 🏷️ Formule de couscous (type : Royal, Tradition...)
# -----------------------------------
class FormuleCouscous(models.Model):
    nom = models.CharField(max_length=100)
    nombre_viandes_incluses = models.PositiveIntegerField()
    prix_base_ttc = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom} - {self.prix_base_ttc} € TTC"


# -----------------------------------
# 🥩 Viande disponible pour le couscous
# -----------------------------------
class ViandeCouscous(models.Model):
    nom = models.CharField(max_length=100)
    portion = models.CharField(max_length=100)
    supplement_inclus = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nom} ({self.portion})"


# -----------------------------------
# 🍽️ Option XL
# -----------------------------------
class OptionXL(models.Model):
    nom = models.CharField(max_length=100, default="Option XL")
    supplement = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom} (+{self.supplement} €)"


# -----------------------------------
# 🥗 Accompagnement pour le couscous
# -----------------------------------
class AccompagnementCouscous(models.Model):
    code = models.CharField(max_length=50, unique=True)  # ex : 'legumes', 'pois_chiches'
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


# -----------------------------------
# 🍛 Couscous Personnalisé
# -----------------------------------
class CouscousPersonnalise(models.Model):
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True)
    formule = models.ForeignKey(FormuleCouscous, on_delete=models.CASCADE)
    viandes_choisies = models.ManyToManyField(ViandeCouscous, through='ChoixViandeCouscous')
    accompagnements = models.ManyToManyField(AccompagnementCouscous, blank=True)
    option_xl = models.BooleanField(default=False)
    prix_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def calculate_prix_total(self):
        prix = self.formule.prix_base_ttc
        inclus_restants = self.formule.nombre_viandes_incluses

        for choix in self.choixviandecouscous_set.all():
            if choix.est_incluse and inclus_restants > 0:
                prix += choix.viande.supplement_inclus
                inclus_restants -= 1
            else:
                prix += choix.viande.supplement_extra

        if self.option_xl:
            xl_option = OptionXL.objects.first()
            if xl_option:
                prix += xl_option.supplement

        self.prix_total = prix.quantize(Decimal('0.01'))
        return self.prix_total

    def __str__(self):
        return f"{self.formule.nom} personnalisé"


# -----------------------------------
# 🔀 Viandes choisies dans le couscous
# -----------------------------------
class ChoixViandeCouscous(models.Model):
    couscous = models.ForeignKey(CouscousPersonnalise, on_delete=models.CASCADE)
    viande = models.ForeignKey(ViandeCouscous, on_delete=models.CASCADE)
    est_incluse = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.viande.nom} ({'incluse' if self.est_incluse else 'supplément'})"

class Accompagnement(models.Model):
    nom = models.CharField(max_length=100)
    prix_supplement = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ordre = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Accompagnement"
        verbose_name_plural = "Accompagnements"
    
    def __str__(self):
        if self.prix_supplement > 0:
            return f"{self.nom} (+{self.prix_supplement}€)"
        return self.nom


class ArticlePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE)
    
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, null=True, blank=True)
    salade_personnalisee = models.ForeignKey(SaladePersonnalisee, on_delete=models.CASCADE, null=True, blank=True)
    couscous_personnalise = models.ForeignKey('CouscousPersonnalise', on_delete=models.CASCADE, null=True, blank=True)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, null=True, blank=True)

    nom_personnalise = models.CharField(max_length=255, blank=True, null=True)
    options = models.ManyToManyField(Option, blank=True)
    
    # Options spécifiques
    options_crousty = models.ManyToManyField(
        'CroustyOption', 
        blank=True,
        verbose_name="Options Crousty"
    )
    
    # Options poulet
    options_poulet = models.ManyToManyField(
        'PouletOption', 
        blank=True,
        verbose_name="Options Poulet"
    )
    
    # 🆕 CHAMP POUR STOCKER LES OPTIONS AVEC DOUBLONS
    options_poulet_avec_quantites = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Options Poulet avec quantités"
    )
    
    # 🆕 ACCOMPAGNEMENT POUR BURGERS
    accompagnement = models.ForeignKey(
        'Accompagnement', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Accompagnement"
    )
    
    # 🆕 AJOUT DU CHAMP MANQUANT
    supplements_menu = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Suppléments menu"
    )
    
    quantite = models.PositiveIntegerField(default=1)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))

    def __str__(self):
        if self.menu:
            nom_article = f"Menu {self.menu.nom}"
        elif self.plat:
            nom_article = self.plat.nom
        elif self.salade_personnalisee:
            nom_article = "Salade personnalisée"
        elif self.couscous_personnalise:
            nom_article = "Couscous personnalisé"
        else:
            nom_article = "Article inconnu"

        return f'{self.quantite} x {nom_article} (Total: {self.prix_total})'

    def calculate_total_price(self):
        """Calcule ET SAUVEGARDE le prix total avec toutes les options"""
        prix_total = self.calculate_base_price() * self.quantite
        self.prix_total = prix_total
        self.save(update_fields=['prix_total'])  # ⭐ Important : sauvegarder explicitement
        
        # 🔥 FORCER LE RECHARGEMENT depuis la base de données
        self.refresh_from_db()
        
        print(f"💰 Article {self.id} - Prix sauvegardé: {self.prix_total}€")
        return self.prix_total

    def calculate_base_price(self):
        """Calcule le prix unitaire de base avec toutes les options et suppléments"""
        if self.menu:
            prix_base = self.menu.prix_ttc
            
            # 🆕 CORRECTION : AJOUTER LES SUPPLÉMENTS SAUVEGARDÉS
            if hasattr(self, 'supplements_menu') and self.supplements_menu and self.supplements_menu.get('total_supplements'):
                try:
                    supplement_total = Decimal(str(self.supplements_menu['total_supplements']))
                    prix_base += supplement_total
                    print(f"🔍 Menu {self.menu.nom} - Prix base: {self.menu.prix_ttc}€ + Suppléments: {supplement_total}€ = {prix_base}€")
                except (ValueError, TypeError) as e:
                    print(f"❌ Erreur calcul supplément menu: {e}")
            
            return prix_base
            
        elif self.plat:
            prix_total = self.plat.prix_unitaire_ttc
            
            # Ajouter le prix des options classiques
            for option in self.options.all():
                prix_total += option.prix_unitaire_ttc
            
            # Ajouter le prix des options Crousty
            for option_crousty in self.options_crousty.all():
                prix_total += option_crousty.prix_supplement
            
            # 🆕 MODIFICATION : CALCUL AVEC QUANTITÉS POUR OPTIONS POULET
            if hasattr(self, 'options_poulet_avec_quantites') and self.options_poulet_avec_quantites:
                from collections import Counter
                options_counter = Counter(self.options_poulet_avec_quantites)
                for option_id, quantite in options_counter.items():
                    try:
                        option = PouletOption.objects.get(id=option_id)
                        prix_total += option.prix_supplement * quantite
                    except PouletOption.DoesNotExist:
                        continue
            else:
                # Fallback à l'ancienne méthode
                for option_poulet in self.options_poulet.all():
                    prix_total += option_poulet.prix_supplement
            
            # 🆕 AJOUTER LE PRIX DE L'ACCOMPAGNEMENT
            if self.accompagnement:
                prix_total += self.accompagnement.prix_supplement
            
            return prix_total
            
        elif self.salade_personnalisee:
            return self.salade_personnalisee.prix_total or self.salade_personnalisee.calculate_prix_total()
            
        elif self.couscous_personnalise:
            return self.couscous_personnalise.prix_total or self.couscous_personnalise.calculate_prix_total()
            
        else:
            return Decimal('0.00')

class ChoixMenuArticle(models.Model):
    article_panier = models.ForeignKey(ArticlePanier, on_delete=models.CASCADE, related_name='choix_menu')
    role = models.CharField(max_length=20, choices=ComposantMenuFixe.ROLE_CHOICES)

    plat_choisi = models.ForeignKey(Plat, on_delete=models.SET_NULL, null=True, blank=True)
    salade = models.ForeignKey(SaladePersonnalisee, on_delete=models.SET_NULL, null=True, blank=True)
    couscous = models.ForeignKey(CouscousPersonnalise, on_delete=models.SET_NULL, null=True, blank=True)
    info_text = models.CharField("Texte libre/affichage", max_length=200, null=True, blank=True)


    def __str__(self):
        nom = (
            self.plat_choisi.nom if self.plat_choisi else
            "Salade personnalisée" if self.salade else
            "Couscous personnalisé" if self.couscous else
            "Non renseigné"
        )
        return f"{self.article_panier.menu.nom} - {self.get_role_display()} : {nom}"

from django.db import models
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class MoyenPaiement(models.TextChoices):
    STRIPE = 'stripe', 'Stripe (en ligne)'
    ESPECE_LIVRAISON = 'especes_livraison', 'Espèces à la livraison'
    TICKET_LIVRAISON = 'ticket_livraison', 'Ticket resto à la livraison'
    ESPECE_RETRAIT = 'especes_retrait', 'Espèces au retrait'
    TICKET_RETRAIT = 'ticket_retrait', 'Ticket resto au retrait'


class Commande(models.Model):
    session_key = models.CharField(max_length=100, null=True, blank=True)
    heure_creation = models.DateTimeField(auto_now_add=True)
    panier = models.OneToOneField('Panier', null=True, blank=True, on_delete=models.SET_NULL, related_name='commande_associee')
    client = models.ForeignKey('Client', null=True, blank=True, on_delete=models.SET_NULL)
    societe = models.CharField(max_length=120, blank=True, null=True)
    adresse_facturation_saisie = models.TextField(blank=True, null=True)
    facture_sans_detail = models.BooleanField(default=False)
    adresse_livraison = models.ForeignKey('AdresseLivraison', on_delete=models.SET_NULL, null=True)
    nom_saisi = models.CharField(max_length=100, blank=True, null=True)
    prenom_saisi = models.CharField(max_length=100, blank=True, null=True)
    telephone_saisi = models.CharField(max_length=15, blank=True, null=True)
    email_saisi = models.EmailField(blank=True, null=True)
    date_livraison_specifiee = models.DateField(null=True, blank=True)
    heure_livraison_specifiee = models.TimeField(null=True, blank=True)
    heure_livraison_asap = models.DateTimeField(null=True, blank=True)

    horaire_verrouille = models.BooleanField(default=False, help_text="Empêche la modification automatique de l’horaire une fois la commande confirmée")

    message_pour_chef = models.TextField("Message pour le chef", blank=True, null=True)
    message_pour_livreur = models.TextField("Message pour le livreur", blank=True, null=True)

    # Statuts
    is_commande_a_emporter = models.BooleanField(default=False)
    heure_commande_a_emporter = models.DateTimeField(null=True, blank=True)

    commande_is_valid = models.BooleanField(default=False, help_text="Commande validée manuellement (paiement en main propre)")


    is_paid = models.BooleanField(default=False)
    heure_paiement = models.DateTimeField(null=True, blank=True)
    moyen_paiement = models.CharField(
            max_length=30,
            choices=MoyenPaiement.choices,
            null=True,
            blank=True,
            help_text="Méthode de paiement choisie (non utilisé en cas de mixte)"
        )

        # Paiement mixte
    montant_especes = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    montant_ticket = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    montant_stripe = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    is_on_tour = models.BooleanField(default=False)
    is_in_the_kitchen = models.BooleanField(default=False)
    heure_in_the_kitchen = models.DateTimeField(null=True, blank=True)
    cuisson_en_cours = models.BooleanField(default=False)
    heure_cuisson_en_cours = models.DateTimeField(null=True, blank=True)
    is_cooked = models.BooleanField(default=False)
    heure_cooked = models.DateTimeField(null=True, blank=True)

    # Livraison
    is_ready_to_ship = models.BooleanField(default=False)
    heure_ready_to_ship = models.DateTimeField(null=True, blank=True)
    is_shipped = models.BooleanField(default=False)
    heure_shipped = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    heure_delivered = models.DateTimeField(null=True, blank=True)

    # À emporter
    heure_pick_up_specifie = models.DateTimeField(null=True, blank=True)
    is_ready_to_pick = models.BooleanField(default=False)
    heure_ready_to_pick = models.DateTimeField(null=True, blank=True)
    is_picked = models.BooleanField(default=False)
    heure_picked = models.DateTimeField(null=True, blank=True)

    # Bar
    is_ok_bar = models.BooleanField(default=False)
    heure_ok_bar = models.DateTimeField(null=True, blank=True)


    @classmethod
    def commandes_a_afficher_sur_la_carte(cls):
        maintenant = timezone.now()
        delai = timedelta(minutes=60)
        return cls.objects.filter(is_paid=False, heure_creation__gte=maintenant - delai)

    def __str__(self):
        return f"Commande {self.id} - Client: {self.client}"

    def update_status(self, status_field, time_field):
        if getattr(self, status_field):
            logging.warning(f"Commande {self.id} est déjà {status_field}.")
            return
        setattr(self, status_field, True)
        setattr(self, time_field, timezone.now())
        self.save(update_fields=[status_field, time_field])
        logging.info(f"Commande {self.id} mise à jour : {status_field} à {getattr(self, time_field)}")

    def set_paiement(self, moyen: str):
        if self.is_paid:
            logger.warning(f"Commande {self.id} déjà payée.")
            return
        if moyen not in dict(MoyenPaiement.choices):
            raise ValueError(f"Moyen de paiement invalide : {moyen}")
        self.moyen_paiement = moyen
        self.update_status('is_paid', 'heure_paiement')
        
    def set_in_the_kitchen(self):
        logger.debug(f"[CUISINE] Commande {self.pk} → is_in_the_kitchen = True")
        self.is_in_the_kitchen = True
        self.heure_in_the_kitchen = timezone.now()
        self.save(update_fields=['is_in_the_kitchen', 'heure_in_the_kitchen'])
    
    def set_cuisson_en_cours(self):
        if not self.cuisson_en_cours:
            self.cuisson_en_cours = True
            self.heure_cuisson_en_cours = timezone.now()
            self.save(update_fields=['cuisson_en_cours', 'heure_cuisson_en_cours'])


    def set_cooked(self):
        self.update_status('is_cooked', 'heure_cooked')
        self.check_ready()

    def set_ready_to_ship(self):
        self.update_status('is_ready_to_ship', 'heure_ready_to_ship')

    def set_shipped(self):
        self.update_status('is_shipped', 'heure_shipped')

    def set_delivered(self):
        self.update_status('is_delivered', 'heure_delivered')

    def set_ok_bar(self):
        self.update_status('is_ok_bar', 'heure_ok_bar')
        self.check_ready()

    def set_ready_to_pick(self):
        self.update_status('is_ready_to_pick', 'heure_ready_to_pick')

    def set_picked(self):
        self.update_status('is_picked', 'heure_picked')

    def check_ready(self):
        if self.is_commande_a_emporter:
            if self.is_cooked and self.is_ok_bar and not self.is_ready_to_pick:
                self.set_ready_to_pick()
                logger.info(f"Commande {self.id} prête à être enlevée.")
        else:
            if self.is_cooked and self.is_ok_bar and not self.is_ready_to_ship:
                self.set_ready_to_ship()
                logger.info(f"Commande {self.id} prête à être expédiée.")

    def set_livraison_asap(self):
        if not self.adresse_livraison:
            logger.error(f"Adresse de livraison manquante pour la commande {self.id}")
            return
        delai = timedelta(minutes=self.adresse_livraison.delai_livraison_estime)
        self.heure_livraison_asap = timezone.now() + delai
        self.save(update_fields=['heure_livraison_asap'])
        logger.info(f"Heure de livraison ASAP définie pour la commande {self.id} : {self.heure_livraison_asap}")

    def calculate_prix_total(self):
        if not self.panier:
            return 0
        return self.panier.prix_total if self.is_paid else self.panier.calculate_total_price()

    def deduire_ingredients(self):
        try:
            for article in self.panier.articlepanier_set.all():
                plat = article.plat
                quantite_article = article.quantite
                for cuisson in plat.cuissons.all():
                    ingredient = cuisson.ingredient
                    quantite_necessaire = cuisson.quantite * quantite_article
                    if ingredient.quantite_stock >= quantite_necessaire:
                        ingredient.quantite_stock -= quantite_necessaire
                        ingredient.save()
                    else:
                        raise Exception(f"Stock insuffisant pour {ingredient.nom}")
                for option in article.options.all():
                    for cuisson in option.cuissons.all():
                        ingredient = cuisson.ingredient
                        quantite_necessaire = cuisson.quantite * quantite_article
                        if ingredient.quantite_stock >= quantite_necessaire:
                            ingredient.quantite_stock -= quantite_necessaire
                            ingredient.save()
                        else:
                            raise Exception(f"Stock insuffisant pour {ingredient.nom}")
        except Exception as e:
            self.is_paid = False
            self.save()
            logger.error(f"Erreur lors de la déduction des ingrédients : {e}")
            raise e

    def verifier_disponibilite_plats(self):
        from .models import Plat
        for plat in Plat.objects.all():
            plat.verifier_disponibilite()

    def set_paiement(self, moyen: str):
            if self.is_paid:
                logger.warning(f"Commande {self.id} déjà payée.")
                return
            if moyen not in dict(MoyenPaiement.choices):
                raise ValueError(f"Moyen de paiement invalide : {moyen}")
            self.moyen_paiement = moyen
            self.update_status('is_paid', 'heure_paiement')

    def set_paiement_mixte(self, montant_especes, montant_ticket, montant_stripe):
        montant_especes = montant_especes or 0
        montant_ticket = montant_ticket or 0
        montant_stripe = montant_stripe or 0

        total_mixte = montant_especes + montant_ticket + montant_stripe
        total_commande = self.calculate_prix_total()

        if total_mixte < total_commande:
            raise ValueError("Total du paiement insuffisant.")
        if total_mixte > total_commande:
            raise ValueError("Le total du paiement dépasse le montant de la commande.")

        self.montant_especes = montant_especes
        self.montant_ticket = montant_ticket
        self.montant_stripe = montant_stripe
        self.moyen_paiement = 'mixte'
        self.update_status('is_paid', 'heure_paiement')

    def get_resume_paiement(self):
            if self.montant_especes or self.montant_ticket or self.montant_stripe:
                return f"Mixte: {self.montant_especes or 0}€ espèces, {self.montant_ticket or 0}€ ticket, {self.montant_stripe or 0}€ stripe"
            return self.get_moyen_paiement_display() or "Non payé"

    def save(self, *args, **kwargs):
        print(f"[DEBUG] save() called on Commande {self.pk}")
        print(f"[DEBUG] is_commande_a_emporter={self.is_commande_a_emporter}")
        print(f"[DEBUG] commande_is_valid={self.commande_is_valid}")
        print(f"[DEBUG] is_in_the_kitchen={self.is_in_the_kitchen}")

        super().save(*args, **kwargs)

        if (
            self.is_commande_a_emporter and
            self.commande_is_valid and
            not self.is_in_the_kitchen
        ):
            print("[DEBUG] -> Entrée en cuisine déclenchée")
            self.set_in_the_kitchen()



    def get_statut(self):
        if self.is_commande_a_emporter:
            if self.is_picked:
                return "Récupérée"
            elif self.is_ready_to_pick:
                return "Prête à être enlevée"
        else:
            if self.is_delivered:
                return "Livrée"
            elif self.is_shipped:
                return "Expédiée"
            elif self.is_ready_to_ship:
                return "Prête à être expédiée"
            elif self.is_on_tour:
                return "En tournée"
        
        if self.is_cooked:
            return "Cuisson terminée"
        elif self.is_in_the_kitchen:
            return "En cuisine"
        
        return "En attente"




# Modèle Livreur
class Livreur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    au_travaille = models.BooleanField(default=False)
    is_booked = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.nom

# Modèle Tournee
class Tournee(models.Model):
    nom = models.PositiveIntegerField()
    id_tournee = models.CharField(max_length=14, unique=True)
    date_tournee = models.DateField(default=timezone.now)
    livreur = models.ForeignKey('Livreur', on_delete=models.SET_NULL, null=True, blank=True)
    heure_depart = models.DateTimeField(null=True, blank=True)
    heure_retour_estime = models.DateTimeField(null=True, blank=True)
    heure_retour_reel = models.DateTimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    heure_cloture = models.DateTimeField(null=True, blank=True)
    is_ready_for_delivery = models.BooleanField(default=False)
    is_sent_livreur = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_figee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('nom', 'date_tournee')

    def __str__(self):
        return f"Tournée {self.nom} - {self.date_tournee}"

    def save(self, *args, **kwargs):
        if self.is_ready_for_delivery and self.livreur and not self.is_sent_livreur:
            self.is_sent_livreur = True
        super().save(*args, **kwargs)

    @classmethod
    def generer_numero_tournee(cls):
        aujourd_hui = date.today()
        date_str = aujourd_hui.strftime('%y%m%d')
        nombre_de_tournees = cls.objects.filter(date_tournee=aujourd_hui).count() + 1
        return f"{date_str}{nombre_de_tournees:02d}"

    @classmethod
    def verifier_tournee_non_terminee(cls, nom_tournee):
        return cls.objects.filter(nom=nom_tournee, is_done=False).exists()

    def mark_as_ready_for_delivery(self):
        self.is_ready_for_delivery = True
        self.save(update_fields=['is_ready_for_delivery'])
        logging.info(f"Tournée {self.nom} est prête pour la livraison.")

    def check_and_mark_ready_for_delivery(self):
        all_ready = all(tc.commande.is_ready_to_ship for tc in self.tourneecommande_set.all())
        if all_ready and not self.is_ready_for_delivery:
            self.mark_as_ready_for_delivery()

# Modèle TourneeCommande
class TourneeCommande(models.Model):
    tournee = models.ForeignKey(Tournee, on_delete=models.CASCADE)
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    ordre = models.PositiveIntegerField(default=0)
    heure_passage = models.DateTimeField(null=True, blank=True)  # <-- Correction ici
    duree_trajet = models.PositiveIntegerField(null=True, blank=True, help_text="Temps de trajet en secondes depuis la commande précédente")

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"Commande {self.commande.id} dans la tournée {self.tournee.nom} (ordre {self.ordre})"


class MouvementStock(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='mouvements_stock'
    )
    date = models.DateTimeField(default=timezone.now)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.ingredient.nom} - {self.quantity} {self.ingredient.get_unite_stock_display()} à {self.price_per_unit} € le {self.date.strftime('%d/%m/%Y %H:%M')}"




class Facture(models.Model):
    numero = models.CharField(max_length=30, unique=True)
    commande = models.OneToOneField('Commande', on_delete=models.CASCADE, related_name='facture')
    client = models.ForeignKey('Client', on_delete=models.PROTECT, related_name='factures')
    date_emission = models.DateTimeField(default=timezone.now)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    tva_par_taux = models.JSONField(null=True, blank=True, default=dict)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    deja_reglee = models.BooleanField(default=False)
    societe = models.CharField(max_length=120, blank=True, null=True)
    adresse_facturation = models.TextField(blank=True)
    facture_sans_detail = models.BooleanField(default=False)


    def __str__(self):
        return f"Facture {self.numero} (Commande {self.commande.id})"

class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=255)
    quantite = models.PositiveIntegerField()
    prix_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=1, choices=TAUX_TVA_CHOICES)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} (x{self.quantite})"
    


class IngredientSaladeTag(models.Model):
    ingredient = models.OneToOneField('Ingredient', on_delete=models.CASCADE, related_name='salade_tag')
    type_salade = models.CharField(
        max_length=20,
        choices=[
            ('base', 'Base'),
            ('proteine', 'Protéine'),
            ('garniture', 'Garniture'),
            ('topping', 'Topping'),
            ('sauce', 'Sauce'),
        ]
    )

    def __str__(self):
        return f"{self.ingredient.nom} → {self.get_type_salade_display()}"


from decimal import Decimal
from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Recette(TranslatableModel):
    """
    Recette de fabrication d'un ProduitTransforme (ex: 12 buns).
    """
    produit = models.OneToOneField(
        'ProduitTransforme',
        on_delete=models.CASCADE,
        related_name='recette',
        help_text="Produit fabriqué par cette recette"
    )

    translations = TranslatedFields(
        nom=models.CharField(max_length=120),
        instructions_globales=models.TextField(blank=True),
    )

    portions = models.PositiveIntegerField(default=1, help_text="Nombre d'unités obtenues (ex: 12 buns)")
    temperature_cuisson = models.PositiveIntegerField(null=True, blank=True, help_text="°C")
    duree_cuisson_minutes = models.PositiveIntegerField(null=True, blank=True)

    prix_revient_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    prix_revient_unitaire_ttc = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    coefficient_vente = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            help_text="x TTC (ex: 4.50)")

    def __str__(self):
        return f"Recette {self.safe_translation_getter('nom', any_language=True)} → {self.produit.nom}"

    # ---------- Utilitaires ----------
    def _facteur(self, quantite_produite: int) -> Decimal:
        return (Decimal(quantite_produite) / Decimal(max(self.portions, 1)))

    def ingredients_totaux(self, quantite_produite=1):
        f = self._facteur(quantite_produite)
        out = []
        for ri in self.ingredients.all():
            out.append({
                "ingredient": ri.ingredient,
                "quantite": (ri.quantite * f).quantize(Decimal("0.01")),
                "unite": ri.unite
            })
        return out

    def deduire_du_stock(self, quantite_produite=1):
        for item in self.ingredients_totaux(quantite_produite):
            ingr = item["ingredient"]
            q = item["quantite"]
            if ingr.quantite_stock < q:
                raise ValueError(f"Stock insuffisant pour {ingr.nom} ({ingr.quantite_stock} < {q})")
            ingr.quantite_stock -= q
            ingr.save()

        self.produit.quantite_disponible += int(quantite_produite)
        self.produit.save()

class RecetteIngredient(models.Model):
    UNITE_CHOICES = [('g', 'grammes'), ('l', 'litres'), ('u', 'unités')]

    recette = models.ForeignKey('Recette', on_delete=models.CASCADE, related_name='ingredients')
    
    # Soit un ingrédient brut, soit un produit transformé
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE, null=True, blank=True)
    produit_transforme = models.ForeignKey('ProduitTransforme', on_delete=models.CASCADE, null=True, blank=True)
    
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES)

    class Meta:
        unique_together = ('recette', 'ingredient', 'produit_transforme')

    def clean(self):
        if not self.ingredient and not self.produit_transforme:
            raise ValidationError("Un ingrédient ou un produit transformé doit être spécifié.")
        if self.ingredient and self.produit_transforme:
            raise ValidationError("Uniquement un ingrédient ou un produit transformé peut être spécifié, pas les deux.")

    def __str__(self):
        nom = self.ingredient.nom if self.ingredient else self.produit_transforme.nom
        return f"{self.quantite} {self.unite} de {nom} ({self.recette.safe_translation_getter('nom')})"


class EtapeRecette(TranslatableModel):
    """
    Étapes détaillées de la recette (procédé de fabrication).
    """
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="etapes")
    ordre = models.PositiveIntegerField()

    translations = TranslatedFields(
        titre=models.CharField(max_length=120, blank=True),
        description=models.TextField(),
    )

    duree_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["ordre"]
        verbose_name = "Étape de recette"
        verbose_name_plural = "Étapes de recettes"

    def __str__(self):
        titre = f" – {self.safe_translation_getter('titre')}" if self.safe_translation_getter('titre') else ""
        return f"Étape {self.ordre}{titre} ({self.recette.safe_translation_getter('nom')})"


class LimiteOptionsPoulet(models.Model):
    CATEGORIE_CHOICES = [
        ('assaisonnement', 'Assaisonnement'),
        ('accompagnement', 'Accompagnement'),
        ('sauce', 'Sauce'),
        ('supplement', 'Supplément'),
    ]
    
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='limites_poulet')
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    limite_selection = models.PositiveIntegerField(default=1)
    est_obligatoire = models.BooleanField(default=True, help_text="L'utilisateur doit-il sélectionner au moins une option?")
    
    class Meta:
        unique_together = ['plat', 'categorie']
        verbose_name = "Limite d'options Poulet"
        verbose_name_plural = "Limites d'options Poulet"
    
    def __str__(self):
        obligatoire = " (obligatoire)" if self.est_obligatoire else " (optionnel)"
        return f"{self.plat.nom} - {self.categorie}: {self.limite_selection}{obligatoire}"
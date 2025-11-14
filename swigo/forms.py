from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Commande, VilleDesservie, CodePromo, AccompagnementCouscous

### Formulaire de commande ###
class CommandeForm(forms.ModelForm):
    CHOIX_LIVRAISON = [
        ('le_plus_tot', 'Le plus tôt possible'),
        ('choisir_date', 'Choisir une date et une heure'),
    ]

    choix_livraison = forms.ChoiceField(choices=CHOIX_LIVRAISON, widget=forms.RadioSelect)
    date_livraison = forms.DateField(required=False, widget=forms.SelectDateWidget)
    heure_livraison = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M'))

    class Meta:
        model = Commande
        fields = [
            'adresse_livraison', 
            'choix_livraison', 
            'date_livraison', 
            'heure_livraison'
        ]

### Formulaire pour l'adresse de livraison ###
from django import forms

class AdresseLivraisonForm(forms.Form):
    adresse_livraison = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}))
    code_postal = forms.CharField(max_length=10)
    ville = forms.CharField(max_length=100)
    localisation = forms.CharField(max_length=20, required=False)  # Localisation facultative
    latitude = forms.FloatField(widget=forms.HiddenInput())  # Champ caché pour latitude
    longitude = forms.FloatField(widget=forms.HiddenInput())  # Champ caché pour longitude

    def clean_ville(self):
        ville = self.cleaned_data.get('ville')
        if not VilleDesservie.objects.filter(ville__iexact=ville).exists():
            raise forms.ValidationError('Désolé, nous ne livrons pas dans cette zone.')
        return ville


### Formulaire pour choisir la date et l'heure de livraison ###
class DateTimeDeliveryForm(forms.Form):
    date_livraison = forms.DateField(
        widget=forms.SelectDateWidget(years=range(timezone.localdate().year, timezone.localdate().year + 5)),
        input_formats=['%Y-%m-%d']  # Format explicite de la date
    )
    heure_livraison = forms.TimeField(
        input_formats=['%H:%M'],  # Format explicite de l'heure
        widget=forms.TimeInput(format='%H:%M')
    )

    def clean_date_livraison(self):
        date = self.cleaned_data.get('date_livraison')
        if not date:
            raise ValidationError('La date est requise.')
        
        today = timezone.localdate()  # Obtenir la date actuelle
        if date < today:
            raise ValidationError('La date de livraison ne peut pas être dans le passé.')
        
        return date

    def clean_heure_livraison(self):
        heure = self.cleaned_data.get('heure_livraison')
        if not heure:
            raise ValidationError('L\'heure est requise.')

        debut_midi = timezone.datetime.strptime('11:30', '%H:%M').time()
        fin_soir = timezone.datetime.strptime('22:30', '%H:%M').time()

        if heure < debut_midi or heure > fin_soir:
            raise ValidationError('L\'heure de livraison doit être comprise entre 12:00 et 22:00.')
        
        return heure

### Formulaire pour les codes promo ###
class CodePromoForm(forms.Form):
    code_promo = forms.CharField(max_length=20, required=False, label='Code Promo')

    def clean_code_promo(self):
        code_promo = self.cleaned_data.get('code_promo')
        if code_promo:
            try:
                promo = CodePromo.objects.get(code=code_promo)
                if not promo.est_valide():
                    raise forms.ValidationError('Ce code promo n\'est plus valide.')
            except CodePromo.DoesNotExist:
                raise forms.ValidationError('Ce code promo est invalide.')
        return code_promo


from django import forms
from .models import Tournee, Commande

class AttribuerCommandeTourneeForm(forms.Form):
    # Afficher les tournées existantes (non clôturées) dans un menu déroulant
    tournee_existante = forms.ModelChoiceField(
        queryset=Tournee.objects.filter(is_closed=False), 
        required=False, 
        label="Attribuer à une tournée existante"
    )
    
    # Possibilité de créer une nouvelle tournée avec les noms A-E
    NOUVELLE_TOURNEE_CHOICES = [
        ('A', 'Tournée A'),
        ('B', 'Tournée B'),
        ('C', 'Tournée C'),
        ('D', 'Tournée D'),
        ('E', 'Tournée E'),
    ]
    
    nouvelle_tournee = forms.ChoiceField(
        choices=NOUVELLE_TOURNEE_CHOICES,
        required=False,
        label="Créer une nouvelle tournée"
    )
    
    # Champ pour la commande concernée
    commande = forms.ModelChoiceField(
        queryset=Commande.objects.filter(is_paid=True, is_on_tour=False),
        required=True,
        label="Sélectionnez la commande"
    )


from django import forms

from django import forms

import logging
from django import forms

logger = logging.getLogger(__name__)

class SaladePersonnaliseeForm(forms.Form):
    base = forms.MultipleChoiceField(
        choices=[
            ('Salade de saison', 'Salade de saison'),
            ('Quinoa', 'Quinoa'),
            ('Mix Quinoa / Salade de saison', 'Mix Quinoa / Salade de saison'),
            ('Semoule', 'Semoule'),
            ('Mix Semoule / Salade de saison', 'Mix Semoule / Salade de saison'),
            ('Riz vinaigré', 'Riz vinaigré'),
            ('Mix Riz vinaigré / Salade de saison', 'Mix Riz vinaigré / Salade de saison'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    proteine = forms.MultipleChoiceField(
        choices=[
            ('Pavé de Saumon', 'Pavé de Saumon'),
            ('Pavé de Thon', 'Pavé de Thon'),
            ('Filet de poisson pané', 'Filet de poisson pané'),
            ('Poulet Braisé', 'Poulet Braisé'),
            ('Poulet Pané', 'Poulet Pané'),
            ('Agneau confit', 'Agneau confit'),
            ('Agneau grillé', 'Agneau grillé'),
            ('Merguez', 'Merguez'),
            ('Brochette de viande hachée charolaise', 'Brochette de viande hachée charolaise'),
            ('Boulette de viande charolaise', 'Boulette de viande charolaise'),
            ('Œuf', 'Œuf'),
            ('Steak végétal', 'Steak végétal'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    garnitures = forms.MultipleChoiceField(
        choices=[
            ('Oeuf', 'Oeuf'),
            ('Courgettes râpées', 'Courgettes râpées'),
            ('Champignons de Paris', 'Champignons de Paris'),
            ('Chou rouge', 'Chou rouge'),
            ('Edamame', 'Edamame'),
            ('Maïs', 'Maïs'),
            ('Oignons rouges', 'Oignons rouges'),
            ('Poivrons', 'Poivrons'),
            ('Carottes râpées', 'Carottes râpées'),
            ('Chou blanc', 'Chou blanc'),
            ('Concombre', 'Concombre'),
            ('Olives noires', 'Olives noires'),
            ('Olives vertes', 'Olives vertes'),
            ('Radis', 'Radis'),
            ('Tomates cerises', 'Tomates cerises'),
            ('Tomates séchées', 'Tomates séchées'),
            ('Aubergines marinées', 'Aubergines marinées'),
            ('Avocat', 'Avocat'),
            ('Pois chiches', 'Pois chiches'),
            ('Quinoa', 'Quinoa'),
            ('Ananas', 'Ananas'),
            ('Mangue', 'Mangue'),
            ('Pruneaux', 'Pruneaux'),
            ('Raisins secs', 'Raisins secs'),
            ('Abricots secs', 'Abricots secs'),
            ('Galette de Pomme de Terre Rosti Maison', 'Galette de Pomme de Terre Rosti Maison'),
            ('Cornichon croquant', 'Cornichon croquant'),
            ('Ratatouille provençale', 'Ratatouille provençale'),
            ('Câpres', 'Câpres'),
            ('Onion rings', 'Onion rings'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    toppings = forms.MultipleChoiceField(
        choices=[
            ('Oignons frits', 'Oignons frits'),
            ('Menthe fraîche', 'Menthe fraîche'),
            ('Coriandre fraîche', 'Coriandre fraîche'),
            ('Ciboulette fraîche', 'Ciboulette fraîche'),
            ('Basilic frais', 'Basilic frais'),
            ('Amandes grillées', 'Amandes grillées'),
            ('Cacahuètes grillées', 'Cacahuètes grillées'),
            ('Mélange de graines (chia-courge-lin-sésame)', 'Mélange de graines (chia-courge-lin-sésame)'),
            ('Pignons de pin', 'Pignons de pin'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    sauce = forms.MultipleChoiceField(
        choices=[
            ('Sauce miel-moutarde', 'Sauce miel-moutarde'),
            ('Sauce crème fraîche et aneth', 'Sauce crème fraîche et aneth'),
            ('Sauce vinaigrette iba', 'Sauce vinaigrette iba'),
            ('Sauce pesto', 'Sauce pesto'),
            ('Sauce soja salé et sésame', 'Sauce soja salé et sésame'),
            ('Sauce soja sucré', 'Sauce soja sucré'),
            ('Sauce tartare', 'Sauce tartare'),
            ('Sauce barbecue', 'Sauce barbecue'),
            ('Sauce sweet chili', 'Sauce sweet chili'),
            ('Huile d\'olive extra et balsamique', 'Huile d\'olive extra et balsamique'),
        ],
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        logger.debug("Entrée dans clean() du formulaire SaladePersonnaliseeForm")
        cleaned_data = super().clean()

        base = cleaned_data.get('base', [])
        proteine = cleaned_data.get('proteine', [])
        garnitures = cleaned_data.get('garnitures', [])
        toppings = cleaned_data.get('toppings', [])
        sauce = cleaned_data.get('sauce', [])

        # Ajouter des print pour débug
        print("Valeurs sélectionnées - base:", base)
        print("Valeurs sélectionnées - proteine:", proteine)
        print("Valeurs sélectionnées - garnitures:", garnitures)
        print("Valeurs sélectionnées - toppings:", toppings)
        print("Valeurs sélectionnées - sauce:", sauce)

        logger.debug(f"Valeurs du formulaire: base={base}, proteine={proteine}, garnitures={garnitures}, toppings={toppings}, sauce={sauce}")

        # Vérification du nombre exact d'options
        if len(base) != 1:
            msg = "Vous devez choisir exactement 1 base."
            self.add_error('base', msg)
            print("Erreur base:", msg)
            logger.debug(f"Erreur base: {msg}")

        if len(proteine) != 1:
            msg = "Vous devez choisir exactement 1 protéine."
            self.add_error('proteine', msg)
            print("Erreur proteine:", msg)
            logger.debug(f"Erreur proteine: {msg}")

        if len(garnitures) != 5:
            msg = "Vous devez choisir exactement 5 garnitures."
            self.add_error('garnitures', msg)
            print("Erreur garnitures:", msg)
            logger.debug(f"Erreur garnitures: {msg}")

        if len(toppings) != 2:
            msg = "Vous devez choisir exactement 2 toppings."
            self.add_error('toppings', msg)
            print("Erreur toppings:", msg)
            logger.debug(f"Erreur toppings: {msg}")

        if len(sauce) != 1:
            msg = "Vous devez choisir exactement 1 sauce."
            self.add_error('sauce', msg)
            print("Erreur sauce:", msg)
            logger.debug(f"Erreur sauce: {msg}")

        return cleaned_data


class PickUpTimeForm(forms.Form):
    heure_retrait = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M'],
        label="Choisir une heure"
    )


from django import forms
from .models import FormuleCouscous, ViandeCouscous

class CouscousPersonnaliseForm(forms.Form):
    formule = forms.ModelChoiceField(
        queryset=FormuleCouscous.objects.all(),
        required=True,
        widget=forms.RadioSelect
    )

    viandes_inclues = forms.ModelMultipleChoiceField(
        queryset=ViandeCouscous.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    viandes_supplement = forms.ModelMultipleChoiceField(
        queryset=ViandeCouscous.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    accompagnements = forms.ModelMultipleChoiceField(
        queryset=AccompagnementCouscous.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Accompagnements"
    )

    option_xl = forms.BooleanField(required=False, label='Option XL (+2,00 €)')

    def clean(self):
        cleaned_data = super().clean()
        formule = cleaned_data.get("formule")
        viandes_inclues = cleaned_data.get("viandes_inclues")

        if formule and viandes_inclues and len(viandes_inclues) > formule.nombre_viandes_incluses:
            self.add_error("viandes_inclues", f"Maximum {formule.nombre_viandes_incluses} viandes incluses.")

        return cleaned_data

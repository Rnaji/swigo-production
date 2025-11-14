import random
import requests
import logging
from django.core.management.base import BaseCommand
from swigo.models import Commande, Client, AdresseLivraison, VilleDesservie, Plat, Option, Panier, ArticlePanier

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "AIzaSyChxLP7_um9XUuGA3rHlUPTQuB7SRFuSNk"

def get_autocomplete_suggestions(ville, code_postal):
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    query = f"mairie {ville} {code_postal}, France"
    params = {"input": query, "types": "establishment", "key": API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        predictions = response.json().get("predictions")
        if predictions:
            logger.info(f"Place ID trouvé pour {ville}: {predictions[0]['place_id']}")
            return predictions[0]['place_id']
        else:
            logger.warning(f"Aucune suggestion pour {ville} {code_postal}")
    except requests.RequestException as e:
        logger.error(f"Erreur Autocomplete pour {ville}: {e}")
    return None

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "key": API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json().get("result")
        if result:
            full_address = result["formatted_address"]
            lat = result["geometry"]["location"]["lat"]
            lng = result["geometry"]["location"]["lng"]
            logger.info(f"Adresse trouvée: {full_address}")

            # ➕ Extraction de la "rue seule"
            street_part = full_address.split(",")[0]  # "21 Rue du Clos de l'Abbaye"
            return street_part, lat, lng
    except requests.RequestException as e:
        logger.error(f"Erreur Details: {e}")
    return None, None, None


def generer_adresse(client):
    villes = VilleDesservie.objects.all()
    ville = random.choice(villes)
    logger.info(f"Recherche mairie de {ville.ville} {ville.code_postal}")
    place_id = get_autocomplete_suggestions(ville.ville, ville.code_postal)

    if place_id:
        adresse, lat, lng = get_place_details(place_id)
        if adresse and lat and lng:
            adr, _ = AdresseLivraison.objects.get_or_create(
                adresse=adresse,
                code_postal=ville.code_postal,
                ville=ville.ville,
                zone=ville.zone,
                localisation=ville.localisation,
                defaults={'latitude': lat, 'longitude': lng}
            )
            return adr

    fallback = f"Centre-ville de {ville.ville}"
    adr, _ = AdresseLivraison.objects.get_or_create(
        adresse=fallback,
        code_postal=ville.code_postal,
        ville=ville.ville,
        zone=ville.zone,
        localisation=ville.localisation
    )
    return adr

def generer_client():
    noms = ['Dupont', 'Martin', 'Bernard', 'Petit', 'Durand']
    prenoms = ['Jean', 'Pierre', 'Luc', 'Sophie', 'Marie']
    nom = random.choice(noms)
    prenom = random.choice(prenoms)
    tel = f"06{random.randint(10000000, 99999999)}"
    email = f"{prenom.lower()}.{nom.lower()}@exemple.com"

    return Client.objects.create(
        nom=nom,
        prenom=prenom,
        numero_telephone=tel,
        email=email,
        adresse_facturation=f"{random.randint(1, 100)} Rue de Paris"
    )

def ajouter_au_panier(panier, plat, quantite, options):
    existants = ArticlePanier.objects.filter(panier=panier, plat=plat)
    for art in existants:
        if set(art.options.all()) == set(options):
            art.quantite += quantite
            art.calculate_total_price()
            art.save()
            return art

    nouvel_article = ArticlePanier.objects.create(
        panier=panier,
        plat=plat,
        quantite=quantite,
        prix_total=0
    )
    nouvel_article.options.set(options)
    nouvel_article.calculate_total_price()
    nouvel_article.save()
    return nouvel_article

from django.utils import timezone
from datetime import timedelta, time

def generer_commande(force_type=None):
    client = generer_client()
    panier = Panier.objects.create(session_key=f"session_{random.randint(1000, 9999)}")

    plats = Plat.objects.all()
    for _ in range(random.randint(1, 3)):
        plat = random.choice(plats)
        options = Option.objects.filter(plat=plat)
        selection = random.sample(list(options), random.randint(0, len(options)))
        quantite = random.randint(1, 3)
        ajouter_au_panier(panier, plat, quantite, selection)

    panier.calculate_total_price()

    now = timezone.now()

    # Déterminer le type
    if force_type == "emporter":
        is_emporter = True
        moyen_paiement = random.choice(['especes_retrait', 'ticket_retrait'])
        is_paid = False
        commande_is_valid = False
        heure_retrait = now + timedelta(minutes=random.randint(10, 60))
        commande = Commande.objects.create(
            client=client,
            adresse_livraison=generer_adresse(client),
            panier=panier,
            is_commande_a_emporter=True,
            moyen_paiement=moyen_paiement,
            is_paid=is_paid,
            commande_is_valid=commande_is_valid,
            heure_pick_up_specifie=heure_retrait
        )

    elif force_type == "livraison_asap":
        is_emporter = False
        moyen_paiement = random.choice(['especes_livraison', 'ticket_livraison'])
        is_paid = False
        commande_is_valid = False
        heure_asap = now + timedelta(minutes=random.randint(20, 45))
        commande = Commande.objects.create(
            client=client,
            adresse_livraison=generer_adresse(client),
            panier=panier,
            is_commande_a_emporter=False,
            moyen_paiement=moyen_paiement,
            is_paid=is_paid,
            commande_is_valid=commande_is_valid,
            heure_livraison_asap=heure_asap
        )

    elif force_type == "livraison_programmee":
        is_emporter = False
        moyen_paiement = random.choice(['especes_livraison', 'ticket_livraison'])
        is_paid = False
        commande_is_valid = False
        date_livraison = now.date() + timedelta(days=random.randint(0, 2))
        heure_livraison = time(hour=random.randint(11, 20), minute=random.choice([0, 15, 30, 45]))
        commande = Commande.objects.create(
            client=client,
            adresse_livraison=generer_adresse(client),
            panier=panier,
            is_commande_a_emporter=False,
            moyen_paiement=moyen_paiement,
            is_paid=is_paid,
            commande_is_valid=commande_is_valid,
            date_livraison_specifiee=date_livraison,
            heure_livraison_specifiee=heure_livraison
        )

    elif force_type == "stripe":
        is_emporter = random.choice([True, False])
        adresse = generer_adresse(client)
        commande = Commande.objects.create(
            client=client,
            adresse_livraison=adresse,
            panier=panier,
            is_commande_a_emporter=is_emporter,
            moyen_paiement='stripe',
            is_paid=True,
            commande_is_valid=True
        )

    else:
        # Génération aléatoire
        is_emporter = random.choice([True, False])
        moyen_paiement = random.choice(
            ['especes_retrait', 'ticket_retrait'] if is_emporter else ['stripe', 'especes_livraison', 'ticket_livraison']
        )
        adresse_livraison = generer_adresse(client)
        is_paid = (moyen_paiement == 'stripe')
        commande_is_valid = is_paid

        if is_emporter:
            heure_retrait = now + timedelta(minutes=random.randint(10, 60))
            commande = Commande.objects.create(
                client=client,
                adresse_livraison=adresse_livraison,
                panier=panier,
                is_commande_a_emporter=True,
                moyen_paiement=moyen_paiement,
                is_paid=is_paid,
                commande_is_valid=commande_is_valid,
                heure_pick_up_specifie=heure_retrait
            )
        else:
            if random.choice([True, False]):
                heure_asap = now + timedelta(minutes=random.randint(20, 45))
                commande = Commande.objects.create(
                    client=client,
                    adresse_livraison=adresse_livraison,
                    panier=panier,
                    is_commande_a_emporter=False,
                    moyen_paiement=moyen_paiement,
                    is_paid=is_paid,
                    commande_is_valid=commande_is_valid,
                    heure_livraison_asap=heure_asap
                )
            else:
                date_livraison = now.date() + timedelta(days=random.randint(0, 2))
                heure_livraison = time(hour=random.randint(11, 20), minute=random.choice([0, 15, 30, 45]))
                commande = Commande.objects.create(
                    client=client,
                    adresse_livraison=adresse_livraison,
                    panier=panier,
                    is_commande_a_emporter=False,
                    moyen_paiement=moyen_paiement,
                    is_paid=is_paid,
                    commande_is_valid=commande_is_valid,
                    date_livraison_specifiee=date_livraison,
                    heure_livraison_specifiee=heure_livraison
                )

    panier.commande = commande
    try:
        panier.save()
    except ValueError as e:
        logger.warning(f"Impossible de sauvegarder le panier {panier.id} : {e}")

    logger.info(f"Commande {commande.id} - {client.nom} - {commande.moyen_paiement} - {'emporter' if commande.is_commande_a_emporter else 'livrer'}")
    return commande




class Command(BaseCommand):
    help = 'Génère des commandes aléatoires avec plats et options'

    def handle(self, *args, **kwargs):
        logger.info("Création des 4 cas obligatoires...")

        # 1. Commande à emporter avec heure de retrait
        commande1 = generer_commande(force_type="emporter")

        # 2. Livraison avec livraison ASAP
        commande2 = generer_commande(force_type="livraison_asap")

        # 3. Livraison avec date et heure spécifiée
        commande3 = generer_commande(force_type="livraison_programmee")

        # 4. Paiement effectué (Stripe)
        commande4 = generer_commande(force_type="stripe")

        logger.info("Cas spécifiques générés. Création de commandes aléatoires...")
        for _ in range(6):
            try:
                generer_commande()  # classique (aléatoire)
            except Exception as e:
                logger.error(f"Erreur lors de la génération d'une commande : {e}")


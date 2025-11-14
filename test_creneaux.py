import pytest
from datetime import datetime, time
from django.utils.timezone import make_aware
from swigo.models import Commande
from swigo.utils import creneau_est_disponible

@pytest.mark.django_db
def test_limite_livraison():
    date = datetime.today().date()
    heure = time(19, 0)

    # Créer 2 commandes livraison valides
    for _ in range(2):
        Commande.objects.create(
            is_commande_a_emporter=False,
            date_livraison_specifiee=date,
            heure_livraison_specifiee=heure,
            moyen_paiement='especes'
        )

    # Trop de livraisons → indisponible
    assert creneau_est_disponible(date, heure, mode='livraison') is False

    # On en supprime une → redevient dispo
    Commande.objects.all().first().delete()
    assert creneau_est_disponible(date, heure, mode='livraison') is True


@pytest.mark.django_db
def test_limite_emporte():
    date = datetime.today().date()
    heure = time(12, 0)
    dt_debut = make_aware(datetime.combine(date, heure))

    # Créer 1 commande à emporter valide
    Commande.objects.create(
        is_commande_a_emporter=True,
        heure_pick_up_specifie=dt_debut,
        moyen_paiement='cb'
    )

    # Créneau saturé
    assert creneau_est_disponible(date, heure, mode='emporter') is False

    # Supprime → redevient dispo
    Commande.objects.all().delete()
    assert creneau_est_disponible(date, heure, mode='emporter') is True


from swigo.utils import chercher_prochain_creneau_disponible

@pytest.mark.django_db
def test_chercher_prochain_creneau_apres_saturation():
    from datetime import timedelta

    print("\n🔁 TEST CHERCHER CRENEAU")

    date = datetime.today().date()
    heure = time(18, 0)  # premier créneau du soir
    dt_depart = make_aware(datetime.combine(date, heure))

    # Saturer le premier créneau (MAX = 2)
    for _ in range(2):
        Commande.objects.create(
            is_commande_a_emporter=False,
            date_livraison_specifiee=date,
            heure_livraison_specifiee=heure,
            moyen_paiement='cb'
        )

    # Le système doit proposer un créneau 15 min plus tard
    prochain_creneau = chercher_prochain_creneau_disponible(dt_depart, mode='livraison')

    attendu = dt_depart + timedelta(minutes=15)
    assert prochain_creneau == attendu, f"Attendu {attendu}, obtenu {prochain_creneau}"
    print(f"✅ Prochain créneau libre trouvé : {prochain_creneau.time()}")



import pytest
from datetime import datetime, timedelta, time
from django.utils import timezone
from swigo.models import AdresseLivraison, VilleDesservie, HoraireDisponible
from swigo.utils import estimer_heure_livraison

@pytest.mark.django_db
def test_estimer_livraison_apres_23h_bascule_jour_suivant():
    print("\n🌙 TEST ESTIMATION À 23H")

    # Créer la ville desservie
    VilleDesservie.objects.create(
        ville="Gisors",
        code_postal="27140",
        nombre_habitants=10000,
        distance_gisors=0,
        temps_gisors=20,
        zone=1,
        panier_minimal=20,
        localisation="N"
    )

    # Créer une adresse valide
    adresse = AdresseLivraison.objects.create(
        adresse="2 Rue Tard",
        code_postal="27140",
        ville="Gisors",
        zone=1,
        localisation="N",
        latitude=49.2794,
        longitude=1.7778
    )

    # Demain (jour suivant)
    demain = (timezone.localtime() + timedelta(days=1)).date()
    jour_str = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"][demain.weekday()]

    # Créneau dispo demain MIDI
    HoraireDisponible.objects.create(
        jour=jour_str,
        service="MIDI",
        heure_debut=time(11, 30),
        heure_fin=time(13, 30),
        intervalle=15
    )

    # Simuler qu'on est aujourd'hui à 23h00
    maintenant = timezone.make_aware(datetime.combine(demain - timedelta(days=1), time(23, 0)))

    # Appeler la fonction
    resultat = estimer_heure_livraison(adresse, maintenant=maintenant)

    # ✅ On attend un datetime, pas une erreur
    assert isinstance(resultat, datetime), f"Une erreur a été retournée : {resultat}"

    # ✅ Le créneau doit être demain (date du jour suivant)
    assert resultat.date() == demain, f"Le créneau devrait être prévu pour le lendemain ({demain}), mais a donné : {resultat}"


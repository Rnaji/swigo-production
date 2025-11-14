from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from swigo.models import Livreur, Tournee, AdresseLivraison
from swigo.utils import estimer_heure_livraison


class Command(BaseCommand):
    help = "Teste les différents cas de l'estimation d'heure de livraison"

    def handle(self, *args, **options):
        now = timezone.localtime()

        def print_test(title):
            self.stdout.write(self.style.SUCCESS(f"\n=== {title} ==="))

        def create_adresse(zone):
            return AdresseLivraison.objects.create(
                adresse=f"Test Zone {zone}",
                code_postal="75000",
                ville=f"Zone {zone}",
                zone=zone,
                localisation="S"
            )

        # Nettoyage
        Livreur.objects.all().delete()
        Tournee.objects.all().delete()
        AdresseLivraison.objects.all().delete()

        # TEST 1 : livreur disponible immédiatement
        print_test("TEST 1 : Livreur libre immédiatement")
        Livreur.objects.create(nom="Ali", au_travaille=True, is_booked=False)
        adresse = create_adresse(zone=1)
        estimation = estimer_heure_livraison(adresse)
        self.stdout.write(f"🕒 Estimation : {estimation.strftime('%Y-%m-%d %H:%M:%S')}")

        # TEST 2 : retour estimé, pas de tournée après
        print_test("TEST 2 : Retour estimé sans tournée suivante")
        Livreur.objects.all().delete()
        Tournee.objects.all().delete()
        livreur2 = Livreur.objects.create(nom="Karim", au_travaille=True, is_booked=True)
        retour = now + timedelta(minutes=30)
        Tournee.objects.create(
            nom=1,
            id_tournee="RT001",
            date_tournee=now.date(),
            livreur=livreur2,
            is_sent_livreur=True,
            heure_retour_estime=retour.time()
        )
        adresse = create_adresse(zone=2)
        estimation = estimer_heure_livraison(adresse)
        self.stdout.write(f"🕒 Estimation : {estimation.strftime('%Y-%m-%d %H:%M:%S')}")

        # TEST 3 : pas encore parti (pas d'heure de retour)
        print_test("TEST 3 : Tournée sans heure de retour (livreur pas encore parti)")
        Livreur.objects.all().delete()
        Tournee.objects.all().delete()
        livreur3 = Livreur.objects.create(nom="Yassine", au_travaille=True, is_booked=True)
        Tournee.objects.create(
            nom=1,
            id_tournee="NP001",
            date_tournee=now.date(),
            livreur=livreur3,
            is_sent_livreur=True,
            heure_retour_estime=None
        )
        adresse = create_adresse(zone=0)
        estimation = estimer_heure_livraison(adresse)
        self.stdout.write(f"🕒 Estimation : {estimation.strftime('%Y-%m-%d %H:%M:%S')}")

        # TEST 4 : surcharge de tournées enchaînées
        print_test("TEST 4 : Tournées chaînées (délai zone surcharge)")
        Livreur.objects.all().delete()
        Tournee.objects.all().delete()
        livreur4 = Livreur.objects.create(nom="Hassan", au_travaille=True, is_booked=True)
        Tournee.objects.create(
            nom=1,
            id_tournee="CH001",
            date_tournee=now.date(),
            livreur=livreur4,
            is_sent_livreur=True,
            heure_retour_estime=(now + timedelta(minutes=30)).time()
        )
        Tournee.objects.create(
            nom=2,
            id_tournee="CH002",
            date_tournee=now.date(),
            livreur=livreur4,
            is_sent_livreur=False
        )
        adresse = create_adresse(zone=3)
        estimation = estimer_heure_livraison(adresse)
        self.stdout.write(f"🕒 Estimation : {estimation.strftime('%Y-%m-%d %H:%M:%S')}")

        self.stdout.write(self.style.SUCCESS("\n✅ Tous les cas ont été testés."))

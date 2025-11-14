from django.utils import timezone
from swigo.models import Commande, AdresseLivraison, Client

# Créer un client fictif
client = Client.objects.create(nom="Test Client", prenom="Test", numero_telephone="0123456789", email="test@test.com")

# Créer des adresses fictives
adresse1 = AdresseLivraison.objects.create(adresse="Mairie, Rue de la Mairie, Montjavoult", code_postal="60240", ville="Montjavoult", zone=1, localisation="S")
adresse2 = AdresseLivraison.objects.create(adresse="Mairie, Rue Hacque, Sérifontaine", code_postal="60590", ville="Sérifontaine", zone=2, localisation="N")
adresse3 = AdresseLivraison.objects.create(adresse="2 Rue de Paris, Gisors", code_postal="27140", ville="Gisors", zone=0, localisation="0")

# Créer des commandes et utiliser set_paid pour déclencher la logique de tournée
commande1 = Commande.objects.create(client=client, adresse_livraison=adresse1, is_paid=False, date_livraison_specifiee=timezone.now().date(), heure_livraison_specifiee=timezone.now().time())
commande2 = Commande.objects.create(client=client, adresse_livraison=adresse2, is_paid=False, date_livraison_specifiee=timezone.now().date(), heure_livraison_specifiee=timezone.now().time())
commande3 = Commande.objects.create(client=client, adresse_livraison=adresse3, is_paid=False, date_livraison_specifiee=timezone.now().date(), heure_livraison_specifiee=timezone.now().time())

# Simuler le paiement des commandes pour déclencher les tournées
commande1.set_paid()
commande2.set_paid()
commande3.set_paid()

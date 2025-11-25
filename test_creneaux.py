# test_creneaux_fin_service.py
import os
import django
import datetime
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from swigo.models import AdresseLivraison, VilleDesservie, HoraireDisponible, Client
from swigo.utils import estimer_heure_livraison, estimer_heure_retrait, creneau_est_disponible

def preparer_adresse_test():
    """Prépare une adresse de test pour les livraisons"""
    try:
        # Utiliser une adresse existante ou créer une simple
        adresse = AdresseLivraison.objects.filter(ville="Gisors").first()
        if not adresse:
            print("ℹ️  Création d'une adresse basique pour test...")
            # Création minimaliste
            client_test = Client.objects.first()
            if not client_test:
                client_test = Client.objects.create(
                    nom="Test", prenom="Client", email="test@test.com"
                )
            adresse = AdresseLivraison.objects.create(
                client=client_test,
                adresse="1 Rue Test",
                code_postal="27140",
                ville="Gisors"
            )
        return adresse
    except Exception as e:
        print(f"❌ Impossible de préparer l'adresse: {e}")
        return None

def tester_scenarios_livraison():
    """Teste différents scénarios de livraison selon l'heure"""
    print("=" * 60)
    print("🧪 TESTS HEURES LIVRAISON PROPOSÉES")
    print("=" * 60)
    
    adresse = preparer_adresse_test()
    if not adresse:
        return
    
    # Scénarios de test avec heures critiques
    scenarios = [
        # Heures normales
        {"nom": "🕘 Matin (9h00)", "heure": datetime.time(9, 0)},
        {"nom": "🕛 Midi (12h00)", "heure": datetime.time(12, 0)},
        
        # Fin de service MIDI
        {"nom": "⏰ Fin Midi - 14h00", "heure": datetime.time(14, 0)},
        {"nom": "🚨 Fin Midi - 14h15", "heure": datetime.time(14, 15)},
        {"nom": "❌ Fin Midi - 14h30", "heure": datetime.time(14, 30)},
        {"nom": "💥 Après Midi - 14h45", "heure": datetime.time(14, 45)},
        {"nom": "💥 Après Midi - 15h00", "heure": datetime.time(15, 0)},
        
        # Début SOIR
        {"nom": "🌙 Début Soir - 18h00", "heure": datetime.time(18, 0)},
        {"nom": "🌙 Soir - 19h00", "heure": datetime.time(19, 0)},
        {"nom": "🌙 Soir - 20h00", "heure": datetime.time(20, 0)},
        
        # Fin de service SOIR
        {"nom": "⏰ Fin Soir - 21h30", "heure": datetime.time(21, 30)},
        {"nom": "🚨 Fin Soir - 22h00", "heure": datetime.time(22, 0)},
        {"nom": "🚨 Fin Soir - 22h15", "heure": datetime.time(22, 15)},
        {"nom": "❌ Fin Soir - 22h30", "heure": datetime.time(22, 30)},
        {"nom": "💥 Après Soir - 22h45", "heure": datetime.time(22, 45)},
        {"nom": "💥 Nuit - 23h00", "heure": datetime.time(23, 0)},
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['nom']}")
        print("-" * 40)
        
        # Créer un datetime simulé pour aujourd'hui
        aujourdhui = timezone.localtime().date()
        heure_simulee = datetime.datetime.combine(aujourdhui, scenario['heure'])
        heure_simulee = timezone.make_aware(heure_simulee)
        
        print(f"⏰ Heure simulation: {heure_simulee.strftime('%d/%m/%Y %H:%M')}")
        
        try:
            resultat = estimer_heure_livraison(adresse, maintenant=heure_simulee)
            
            if isinstance(resultat, dict) and 'error' in resultat:
                print(f"❌ Erreur: {resultat['error']}")
            else:
                print(f"✅ Heure proposée: {resultat.strftime('%d/%m/%Y %H:%M')}")
                delai = (resultat - heure_simulee).total_seconds() / 60
                print(f"⏱️  Délai estimé: {delai:.0f} minutes")
                
                # Vérifier si c'est le même jour ou jour suivant
                if resultat.date() > heure_simulee.date():
                    print(f"📅 Report au jour suivant")
                
        except Exception as e:
            print(f"💥 Erreur lors du test: {e}")

def tester_retrait_emporter_fin_service():
    """Teste les heures de retrait à emporter avec heures de fin de service"""
    print("\n" + "=" * 60)
    print("🥡 TESTS RETRAIT - HEURES CRITIQUES")
    print("=" * 60)
    
    # Scénarios pour retrait avec heures limites
    scenarios_retrait = [
        {"nom": "🕘 Matin (9h00)", "heure": datetime.time(9, 0)},
        {"nom": "🕛 Midi (12h00)", "heure": datetime.time(12, 0)},
        
        # Fin service MIDI
        {"nom": "⏰ Fin Midi - 14h00", "heure": datetime.time(14, 0)},
        {"nom": "🚨 Fin Midi - 14h15", "heure": datetime.time(14, 15)},
        {"nom": "❌ Fin Midi - 14h30", "heure": datetime.time(14, 30)},
        
        # Transition après-midi
        {"nom": "💥 Après-midi 15h00", "heure": datetime.time(15, 0)},
        {"nom": "💥 Après-midi 16h00", "heure": datetime.time(16, 0)},
        {"nom": "💥 Après-midi 17h00", "heure": datetime.time(17, 0)},
        
        # Début SOIR
        {"nom": "🌙 Début Soir - 18h00", "heure": datetime.time(18, 0)},
        {"nom": "🌙 Soir - 19h00", "heure": datetime.time(19, 0)},
        
        # Fin service SOIR
        {"nom": "⏰ Fin Soir - 21h30", "heure": datetime.time(21, 30)},
        {"nom": "🚨 Fin Soir - 22h00", "heure": datetime.time(22, 0)},
        {"nom": "🚨 Fin Soir - 22h15", "heure": datetime.time(22, 15)},
        {"nom": "❌ Fin Soir - 22h30", "heure": datetime.time(22, 30)},
        {"nom": "💥 Après Soir - 22h45", "heure": datetime.time(22, 45)},
    ]
    
    for scenario in scenarios_retrait:
        print(f"\n{scenario['nom']}")
        print("-" * 40)
        
        # Simuler l'heure actuelle
        aujourdhui = timezone.localtime().date()
        heure_simulee = datetime.datetime.combine(aujourdhui, scenario['heure'])
        heure_simulee = timezone.make_aware(heure_simulee)
        
        print(f"⏰ Heure simulation: {heure_simulee.strftime('%d/%m/%Y %H:%M')}")
        
        try:
            # Pour tester retrait, on va simuler le comportement
            original_now = timezone.now
            
            # Temporairement remplacer now() pour le test
            def mock_now():
                return heure_simulee
            timezone.now = mock_now
            
            heure_retrait = estimer_heure_retrait()
            print(f"✅ Heure retrait proposée: {heure_retrait.strftime('%d/%m/%Y %H:%M')}")
            
            delai = (heure_retrait - heure_simulee).total_seconds() / 60
            print(f"⏱️  Délai estimé: {delai:.0f} minutes")
            
            # Vérifier si c'est le même jour ou jour suivant
            if heure_retrait.date() > heure_simulee.date():
                print(f"📅 Report au jour suivant")
            
            # Restaurer la fonction now originale
            timezone.now = original_now
            
        except Exception as e:
            print(f"💥 Erreur: {e}")
            # Restaurer en cas d'erreur
            timezone.now = original_now

def tester_limites_service():
    """Teste spécifiquement les limites de service"""
    print("\n" + "=" * 60)
    print("🚨 TESTS LIMITES DE SERVICE")
    print("=" * 60)
    
    adresse = preparer_adresse_test()
    if not adresse:
        return
    
    # Test des limites exactes
    limites = [
        {"nom": "LIMITE MIDI - 14h29", "heure": datetime.time(14, 29)},
        {"nom": "LIMITE MIDI - 14h30", "heure": datetime.time(14, 30)},
        {"nom": "LIMITE MIDI - 14h31", "heure": datetime.time(14, 31)},
        {"nom": "LIMITE SOIR - 22h29", "heure": datetime.time(22, 29)},
        {"nom": "LIMITE SOIR - 22h30", "heure": datetime.time(22, 30)},
        {"nom": "LIMITE SOIR - 22h31", "heure": datetime.time(22, 31)},
    ]
    
    for limite in limites:
        print(f"\n{limite['nom']}")
        print("-" * 30)
        
        aujourdhui = timezone.localtime().date()
        heure_simulee = datetime.datetime.combine(aujourdhui, limite['heure'])
        heure_simulee = timezone.make_aware(heure_simulee)
        
        print(f"⏰ Simulation: {heure_simulee.strftime('%H:%M')}")
        
        try:
            resultat = estimer_heure_livraison(adresse, maintenant=heure_simulee)
            
            if isinstance(resultat, dict) and 'error' in resultat:
                print(f"❌ {resultat['error']}")
            else:
                print(f"✅ Proposé: {resultat.strftime('%d/%m %H:%M')}")
                if resultat.date() > heure_simulee.date():
                    print("🔁 Reporté au lendemain")
                    
        except Exception as e:
            print(f"💥 Erreur: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests des créneaux horaires critiques...")
    print(f"📅 Date du jour: {timezone.localtime().strftime('%d/%m/%Y')}")
    
    try:
        tester_scenarios_livraison()
        tester_retrait_emporter_fin_service()
        tester_limites_service()
        
        print("\n" + "=" * 60)
        print("🎯 TESTS DES HEURES LIMITES TERMINÉS")
        print("=" * 60)
        
    except Exception as e:
        print(f"💥 ERREUR GLOBALE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
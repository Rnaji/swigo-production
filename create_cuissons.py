from swigo.models import Plat, Option, Cuisson

def create_cuissons():
    # 1. 1/4 de Poulet braisé – 1/4 Poulet, Josper
    try:
        plat = Plat.objects.get(nom="1/4 de Poulet braisé")
        Cuisson.objects.create(plat=plat, ingredient="Poulet", quantite=1, mode_cuisson="josper")
    except Plat.DoesNotExist:
        print("Le plat '1/4 de Poulet braisé' n'existe pas.")

    # 2. Pâtes au thon – Pâtes, Cuiseur
    try:
        plat = Plat.objects.get(nom="Pâtes au thon")
        Cuisson.objects.create(plat=plat, ingredient="Pâtes", quantite=1, mode_cuisson="cuiseur")
    except Plat.DoesNotExist:
        print("Le plat 'Pâtes au thon' n'existe pas.")

    # 3. Couscous Royal – 1 Merguez, Josper
    try:
        plat = Plat.objects.get(nom="Couscous Royal")
        Cuisson.objects.create(plat=plat, ingredient="Merguez", quantite=1, mode_cuisson="josper")
        Cuisson.objects.create(plat=plat, ingredient="Brochette", quantite=1, mode_cuisson="josper")
        Cuisson.objects.create(plat=plat, ingredient="Poulet", quantite=1, mode_cuisson="josper")
    except Plat.DoesNotExist:
        print("Le plat 'Couscous Royal' n'existe pas.")

    # 4. Couscous Merguez – 2 Merguez, Josper
    try:
        plat = Plat.objects.get(nom="Couscous Merguez")
        Cuisson.objects.create(plat=plat, ingredient="Merguez", quantite=2, mode_cuisson="josper")
    except Plat.DoesNotExist:
        print("Le plat 'Couscous Merguez' n'existe pas.")

    # 5. Burger Hamza – 1 Steak, Grill
    try:
        plat = Plat.objects.get(nom="Burger Hamza")
        Cuisson.objects.create(plat=plat, ingredient="Steak", quantite=1, mode_cuisson="grill")
    except Plat.DoesNotExist:
        print("Le plat 'Burger Hamza' n'existe pas.")

    # 6. Burger Mimile – 1 Steak, Grill
    try:
        plat = Plat.objects.get(nom="Burger Mimile")
        Cuisson.objects.create(plat=plat, ingredient="Steak", quantite=1, mode_cuisson="grill")
    except Plat.DoesNotExist:
        print("Le plat 'Burger Mimile' n'existe pas.")

    # 7. Burger Didine – 1 Steak, Grill
    try:
        plat = Plat.objects.get(nom="Burger Didine")
        Cuisson.objects.create(plat=plat, ingredient="Steak", quantite=1, mode_cuisson="grill")
    except Plat.DoesNotExist:
        print("Le plat 'Burger Didine' n'existe pas.")

    # 8. Burger Royal – 2 Steaks, Grill
    try:
        plat = Plat.objects.get(nom="Burger Royal")
        Cuisson.objects.create(plat=plat, ingredient="Steak", quantite=2, mode_cuisson="grill")

        # 9. Vérifier si l'option "double steack" existe pour ce plat
        try:
            option = Option.objects.get(nom_option="double steack", plat=plat)
        except Option.DoesNotExist:
            # Si l'option n'existe pas, on la crée
            print("L'option 'double steack' n'existe pas. Création de l'option.")
            option = Option.objects.create(plat=plat, nom_option="double steack", prix_unitaire=5.00)

        # 10. Créer la cuisson associée à l'option "double steack"
        Cuisson.objects.create(option=option, ingredient="Steak", quantite=1, mode_cuisson="grill")

    except Plat.DoesNotExist:
        print("Le plat 'Burger Royal' n'existe pas.")

# Appeler la fonction pour créer les cuissons
create_cuissons()

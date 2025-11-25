from django.shortcuts import render


from django.shortcuts import redirect

def index(request):
    return redirect('adresse_livraison')  # Redirige vers la page adresse_livraison


def index_2(request):
    context={
        "page_title":"Home 2"
    }
    return render(request,'swigo/index-2.html',context)

def index_3(request):
    context={
        "page_title":"Home 3"
    }
    return render(request,'swigo/index-3.html',context)

def about_us(request):
    context={
        "page_title":"About Us"
    }
    return render(request,'swigo/about-us.html',context)

def faq(request):
    context={
        "page_title":"FAQ"
    }
    return render(request,'swigo/faq.html',context)

def team(request):
    context={
        "page_title":"Team"
    }
    return render(request,'swigo/team.html',context)

def team_detail(request):
    context={
        "page_title":"Team Detail"
    }
    return render(request,'swigo/team-detail.html',context)

def testimonial(request):
    context={
        "page_title":"Testimonial"
    }
    return render(request,'swigo/testimonial.html',context)

def services(request):
    context={
        "page_title":"Services"
    }
    return render(request,'swigo/services.html',context)

def service_detail(request):
    context={
        "page_title":"Service Detail"
    }
    return render(request,'swigo/service-detail.html',context)

def our_menu_1(request):
    context={
        "page_title":"Our Menu 1"
    }
    return render(request,'swigo/our-menu-1.html',context)

def our_menu_2(request):
    context={
        "page_title":"Our Menu 2"
    }
    return render(request,'swigo/our-menu-2.html',context)

def our_menu_3(request):
    context={
        "page_title":"Our Menu 3"
    }
    return render(request,'swigo/our-menu-3.html',context)

def our_menu_4(request):
    context={
        "page_title":"Our Menu 4"
    }
    return render(request,'swigo/our-menu-4.html',context)

def our_menu_5(request):
    context={
        "page_title":"Our Menu 5"
    }
    return render(request,'swigo/our-menu-5.html',context)

def shop_style_1(request):
    context={
        "page_title":"Shop Style 1"
    }
    return render(request,'swigo/shop-style-1.html',context)

def shop_style_2(request):
    context={
        "page_title":"Shop Style 2"
    }
    return render(request,'swigo/shop-style-2.html',context)

def shop_cart(request):
    context={
        "page_title":"Shop Cart"
    }
    return render(request,'swigo/shop-cart.html',context)

def shop_wishlist(request):
    context={
        "page_title":"Shop Wishlist"
    }
    return render(request,'swigo/shop-wishlist.html',context)

def shop_checkout(request):
    context={
        "page_title":"Shop Checkout"
    }
    return render(request,'swigo/shop-checkout.html',context)

def product_detail(request):
    context={
        "page_title":"Product Detail"
    }
    return render(request,'swigo/product-detail.html',context)

def blog_grid_2(request):
    context={
        "page_title":"Blog Grid 2"
    }
    return render(request,'swigo/blog-grid-2.html',context)

def blog_grid_3(request):
    context={
        "page_title":"Blog Grid 3"
    }
    return render(request,'swigo/blog-grid-3.html',context)

def blog_grid_left_sidebar(request):
    context={
        "page_title":"Blog Grid Left Sidebar"
    }
    return render(request,'swigo/blog-grid-left-sidebar.html',context)

def blog_grid_right_sidebar(request):
    context={
        "page_title":"Blog Grid Right Sidebar"
    }
    return render(request,'swigo/blog-grid-right-sidebar.html',context)

def blog_list(request):
    context={
        "page_title":"Blog List"
    }
    return render(request,'swigo/blog-list.html',context)

def blog_list_left_sidebar(request):
    context={
        "page_title":"Blog List Left Sidebar"
    }
    return render(request,'swigo/blog-list-left-sidebar.html',context)

def blog_list_right_sidebar(request):
    context={
        "page_title":"Blog List Right Sidebar"
    }
    return render(request,'swigo/blog-list-right-sidebar.html',context)

def blog_both_sidebar(request):
    context={
        "page_title":"Blog Both Sidebar"
    }
    return render(request,'swigo/blog-both-sidebar.html',context)

def blog_standard(request):
    context={
        "page_title":"Blog Standard"
    }
    return render(request,'swigo/blog-standard.html',context)

def blog_open_gutenberg(request):
    context={
        "page_title":"Blog Open Gutenberg"
    }
    return render(request,'swigo/blog-open-gutenberg.html',context)

def blog_detail_left_sidebar(request):
    context={
        "page_title":"Blog Detail Left Sidebar"
    }
    return render(request,'swigo/blog-detail-left-sidebar.html',context)

def blog_detail_right_sidebar(request):
    context={
        "page_title":"Blog Detail Right Sidebar"
    }
    return render(request,'swigo/blog-detail-right-sidebar.html',context)

def blog_grid_3_masonary(request):
    context={
        "page_title":"Blog Grid 3 Masonry"
    }
    return render(request,'swigo/blog-grid-3-masonary.html',context)

def blog_grid_4_masonary(request):
    context={
        "page_title":"Blog Grid 4 Masonry"
    }
    return render(request,'swigo/blog-grid-4-masonary.html',context)

def blog_wide_list_sidebar(request):
    context={
        "page_title":"Blog Wide List Sidebar"
    }
    return render(request,'swigo/blog-wide-list-sidebar.html',context)

def blog_wide_grid_sidebar(request):
    context={
        "page_title":"Blog Wide Grid Sidebar"
    }
    return render(request,'swigo/blog-wide-grid-sidebar.html',context)

def contact_us(request):
    context={
        "page_title":"Contact Us"
    }
    return render(request,'swigo/contact-us.html',context)

def coming_soon(request):
    context={
        "page_title":"Coming Soon"
    }
    return render(request,'swigo/coming-soon.html',context)

def under_maintenance(request):
    context={
        "page_title":"Under Maintenance"
    }
    return render(request,'swigo/under-maintenance.html',context)

def error_404(request):
    context={
        "page_title":"Error 404"
    }
    return render(request,'404.html',context)


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from datetime import date, timedelta, datetime
import logging
import json
from decimal import Decimal

from .forms import (
    AdresseLivraisonForm, 
    DateTimeDeliveryForm, 
    CodePromoForm,
)
from .models import (
    AdresseLivraison, 
    Commande, 
    VilleDesservie, 
    CodePromo, 
    Plat, 
    Option, 
    HoraireDisponible, 
    Categorie, 
    ArticlePanier, 
    Panier,
    JourFermeture,
    SaladePersonnalisee,
    PouletOption,
    Accompagnement,
    LimiteOptionsPoulet
)
from .utils import estimer_heure_livraison, creneau_est_disponible, estimer_heure_retrait

logger = logging.getLogger(__name__)

def format_date_fr(date_obj):
    jours = [
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"
    ]
    mois = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    jour = jours[date_obj.weekday()]
    mois_nom = mois[date_obj.month - 1]
    return f"{jour} {date_obj.day} {mois_nom} {date_obj.year}"

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import date, timedelta, datetime
import logging

from .forms import AdresseLivraisonForm
from .models import (
    AdresseLivraison,
    Commande,
    VilleDesservie,
    Panier,
    HoraireDisponible,
    JourFermeture,
    CouscousPersonnalise,
)
from .utils import estimer_heure_livraison, estimer_heure_retrait

logger = logging.getLogger(__name__)

@csrf_exempt
def adresse_livraison(request):
    print("===== ADRESSE_LIVRAISON =====")
    print(f"Méthode: {request.method}")
    
    if request.method == 'POST':
        try:
            # 1. Récupération des données
            adresse = request.POST.get('adresse_livraison', '').strip()
            code_postal = request.POST.get('code_postal', '').strip()
            ville = request.POST.get('ville', '').strip()
            latitude = request.POST.get('latitude', '')
            longitude = request.POST.get('longitude', '')
            
            print(f"📦 Données reçues: {adresse}, {code_postal}, {ville}")
            
            # 2. Validation basique
            if not adresse or not code_postal or not ville:
                return JsonResponse({
                    'error': 'Veuillez remplir tous les champs obligatoires.',
                    'disable_livrer_au_plus_tot': True,
                    'disable_planifier': True,
                    'disable_emporter': True
                }, status=400)
            
            # 3. Vérification si la ville est desservie
            try:
                ville_desservie = VilleDesservie.objects.get(ville__iexact=ville)
                print(f"✅ Ville desservie: {ville}")
                hors_zone = False
            except VilleDesservie.DoesNotExist:
                print(f"❌ Ville NON desservie: {ville}")
                hors_zone = True
            
            # 4. CAS HORS ZONE - Uniquement pickup disponible
            if hors_zone:
                print("🟡 Traitement cas HORS ZONE")
                
                # Calcul du premier créneau emporter disponible
                try:
                    creneau_emporter_dispo = estimer_heure_retrait()
                    premiere_heure_emporter = creneau_emporter_dispo.strftime('%H:%M')
                    premiere_date_emporter = creneau_emporter_dispo.date().strftime('%Y-%m-%d')
                    print(f"🕒 Créneau emporter: {premiere_date_emporter} {premiere_heure_emporter}")
                except Exception as exc:
                    print(f"⚠️ Erreur estimation créneau emporter: {exc}")
                    premiere_heure_emporter = ''
                    premiere_date_emporter = ''
                
                # Nettoyage de la session
                request.session.flush()
                request.session.create()
                
                # Création de l'adresse pour pickup
                adresse_livraison = AdresseLivraison.objects.create(
                    adresse="Retrait sur place",
                    code_postal=code_postal,
                    ville=ville,
                    zone=-1,  # -1 pour "hors zone"
                    localisation="EXT",  # "EXT" pour "exterieur"
                    latitude=latitude,
                    longitude=longitude
                )
                
                # Création de la commande PICKUP
                commande = Commande.objects.create(
                    client=None,
                    adresse_livraison=adresse_livraison,
                    session_key=request.session.session_key,
                    is_commande_a_emporter=True  # ← MODE PICKUP
                )
                request.session['commande_id'] = commande.id
                
                # Création du panier
                panier = Panier.objects.create(
                    commande=commande,
                    session_key=request.session.session_key
                )
                commande.panier = panier
                commande.save()
                
                print(f"✅ Commande pickup créée - ID: {commande.id}")
                
                return JsonResponse({
                    'error': 'Malheureusement nous ne livrons pas votre secteur. Vous pouvez quand même commander à emporter !',
                    'disable_livrer_au_plus_tot': True,
                    'disable_planifier': True,
                    'disable_emporter': False,
                    'pickup_indispo': False,
                    'premiere_date': premiere_date_emporter,
                    'premiere_heure': premiere_heure_emporter,
                    'commande_id': commande.id,
                    'panier_id': panier.id,
                    'hors_zone': True
                })
            
            # 5. CAS ZONE DESSERVIE - Livraison disponible
            else:
                print("🟢 Traitement cas ZONE DESSERVIE")
                
                # Nettoyage de l'adresse
                adresse_clean = adresse.split(',')[0].strip()
                
                # Création ou récupération de l'adresse
                adresse_livraison, created = AdresseLivraison.objects.get_or_create(
                    adresse=adresse_clean,
                    code_postal=code_postal,
                    ville=ville,
                    zone=ville_desservie.zone,
                    localisation=ville_desservie.localisation,
                    defaults={
                        'latitude': latitude,
                        'longitude': longitude
                    }
                )
                
                print(f"📌 Adresse: {'Créée' if created else 'Existante'} - ID: {adresse_livraison.id}")
                
                # Estimation de l'horaire de livraison
                try:
                    estimation = estimer_heure_livraison(adresse_livraison)
                    print(f"🕒 Estimation brute: {estimation}")
                    
                    # Gestion des erreurs d'estimation
                    if isinstance(estimation, dict) and estimation.get('error'):
                        return JsonResponse({
                            'error': estimation['error'],
                            'disable_livrer_au_plus_tot': True,
                            'disable_planifier': False,
                            'disable_emporter': True,
                        })
                    
                    # Conversion en datetime aware si nécessaire
                    if timezone.is_naive(estimation):
                        estimation = timezone.make_aware(estimation)
                    
                    date_estimee = estimation.date()
                    heure_estimee = estimation.time()
                    
                    print(f"📅 Date estimée: {date_estimee}, Heure: {heure_estimee}")
                    
                    # Vérification que le créneau n'est pas dans le passé
                    maintenant = timezone.localtime()
                    if estimation < maintenant:  # ✅ CORRECTION : estimation doit être APRÈS maintenant
                        print("⚠️ Créneau dans le passé, recherche du prochain...")
                        prochaine_heure = chercher_prochain_creneau_disponible(
                            maintenant + timedelta(hours=1), 
                            mode='livraison'
                        )
                        
                        jours_fr = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
                        mois_fr = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
                        
                        jour_txt = jours_fr[prochaine_heure.weekday()]
                        date_str = f"{prochaine_heure.day} {mois_fr[prochaine_heure.month]}"
                        heure_str = prochaine_heure.strftime('%H:%M')
                        
                        return JsonResponse({
                            'error': f"C'est terminé pour aujourd'hui. 📦 Prochaine livraison {jour_txt} {date_str} à {heure_str}.",
                            'disable_livrer_au_plus_tot': True,
                            'disable_planifier': False,
                            'disable_emporter': True,
                        })
                        
                except Exception as e:
                    print(f"❌ Erreur estimation horaire: {e}")
                    return JsonResponse({
                        'error': 'Erreur lors de l\'estimation des horaires.',
                        'disable_livrer_au_plus_tot': True,
                        'disable_planifier': True,
                        'disable_emporter': True,
                    }, status=500)
                
                # Vérification des fermetures exceptionnelles
                fermeture = JourFermeture.objects.filter(
                    date_debut__lte=date_estimee, 
                    date_fin__gte=date_estimee
                ).first()
                
                if fermeture:
                    return JsonResponse({
                        'error': f"Le restaurant est fermé ce jour-là : {fermeture.description or 'fermeture exceptionnelle'}",
                        'disable_livrer_au_plus_tot': True,
                        'disable_emporter': True,
                        'disable_planifier': True,
                    })
                
                # Création de la session
                request.session.flush()
                request.session.create()
                
                # Création de la commande LIVRAISON
                commande = Commande.objects.create(
                    client=None,
                    adresse_livraison=adresse_livraison,
                    session_key=request.session.session_key,
                    date_livraison_specifiee=date_estimee,
                    heure_livraison_specifiee=heure_estimee,
                    is_commande_a_emporter=False  # ← MODE LIVRAISON
                )
                request.session['commande_id'] = commande.id
                
                # Création du panier
                panier = Panier.objects.create(
                    commande=commande,
                    session_key=request.session.session_key
                )
                commande.panier = panier
                commande.save()
                
                print(f"✅ Commande livraison créée - ID: {commande.id}")
                
                # Calcul créneau emporter pour comparaison
                try:
                    creneau_emporter_dispo = estimer_heure_retrait()
                    premiere_heure_emporter = creneau_emporter_dispo.strftime('%H:%M')
                    premiere_date_emporter = creneau_emporter_dispo.date().strftime('%Y-%m-%d')
                except Exception as exc:
                    print(f"⚠️ Erreur estimation créneau emporter: {exc}")
                    premiere_heure_emporter = ''
                    premiere_date_emporter = ''
                
                # Vérification si pickup disponible aujourd'hui
                pickup_indispo = True
                try:
                    aujourd_hui = timezone.localdate()
                    heure_now = timezone.localtime().time()
                    jours_translation = {
                        'MON': 'LUN', 'TUE': 'MAR', 'WED': 'MER', 'THU': 'JEU',
                        'FRI': 'VEN', 'SAT': 'SAM', 'SUN': 'DIM'
                    }
                    jour_str = aujourd_hui.strftime('%a').upper()
                    jour_traduit = jours_translation.get(jour_str, jour_str)
                    horaires_jours = HoraireDisponible.objects.filter(jour=jour_traduit)
                    
                    for horaire in horaires_jours:
                        for hstr in horaire.get_horaires():
                            h = datetime.strptime(hstr, "%H:%M").time()
                            if h > heure_now:
                                pickup_indispo = False
                                break
                        if not pickup_indispo:
                            break
                except Exception as exc:
                    print(f"⚠️ Erreur vérification pickup: {exc}")
                    pickup_indispo = True
                
                # Formatage du message de livraison
                jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
                mois_fr = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
                
                dt = date_estimee
                jour_txt = jours_fr[dt.weekday()]
                date_str = f"{dt.day} {mois_fr[dt.month]}"
                
                # Calcul plage horaire livraison
                # Calcul plage horaire livraison (sans ajouter le temps de trajet)
                dt_depart = datetime.combine(dt, heure_estimee)
                heure1 = dt_depart.time().strftime('%H:%M')
                heure2 = (dt_depart + timedelta(minutes=15)).time().strftime('%H:%M')
                
                if date_estimee == timezone.localdate():
                    message = f"Livraison au plus tôt estimée entre {heure1} et {heure2}."
                    has_error = False
                else:
                    message = f"C'est terminé pour aujourd'hui. 📦 Prochaine livraison {jour_txt} {date_str} entre {heure1} et {heure2}."
                    has_error = True
                
                # Détermination état des boutons
                aujourdhui = timezone.localdate()
                disable_livrer_au_plus_tot = (date_estimee > aujourdhui) or has_error
                disable_emporter = disable_livrer_au_plus_tot
                disable_planifier = False
                pickup_indispo_flag = pickup_indispo if date_estimee == aujourdhui else True
                
                # Construction de la réponse
                response_data = {
                    'message': message,
                    'commande_id': commande.id,
                    'panier_id': panier.id,
                    'zone': adresse_livraison.zone,
                    'premiere_date': date_estimee.strftime('%Y-%m-%d'),
                    'premiere_heure': heure_estimee.strftime('%H:%M'),
                    'premiere_date_emporter': premiere_date_emporter,
                    'premiere_heure_emporter': premiere_heure_emporter,
                    'pickup_indispo': pickup_indispo_flag,
                    'disable_livrer_au_plus_tot': disable_livrer_au_plus_tot,
                    'disable_emporter': disable_emporter,
                    'disable_planifier': disable_planifier,
                    'hors_zone': False
                }
                
                # Ajout de l'erreur si pas aujourd'hui
                if has_error:
                    response_data['error'] = message
                
                print(f"✅ Réponse finale: {response_data}")
                return JsonResponse(response_data)
                
        except Exception as e:
            print(f"❌ ERREUR GLOBALE: {e}")
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            
            return JsonResponse({
                'error': 'Une erreur technique est survenue. Veuillez réessayer.',
                'disable_livrer_au_plus_tot': True,
                'disable_planifier': True,
                'disable_emporter': True
            }, status=500)
    
    # REQUÊTE GET - Affichage du formulaire
    else:
        print("📄 Affichage formulaire GET")
        
        # Vérification des fermetures à venir
        today = date.today()
        dates_a_verifier = [today + timedelta(days=i) for i in range(3)]
        message_fermeture = None
        
        for date_to_check in dates_a_verifier:
            fermeture = JourFermeture.objects.filter(
                date_debut__lte=date_to_check, 
                date_fin__gte=date_to_check
            ).first()
            
            if fermeture:
                if fermeture.date_debut == fermeture.date_fin:
                    date_str = fermeture.date_debut.strftime('%d/%m/%Y')
                else:
                    date_str = f"{fermeture.date_debut.strftime('%d/%m')} → {fermeture.date_fin.strftime('%d/%m')}"
                
                message_fermeture = f"Nous sommes exceptionnellement fermés le {date_str}. Motif : {fermeture.description}"
                break
        
        return render(request, 'swigo/adresse_livraison.html', {
            'form': AdresseLivraisonForm(),
            'message_fermeture': message_fermeture,
        })









def nettoyer_adresse(adresse, ville, code_postal):
    adresse_nettoyee = adresse
    if ville.lower() in adresse.lower():
        adresse_nettoyee = adresse_nettoyee.replace(ville, '').strip()
    if code_postal in adresse_nettoyee:
        adresse_nettoyee = adresse_nettoyee.replace(code_postal, '').strip()
    adresse_nettoyee = adresse_nettoyee.replace('France', '').strip()
    while ',,' in adresse_nettoyee or ',,,' in adresse_nettoyee:
        adresse_nettoyee = adresse_nettoyee.replace(',,,', ',').replace(',,', ',')
    adresse_nettoyee = adresse_nettoyee.strip(',')
    adresse_nettoyee = ', '.join(part.strip() for part in adresse_nettoyee.split(',') if part.strip())
    adresse_nettoyee = ' '.join(adresse_nettoyee.split())
    return adresse_nettoyee


from .utils import estimer_heure_livraison, arrondir_au_quart_heure, chercher_prochain_creneau_disponible


@csrf_exempt
def programmer_livraison(request):
    jours_translation = {
        'MON': 'LUN', 'TUE': 'MAR', 'WED': 'MER', 'THU': 'JEU',
        'FRI': 'VEN', 'SAT': 'SAM', 'SUN': 'DIM'
    }

    if request.method == 'POST':
        form = DateTimeDeliveryForm(request.POST)
        if form.is_valid():
            date_livraison = form.cleaned_data['date_livraison']
            heure_livraison = form.cleaned_data['heure_livraison']

            # Si le restaurant est fermé ce jour-là : retourne tous les flags désactivés
            if JourFermeture.est_ferme(date_livraison):
                motif = JourFermeture.objects.filter(
                    date_debut__lte=date_livraison, date_fin__gte=date_livraison
                ).first()
                motif_desc = motif.description if motif else "fermeture exceptionnelle"
                return JsonResponse({
                    'error': f"Le restaurant est fermé ce jour-là : {motif_desc}",
                    'disable_livrer_au_plus_tot': True,
                    'disable_emporter': True,
                    'disable_planifier': True,
                    'pickup_indispo': True,
                }, status=400)

            commande_id = request.POST.get('commande_id') or request.session.get('commande_id')
            if not commande_id:
                return JsonResponse({'error': 'Aucune commande trouvée'}, status=400)

            commande = get_object_or_404(Commande, id=commande_id)
            now = timezone.localtime()
            if date_livraison == now.date() and heure_livraison <= now.time():
                return JsonResponse({'error': 'Vous ne pouvez pas sélectionner un horaire déjà passé'}, status=400)

            if creneau_est_disponible(date_livraison, heure_livraison, mode='livraison'):
                commande.date_livraison_specifiee = date_livraison
                commande.heure_livraison_specifiee = heure_livraison
                commande.save()
                return redirect('swigo:renseigner_commande')
            else:
                return JsonResponse({'error': 'Ce créneau est complet, veuillez en choisir un autre.'}, status=400)

        return JsonResponse({'error': 'Données invalides', 'form_errors': form.errors}, status=400)

    # --- GET ---
    form = DateTimeDeliveryForm()
    today = timezone.localdate()
    dates_disponibles = [today + timedelta(days=i) for i in range(3)]  # 3 prochains jours

    # Chargement des jours fermés et motifs sur la période
    jours_fermes = {
        d: jf.description
        for jf in JourFermeture.objects.all()
        for d in [jf.date_debut + timedelta(days=i) for i in range((jf.date_fin - jf.date_debut).days + 1)]
    }

    commande_id = request.GET.get('commande_id') or request.session.get('commande_id')
    if not commande_id:
        return redirect('swigo:adresse_livraison')

    commande = get_object_or_404(Commande, id=commande_id)
    adresse = commande.adresse_livraison


    # --- Estimation initiale ---
    estimation = estimer_heure_livraison(adresse)

    # Par défaut (en cas de plantage), mettre estimation à None
    if estimation is None:
        return render(request, "swigo/programmer_livraison.html", {
            'indispo': True,
            'message': "Erreur inconnue lors de l’estimation de la livraison."
        })

    if isinstance(estimation, dict) and 'error' in estimation:
    # En cas de fermeture totale, afficher message et désactiver livraison au plus tôt
        if "fermé" in estimation["error"].lower():
            return render(request, "swigo/programmer_livraison.html", {
                'indispo': True,
                'message': estimation['error']
            })
        heure_estim = datetime.strptime("23:59", "%H:%M").time()
        date_estimee = today
    else:
        estimation = timezone.localtime(estimation)

        # ✅ Vérifie si le créneau est encore dispo (très important !)
        if not creneau_est_disponible(estimation.date(), estimation.time(), mode='livraison'):
            return render(request, "swigo/programmer_livraison.html", {
                'indispo': True,
                'message': "Aucun créneau de livraison disponible actuellement."
            })

        # ⚠️ Vérifie aussi s’il n’est pas déjà dépassé
        if estimation < timezone.localtime():
            estimation += timedelta(days=1)
            estimation = estimation.replace(hour=0, minute=0, second=0)

        heure_estim = arrondir_au_quart_heure(estimation).time()
        date_estimee = estimation.date().strftime('%Y-%m-%d')
        heure_estimee_val = heure_estim.strftime('%H:%M')





    horaires_disponibles = {}
    horaires_complets = {}
    jours_affiches = []

    horaires_jours = HoraireDisponible.objects.filter(jour__in=jours_translation.values())

    for date in dates_disponibles:
        if date in jours_fermes:
            jours_affiches.append({
                'date': date,
                'ferme_exceptionnellement': True,
                'motif': jours_fermes[date]
            })
            continue

        jour_str = date.strftime('%a').upper()
        jour_traduit = jours_translation.get(jour_str, jour_str)

        horaires_par_service_dispo = {'MIDI': [], 'SOIR': []}
        horaires_par_service_complet = {'MIDI': [], 'SOIR': []}
        horaires_jour = horaires_jours.filter(jour=jour_traduit)

        for horaire in horaires_jour:
            for horaire_str in horaire.get_horaires():
                try:
                    h = datetime.strptime(horaire_str, "%H:%M").time()
                    # Masquer horaires déjà passés aujourd'hui
                    if date == today and h < heure_estim:
                        continue
                    horaires_par_service_complet[horaire.service].append(horaire_str)
                    if creneau_est_disponible(date, h, mode='livraison'):
                        horaires_par_service_dispo[horaire.service].append(horaire_str)
                except Exception:
                    continue

        if not horaires_par_service_complet['MIDI'] and not horaires_par_service_complet['SOIR']:
            jours_affiches.append({
                'date': date,
                'aucun_service': True
            })
            continue

        jours_affiches.append({
            'date': date,
            'jour': jour_traduit,
            'horaires': horaires_par_service_complet
        })

        horaires_disponibles[date.strftime('%Y-%m-%d')] = horaires_par_service_dispo
        horaires_complets[date.strftime('%Y-%m-%d')] = horaires_par_service_complet

    horaires_json = json.dumps({
        'disponibles': horaires_disponibles,
        'complets': horaires_complets
    })

    jours_fermeture_detailles = JourFermeture.objects.all().order_by('date_debut')

    # Sélectionne la première date/heure dispo pour affichage
    # ✅ Priorise l'estimation calculée par estimer_heure_livraison()
    if not (isinstance(estimation, dict) and 'error' in estimation):
        estimation = timezone.localtime(estimation)
        date_estimee = estimation.date().strftime('%Y-%m-%d')
        heure_estimee_val = estimation.time().strftime('%H:%M')
    else:
        # Fallback si aucune estimation valide (ex: restaurant fermé)
        date_estimee = None
        heure_estimee_val = None
        for date_str, services in horaires_disponibles.items():
            for service, heures in services.items():
                if heures:
                    date_estimee = date_str
                    heure_estimee_val = heures[0]
                    break
            if date_estimee:
                break


    # Formatte une belle chaîne FR, ou fallback
    def formater_date_fr(date_str, heure_str):
        jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{jours_fr[dt.weekday()].capitalize()} {dt.day} {mois_fr[dt.month-1]} {dt.year} à {heure_str}"

    heure_estimee_affichage = ""
    if date_estimee and heure_estimee_val:
        heure_estimee_affichage = formater_date_fr(date_estimee, heure_estimee_val)

    return render(request, 'swigo/programmer_livraison.html', {
        'form': form,
        'date_livraison': today,
        'dates_disponibles': dates_disponibles,
        'jours_affiches': jours_affiches,
        'horaires_disponibles': horaires_json,
        'heure_estimee': heure_estim.strftime('%H:%M'),
        'date_estimee': date_estimee,                        # AJOUT
        'heure_estimee_affichage': heure_estimee_affichage,   # AJOUT
        'jours_fermeture_detailles': jours_fermeture_detailles,
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, time, timedelta
import pytz
import json
import logging

from .models import Commande, HoraireDisponible
from .forms import PickUpTimeForm

logger = logging.getLogger(__name__)
PARIS_TZ = pytz.timezone('Europe/Paris')


def round_down_to_quarter(dt):
    """Arrondit l'heure au quart d'heure inférieur."""
    new_minute = (dt.minute // 15) * 15
    dt = dt.replace(minute=new_minute, second=0, microsecond=0)
    return dt


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.shortcuts import get_object_or_404
from swigo.models import Commande, HoraireDisponible

@csrf_exempt
def choisir_retrait_sur_place(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Requête invalide'}, status=400)

    commande_id = request.session.get('commande_id')
    if not commande_id:
        return JsonResponse({'error': 'Aucune commande en cours.'}, status=400)

    commande = get_object_or_404(Commande, id=commande_id)
    commande.is_commande_a_emporter = True

    now = timezone.localtime()
    today = now.date()
    TEMPS_PREPARATION = 30  # minutes

    # Préparation terminée au plus tôt
    heure_minimale = now + timedelta(minutes=TEMPS_PREPARATION)

    # Choix du service selon l'heure
    if heure_minimale.time() >= time(14, 30):
        service = 'SOIR'
    else:
        service = 'MIDI'

    jours_translation = {
        'MON': 'LUN', 'TUE': 'MAR', 'WED': 'MER', 'THU': 'JEU',
        'FRI': 'VEN', 'SAT': 'SAM', 'SUN': 'DIM'
    }
    jour_traduit = jours_translation.get(today.strftime('%a').upper(), today.strftime('%a').upper())

    horaires_jours = HoraireDisponible.objects.filter(jour=jour_traduit, service=service)

    # Si SOIR : jamain avant 18h30 (même si prépa avant)
    HEURE_DEBUT_SOIR = time(18, 30)
    if service == "SOIR" and heure_minimale.time() < HEURE_DEBUT_SOIR:
        heure_minimale = datetime.combine(today, HEURE_DEBUT_SOIR)

    # Cherche le créneau
    creneau = chercher_prochain_creneau_disponible(
        horaires_jours, today, service, heure_minimale
    )

    if not creneau:
        return JsonResponse({
            'error': 'Aucun créneau de retrait disponible pour aujourd’hui.'
        }, status=400)

    date_creneau, heure_creneau = creneau

    commande.heure_pick_up_specifie = datetime.combine(date_creneau, heure_creneau)
    commande.save()
    request.session['mode_livraison'] = 'retrait'

    return JsonResponse({
        'message': 'Retrait sur place sélectionné',
        'creneau': heure_creneau.strftime('%H:%M'),
        'date': date_creneau.strftime('%Y-%m-%d')
    })



from datetime import datetime, time, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def programmer_pick_up(request):
    # Import des modèles et utilitaires
    from .models import Commande, JourFermeture, HoraireDisponible
    from .forms import PickUpTimeForm
    from .utils import arrondir_au_quart_heure, creneau_est_disponible, estimer_heure_retrait

    jours_translation = {
        'MON': 'LUN', 'TUE': 'MAR', 'WED': 'MER', 'THU': 'JEU',
        'FRI': 'VEN', 'SAT': 'SAM', 'SUN': 'DIM'
    }

    today = timezone.localdate()
    now = timezone.localtime()

    if request.method == 'POST':
        form = PickUpTimeForm(request.POST)
        if form.is_valid():
            heure_retrait = form.cleaned_data.get('heure_retrait')
            date_pick_up = today

            if JourFermeture.est_ferme(date_pick_up):
                motif_obj = JourFermeture.objects.filter(date_debut__lte=date_pick_up, date_fin__gte=date_pick_up).first()
                motif = motif_obj.description if motif_obj else "fermeture exceptionnelle"
                return JsonResponse({'error': f"Le restaurant est fermé ce jour-là : {motif}"}, status=400)

            commande_id = request.POST.get('commande_id') or request.session.get('commande_id')
            if not commande_id:
                return JsonResponse({'error': 'Aucune commande trouvée'}, status=400)

            commande = get_object_or_404(Commande, id=commande_id)
            
            heure_retrait_dt = datetime.combine(date_pick_up, heure_retrait)
            heure_retrait_aware = timezone.make_aware(heure_retrait_dt)
            
            if date_pick_up == now.date() and heure_retrait_aware <= now:
                return JsonResponse({'error': "Vous ne pouvez pas sélectionner un horaire déjà passé"}, status=400)

            if creneau_est_disponible(date_pick_up, heure_retrait, mode='emporter'):
                commande.is_commande_a_emporter = True
                commande.heure_pick_up_specifie = heure_retrait_aware
                commande.save()
                return redirect('swigo:renseigner_commande')
            else:
                return JsonResponse({'error': "Ce créneau est complet, veuillez en choisir un autre."}, status=400)
        return JsonResponse({'error': "Données invalides", 'form_errors': form.errors}, status=400)

    # --- GET METHOD ---

    form = PickUpTimeForm()
    dates_disponibles = [today + timedelta(days=i) for i in range(3)]

    fermetures = JourFermeture.objects.all()
    jours_fermes = {
        d: fermeture.description
        for fermeture in fermetures
        for d in [fermeture.date_debut + timedelta(days=i) for i in range((fermeture.date_fin - fermeture.date_debut).days + 1)]
    }

    commande_id = request.GET.get('commande_id') or request.session.get('commande_id')
    commande = get_object_or_404(Commande, id=commande_id)

    # Heure arrondie au quart d'heure pour filtrage des horaires
    heure_estim = arrondir_au_quart_heure(now)

    # Récupérer l'heure estimée de retrait - CORRECTION IMPORTANTE
    try:
        heure_estimee_retrait = estimer_heure_retrait()
        heure_estimee_str = heure_estimee_retrait.strftime('%H:%M')
        print(f"[PROGRAMMER PICKUP] Heure estimée retrait: {heure_estimee_retrait}")
    except Exception as e:
        print(f"Erreur estimation heure retrait: {e}")
        # Fallback basé sur l'heure actuelle + préparation
        debut_prepa = max(now, now.replace(hour=11, minute=0, second=0, microsecond=0))
        fin_prepa = debut_prepa + timedelta(minutes=30)
        # Arrondi au quart d'heure supérieur
        minute_arrondie = ((fin_prepa.minute // 15) + 1) * 15
        if minute_arrondie >= 60:
            fin_prepa += timedelta(hours=1)
            minute_arrondie = 0
        heure_estimee = fin_prepa.replace(minute=minute_arrondie, second=0, microsecond=0)
        heure_estimee_str = heure_estimee.strftime('%H:%M')
        print(f"[PROGRAMMER PICKUP] Fallback heure estimée: {heure_estimee_str}")

    # Déterminer le service actuel (MIDI ou SOIR) selon l'heure
    service_actuel = 'MIDI' if now.hour < 14 else 'SOIR'

    # Traduction du jour actuel au format modèle (LUN, MAR, ...)
    jour_str = today.strftime('%a').upper()
    jour_traduit = jours_translation.get(jour_str, jour_str)

    # Récupérer les services ouverts aujourd'hui
    services_ouverts = list(HoraireDisponible.objects.filter(jour=jour_traduit).values_list('service', flat=True).distinct())

    # Si le service actuel n'est pas ouvert, basculer vers SOIR si possible, sinon fermer
    ferme = False
    if service_actuel not in services_ouverts:
        if 'SOIR' in services_ouverts:
            service_actuel = 'SOIR'
        else:
            ferme = True

    horaires_disponibles = {}
    horaires_complets = {}
    jours_affiches = []

    horaires_jours = HoraireDisponible.objects.filter(jour__in=list(jours_translation.values()))

    for date in dates_disponibles:
        jour_str = date.strftime('%a').upper()
        jour_traduit = jours_translation.get(jour_str, jour_str)

        if date in jours_fermes:
            jours_affiches.append({
                'date': date,
                'jour': jour_traduit,
                'ferme_exceptionnellement': True,
                'motif_fermeture': jours_fermes[date],
                'horaires': {'MIDI': [], 'SOIR': []}
            })
            continue

        horaires_par_service_dispo = {'MIDI': [], 'SOIR': []}
        horaires_par_service_complet = {'MIDI': [], 'SOIR': []}
        horaires_jour = horaires_jours.filter(jour=jour_traduit)

        if not horaires_jour.exists():
            jours_affiches.append({
                'date': date,
                'jour': jour_traduit,
                'ferme_exceptionnellement': False,
                'motif_fermeture': None,
                'horaires': {'MIDI': [], 'SOIR': []},
                'aucun_service': True
            })
            continue

        # Pour la date du jour, n'affiche que les horaires du service actif
        for horaire in horaires_jour:
            service = horaire.service
            if date == today and service != service_actuel:
                continue
                
            for hstr in horaire.get_horaires():
                try:
                    h = datetime.strptime(hstr, "%H:%M").time()
                    # Pour aujourd'hui, filtrer les horaires passés
                    if date == today and h < heure_estim.time():
                        continue

                    horaires_par_service_complet[service].append(hstr)
                    if creneau_est_disponible(date, h, mode='emporter'):
                        horaires_par_service_dispo[service].append(hstr)
                except Exception as e:
                    print(f"Erreur parsing horaire {hstr}: {e}")
                    continue

        # CORRECTION CRITIQUE : S'assurer que le créneau 22:30 est inclus
        if date == today and service_actuel == 'SOIR':
            # Vérifier manuellement la disponibilité du créneau 22:30
            creneau_22_30 = time(22, 30)
            if creneau_est_disponible(date, creneau_22_30, mode='emporter'):
                if "22:30" not in horaires_par_service_dispo[service_actuel]:
                    horaires_par_service_dispo[service_actuel].append("22:30")
                if "22:30" not in horaires_par_service_complet[service_actuel]:
                    horaires_par_service_complet[service_actuel].append("22:30")
                print(f"[CORRECTION] Créneau 22:30 ajouté manuellement pour aujourd'hui")

        jours_affiches.append({
            'date': date,
            'jour': jour_traduit,
            'ferme_exceptionnellement': False,
            'motif_fermeture': None,
            'horaires': horaires_par_service_complet
        })

        horaires_disponibles[date.strftime('%Y-%m-%d')] = horaires_par_service_dispo
        horaires_complets[date.strftime('%Y-%m-%d')] = horaires_par_service_complet

    # DEBUG : Afficher les horaires disponibles
    print(f"[DEBUG] Horaires disponibles aujourd'hui: {horaires_disponibles.get(today.strftime('%Y-%m-%d'), {})}")
    print(f"[DEBUG] Service actuel: {service_actuel}")
    print(f"[DEBUG] Heure estimée: {heure_estimee_str}")

    return render(request, 'swigo/programmer_pick_up.html', {
        'form': form,
        'date_pick_up': today,
        'jours_affiches': jours_affiches,
        'horaires_disponibles': json.dumps({
            'disponibles': horaires_disponibles,
            'complets': horaires_complets
        }),
        'heure_estimee': heure_estimee_str,
        'service_actuel': service_actuel,
        'ferme': ferme
    })



@csrf_exempt
def verifier_code_promo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip().upper()
            promo = CodePromo.objects.get(code=code)
            if not promo.est_valide():
                raise CodePromo.DoesNotExist
            return JsonResponse({
                'valid': True,
                'reduction': promo.reduction_amount,
                'type': promo.reduction_type
            })
        except (CodePromo.DoesNotExist, json.JSONDecodeError):
            return JsonResponse({'valid': False, 'message': 'Code promo invalide.'})
        except Exception as e:
            logger.error(f'Erreur lors de la vérification du code promo: {e}')
            return JsonResponse({'valid': False, 'message': str(e)})

    return JsonResponse({'valid': False, 'message': 'Méthode de requête non autorisée.'})


def renseigner_commande(request):
    # ✅ Gestion de session et récupération du panier existant s’il y a une commande en session
    if "panier_id" not in request.session:
        logger.debug("[SESSION] 🕵️ Aucun panier_id trouvé en session, tentative via commande_id...")

        commande_id = request.session.get("commande_id")
        if commande_id:
            try:
                commande = Commande.objects.get(id=commande_id)
                if commande.panier:
                    panier = commande.panier
                    request.session["panier_id"] = panier.id
                    logger.debug(f"[SESSION] 🔁 Panier retrouvé via commande ID={commande.id}")
                else:
                    panier = Panier.objects.create(commande=commande)
                    commande.panier = panier
                    commande.save()
                    request.session["panier_id"] = panier.id
                    logger.debug(f"[SESSION] ✅ Panier créé et lié à commande ID={commande.id}")
            except Commande.DoesNotExist:
                logger.warning(f"[SESSION] ❌ Commande introuvable ID={commande_id}")
                panier = Panier.objects.create()
                request.session["panier_id"] = panier.id
                logger.debug(f"[SESSION] ✅ Nouveau panier créé sans commande")
        else:
            panier = Panier.objects.create()
            request.session["panier_id"] = panier.id
            logger.debug(f"[SESSION] ✅ Nouveau panier créé sans commande")

        request.session.modified = True
    else:
        logger.debug(f"[SESSION] 🧾 Panier existant ID={request.session['panier_id']}")

    # 🔢 Ordre personnalisé des catégories
    order = ['menu', 'burger', 'couscous/tajine', 'crousty', 'poulet', 'sides', 'boisson', 'dessert','traiteur']

    ordering = Case(
        *[When(nom__iexact=nom, then=pos) for pos, nom in enumerate(order)],
        default=len(order),
        output_field=IntegerField(),
    )

    categories_sorted = Categorie.objects.all().annotate(
        sort_order=ordering
    ).order_by('sort_order')

    sorted_categories_names = [c.nom for c in categories_sorted]
    logger.debug("Categories sorted with ORM: %s", sorted_categories_names)

    plats = Plat.objects.all()

    return render(request, 'swigo/renseigner_commande.html', {
        'categories': categories_sorted,
        'plats': plats
    })


from django.db.models import Case, When, IntegerField



def get_categories(request):
    # Liste qui définit l'ordre spécifique des catégories
    order = ['menu', 'burger', 'crousty', 'couscous/tajine', 'poulet', 'sides', 'boisson', 'dessert','traiteur']

    # Créer une liste de conditions pour l'annotation
    ordering = Case(
        *[When(nom__iexact=nom, then=pos) for pos, nom in enumerate(order)],
        default=len(order),
        output_field=IntegerField(),
    )

    # Annoter et ordonner les catégories
    categories_sorted = Categorie.objects.all().annotate(
        sort_order=ordering
    ).order_by('sort_order')

    # Journaliser l'ordre des catégories triées
    sorted_categories_names = [c.nom for c in categories_sorted]
    logger.debug("Categories sorted with ORM: %s", sorted_categories_names)

    # Récupérez les plats si nécessaire
    plats = Plat.objects.all()  # Ajustez selon vos besoins

    return render(request, 'swigo/renseigner_commande.html', {
        'categories': categories_sorted,
        'plats': plats  # Passez les plats au template si nécessaire
    })


from django.http import JsonResponse

import json
from django.http import JsonResponse
from django.utils.html import escape


from django.utils.text import slugify
from django.utils.html import escape
from django.http import JsonResponse
from .models import Plat, Categorie

def plats_par_categorie_ajax(request, categorie_nom):
    print(f"Requête pour la catégorie : {categorie_nom}")

    # Déslugification à partir des choix déclarés dans le modèle
    mapping = {slugify(code): code for code, _ in Categorie.SPECIALITES}
    vrai_nom = mapping.get(categorie_nom, categorie_nom)
    print(f"[DEBUG] Nom réel de la catégorie après déslugification : {vrai_nom}")


    plats = Plat.objects.filter(categorie__nom__iexact=vrai_nom)

    if plats.exists():
        print(f"Nombre de plats trouvés : {plats.count()}")
    else:
        print(f"Aucun plat trouvé pour la catégorie : {vrai_nom}")

    plats_list = []
    for plat in plats:
        photo_url = plat.photo.url if plat.photo else ''
        print(f"Plat trouvé : {plat.nom} - URL de la photo : {photo_url}")

        plats_list.append({
            'id': plat.id,
            'nom': escape(plat.nom),
            'description_courte': escape(plat.description_courte).replace('\r\n', '\\n').replace('\n', '\\n'),
            'description_longue': escape(plat.description_longue).replace('\r\n', '\\n').replace('\n', '\\n'),
            'prix_unitaire_ht': str(plat.prix_unitaire_ht),
            'prix_unitaire_ttc': str(plat.prix_unitaire_ttc),
            'photo_url': photo_url,
        })

    print(f"Réponse JSON envoyée : {plats_list}")
    return JsonResponse({'plats': plats_list})





from django.http import JsonResponse
from swigo.models import Plat, Option

def options_par_plat_ajax(request, plat_id):
    try:
        plat = Plat.objects.get(id=plat_id)
        options = Option.objects.filter(plat=plat).order_by('categorie', 'ordre', 'nom_option')
        
        # Définir l'ordre d'affichage des catégories
        ordre_categories = ['supp_viande', 'supp_fromage', 'supp_croustillant', 'supp_sauce', 'autre']
        
        # Grouper les options par catégorie
        options_par_categorie = {}
        for option in options:
            categorie_display = option.get_categorie_display()
            if categorie_display not in options_par_categorie:
                options_par_categorie[categorie_display] = []
            
            options_par_categorie[categorie_display].append({
                'id': option.id,
                'nom_option': option.nom_option,
                'prix_unitaire': str(option.prix_unitaire_ttc),
                'categorie': option.categorie,
                'ordre': option.ordre
            })
        
        # Réorganiser selon l'ordre défini
        options_triees = {}
        for categorie_code in ordre_categories:
            categorie_display = dict(Option.CATEGORIE_OPTION_CHOICES).get(categorie_code)
            if categorie_display in options_par_categorie:
                options_triees[categorie_display] = options_par_categorie[categorie_display]
        
        # Ajouter les catégories non définies dans l'ordre
        for categorie_display, options_list in options_par_categorie.items():
            if categorie_display not in options_triees:
                options_triees[categorie_display] = options_list
        
        return JsonResponse({
            'success': True,
            'options_par_categorie': options_triees,
            'plat_nom': plat.nom
        })
        
    except Plat.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Plat non trouvé'})


def get_cart_totals(request):
    """Calcule les totaux du panier basé sur la session"""
    try:
        # Récupérer le panier avec session_key
        if request.user.is_authenticated:
            session_key = str(request.user.id)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
        
        panier = Panier.objects.get(session_key=session_key)
        
        # Calculer les totaux
        panier.calculate_total_price()
        
        return {
            'sous_total': float(panier.sous_total),
            'frais_livraison': float(panier.frais_livraison_effectif),
            'frais_gestion': float(panier.frais_gestion),
            'reduction': float(panier.promotion or 0),
            'prix_total': float(panier.prix_total)
        }
        
    except Panier.DoesNotExist:
        return {
            'sous_total': 0.0,
            'frais_livraison': 0.0,
            'frais_gestion': 0.0,
            'reduction': 0.0,
            'prix_total': 0.0
        }

def ajouter_au_panier(request):
    if request.method == 'POST':
        article_panier = None
        try:
            data = json.loads(request.body)
            plat_id = data.get('plat_id')
            options_selectionnees = data.get('options', [])
            accompagnement_id = data.get('accompagnement')

            print(f"📥 Données reçues - Plat: {plat_id}, Options: {options_selectionnees}, Accompagnement: {accompagnement_id}")

            # Validation
            if not plat_id:
                return JsonResponse({'success': False, 'message': 'Plat ID manquant'}, status=400)

            # Récupérer le plat
            try:
                plat = Plat.objects.get(id=plat_id)
                print(f"✅ Plat trouvé: {plat.nom}")
            except Plat.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Plat non trouvé'}, status=404)

            # Récupérer ou créer le panier avec session_key
            if request.user.is_authenticated:
                session_key = str(request.user.id)
            else:
                if not request.session.session_key:
                    request.session.create()
                session_key = request.session.session_key

            print(f"🔑 Session key: {session_key}")

            panier, created = Panier.objects.get_or_create(session_key=session_key)
            print(f"✅ Panier: {panier.id} (créé: {created})")

            # ÉTAPE 1: Créer l'article de base SANS prix_unitaire
            article_panier = ArticlePanier(
                panier=panier,
                plat=plat,
                quantite=1,
                prix_total=plat.prix_unitaire_ttc  # Prix initial basé sur le plat
            )
            
            # SAUVEGARDER pour obtenir l'ID
            article_panier.save()
            print(f"✅ Article créé avec ID: {article_panier.id}")

            # ÉTAPE 2: Ajouter les options (many-to-many)
            if options_selectionnees:
                print(f"🔄 Ajout des options: {options_selectionnees}")
                options_objets = Option.objects.filter(id__in=options_selectionnees)
                if options_objets.exists():
                    article_panier.options.add(*options_objets)
                    print(f"✅ Options ajoutées: {options_objets.count()}")

            # ÉTAPE 3: Gérer l'accompagnement
            if accompagnement_id and accompagnement_id != 'undefined':
                try:
                    accompagnement = Accompagnement.objects.get(id=accompagnement_id)
                    article_panier.accompagnement = accompagnement
                    article_panier.save(update_fields=['accompagnement'])
                    print(f"✅ Accompagnement ajouté: {accompagnement.nom}")
                except Accompagnement.DoesNotExist:
                    print(f"❌ Accompagnement ID {accompagnement_id} non trouvé")

            # ÉTAPE 4: Calculer le prix final avec la méthode du modèle
            article_panier.calculate_total_price()
            print(f"💰 Prix final calculé: {article_panier.prix_total}€")

            # ÉTAPE 5: Mettre à jour les totaux du panier
            panier.calculate_total_price()
            
            # ÉTAPE 6: Récupérer les données mises à jour
            cart_items = get_cart_items(panier)
            totals = get_cart_totals(request)

            return JsonResponse({
                'success': True,
                'message': 'Article ajouté au panier',
                'cart_items': cart_items,
                'totals': totals,
                'article_id': article_panier.id
            })
            
        except Exception as e:
            print(f"❌ Erreur ajouter_au_panier: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Nettoyer en cas d'erreur
            if article_panier and article_panier.id:
                try:
                    article_panier.delete()
                    print("🧹 Article nettoyé après erreur")
                except:
                    pass
            
            return JsonResponse({
                'success': False, 
                'message': f'Erreur lors de l\'ajout au panier: {str(e)}'
            }, status=500)








@csrf_exempt
def remove_item_from_cart(request):
    if request.method == "POST":
        data = json.loads(request.body)
        article_id = data.get('article_id')

        try:
            # Récupérer l'article du panier
            article = ArticlePanier.objects.get(id=article_id)
            panier = article.panier
            article.delete()  # Supprimer l'article

            # Récupérer la commande à partir de la session
            commande_id = request.session.get('commande_id')
            if commande_id:
                commande = Commande.objects.get(id=commande_id)
                
                # Vérifier si la commande a un panier
                if commande.panier:
                    # Recalculer le prix total du panier après la suppression
                    commande.panier.calculate_total_price()

                    # Vérifier s'il y a un code promo appliqué sur le panier
                    if commande.panier.code_promo:
                        code_promo = commande.panier.code_promo
                        reduction = f"{commande.panier.promotion:.2f}" if commande.panier.promotion else "0.00"
                        code_promo_data = {
                            'code': code_promo.code,
                            'reduction_type': code_promo.reduction_type,
                            'reduction_amount': reduction,
                        }
                    else:
                        code_promo_data = None

                    # Récupérer les articles mis à jour dans le panier
                    cart_items = get_cart_items(commande.panier)
                    return JsonResponse({
                        'success': True,
                        'cart_items': cart_items,
                        'totals': {
                            'sous_total': f"{commande.panier.sous_total:.2f}",
                            'frais_livraison': f"{commande.panier.frais_livraison_effectif:.2f}",
                            'promotion': f"{commande.panier.promotion:.2f}" if commande.panier.promotion else "0.00",
                            'prix_total': f"{commande.panier.prix_total:.2f}"
                        },
                        'code_promo': code_promo_data
                    })

            return JsonResponse({'error': 'Commande non trouvée'}, status=400)
        
        except ArticlePanier.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Article non trouvé'}, status=404)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)






from decimal import Decimal

@csrf_exempt
def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        article_id = data.get('article_id')
        delta = data.get('delta')

        if not isinstance(delta, int):
            return JsonResponse({'success': False, 'message': 'Delta doit être un entier'}, status=400)

        try:
            article = ArticlePanier.objects.get(id=article_id)
            article.quantite += delta

            if article.quantite <= 0:
                article.delete()  # Supprimer l'article si la quantité est inférieure ou égale à 0
            else:
                # Recalculer le prix total après la mise à jour de la quantité
                article.calculate_total_price()
                article.save()

            # Récupérer le panier et recalculer les totaux
            panier = article.panier
            panier.calculate_total_price()  # Recalculer le prix total du panier avec la promotion si applicable

            cart_items = get_cart_items(panier)
            
            # Assurer que les données sur la réduction sont renvoyées
            reduction = panier.promotion if panier.promotion else Decimal('0.00')
            frais_livraison = panier.frais_livraison_effectif
            sous_total = panier.sous_total
            prix_total = panier.prix_total

            # Vérifier s'il y a un code promo actif
            code_promo_data = None
            if panier.code_promo and panier.code_promo.est_valide():
                code_promo_data = {
                    'code': panier.code_promo.code,
                    'reduction_type': panier.code_promo.reduction_type,
                    'reduction_amount': str(panier.promotion),
                }

            return JsonResponse({
                'success': True,
                'cart_items': cart_items,
                'totals': {
                    'sous_total': f"{sous_total:.2f}",
                    'frais_livraison': f"{frais_livraison:.2f}",
                    'reduction': f"{reduction:.2f}",
                    'prix_total': f"{prix_total:.2f}"
                },
                'code_promo': code_promo_data
            })
        except ArticlePanier.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Article non trouvé'}, status=404)
    else:
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)







def add_options_to_article(article, options_ids):
    """Ajoute les options à l'article en vérifiant leur existence."""
    options = Option.objects.filter(id__in=options_ids)
    found_option_ids = options.values_list('id', flat=True)
    invalid_option_ids = set(options_ids) - set(found_option_ids)

    if invalid_option_ids:
        return JsonResponse({
            'success': False,
            'message': f'Options avec ids {list(invalid_option_ids)} non trouvées'
        }, status=400)

    # Ajout des options valides à l'article
    article.options.set(options)
    return True  # Retourne True pour indiquer que tout s'est bien passé


def calculate_total_price(plat, options_ids):
    """Calcule le prix total d'un plat avec les options."""
    prix_total = plat.calculer_prix_vente_ttc()  # Utiliser le prix TTC
    options = Option.objects.filter(id__in=options_ids)

    # Ajouter le prix de chaque option au prix total
    prix_total += sum(option.prix_unitaire for option in options)
    
    return prix_total


import logging

logger = logging.getLogger(__name__)

from collections import Counter

from collections import Counter
from decimal import Decimal
from .models import ArticlePanier

from collections import Counter  # Import global pour éviter les problèmes de portée

from collections import Counter
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from collections import Counter
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def get_cart_items(panier):
    print("🔍 get_cart_items appelé avec panier:", panier)
    logger.debug(f"[get_cart_items] Panier ID = {panier.id if panier else 'None'}")

    cart_items = []

    articles = (
        ArticlePanier.objects
        .filter(panier=panier)
        .select_related(
            'plat__categorie',
            'salade_personnalisee__base',
            'salade_personnalisee__sauce',
            'couscous_personnalise',
            'couscous_personnalise__formule',
            'menu',
            'accompagnement'
        )
        .prefetch_related(
            'options',
            'options_crousty',
            'options_poulet',
            'salade_personnalisee__proteines',
            'salade_personnalisee__garnitures',
            'salade_personnalisee__toppings',
            'salade_personnalisee__supplement',
            'couscous_personnalise__choixviandecouscous_set__viande',
            'couscous_personnalise__accompagnements',
            'choix_menu__plat_choisi',
            'choix_menu__salade',
            'choix_menu__couscous',
            'choix_menu__couscous__choixviandecouscous_set__viande',
            'choix_menu__couscous__accompagnements'
        )
    )

    print(f"📦 {articles.count()} article(s) trouvé(s) dans le panier.")
    logger.debug(f"[get_cart_items] {articles.count()} articles récupérés pour le panier {panier.id}")

    for article in articles:
        logger.debug(f"[get_cart_items] Traitement article #{article.id} - Plat: {getattr(article.plat, 'nom', 'Personnalisé')}")

        options_list = []
        plat_nom = "Inconnu"
        categorie_nom = "Autres"
        accompagnement_info = None
        viandes_couscous = []

        # 🆕 CROUSTY
        if article.plat and article.plat.type_plat == 'crousty' and article.options_crousty.exists():
            plat_nom = article.plat.nom
            categorie_nom = article.plat.categorie.nom if article.plat.categorie else "crousty"
            options_par_categorie = {}
            for option in article.options_crousty.all():
                options_par_categorie.setdefault(option.categorie, [])
                txt = f"+{option.nom}"
                if option.prix_supplement > 0:
                    txt += f" (+{option.prix_supplement}€)"
                options_par_categorie[option.categorie].append(txt)
            for cat in ['fromage', 'sauce_rouge', 'sauce_erc', 'prot_veggie', 'supplement']:
                options_list.extend(options_par_categorie.get(cat, []))

        # 🆕 POULET
        elif article.plat and article.plat.type_plat == 'poulet':
            plat_nom = article.plat.nom
            categorie_nom = article.plat.categorie.nom if article.plat.categorie else "poulet"
            print(f"🐔 Traitement poulet personnalisé: {plat_nom}")

            if hasattr(article, 'options_poulet_avec_quantites') and article.options_poulet_avec_quantites:
                options_counter = Counter(article.options_poulet_avec_quantites)
                print(f"   - Options avec quantités: {dict(options_counter)}")
                options_avec_noms = {}
                for opt_id, quantite in options_counter.items():
                    try:
                        opt = PouletOption.objects.get(id=opt_id)
                        options_avec_noms[opt_id] = {
                            'nom': opt.nom,
                            'quantite': quantite,
                            'categorie': opt.categorie,
                            'prix_supplement': opt.prix_supplement
                        }
                    except PouletOption.DoesNotExist:
                        continue

                for opt in options_avec_noms.values():
                    txt = f"+{opt['nom']}"
                    if opt['prix_supplement'] > 0:
                        txt += f" (+{opt['prix_supplement']}€)"
                    if opt['quantite'] > 1:
                        txt += f" × {opt['quantite']}"
                    options_list.append(txt)
            else:
                for opt in article.options_poulet.all():
                    txt = f"+{opt.nom}"
                    if opt.prix_supplement > 0:
                        txt += f" (+{opt.prix_supplement}€)"
                    options_list.append(txt)

        # 🥘 COUSCOUS PERSONNALISÉ (direct)
        elif article.couscous_personnalise:
            couscous = article.couscous_personnalise
            couscous.calculate_prix_total()
            plat_nom = article.nom_personnalise or couscous.formule.nom
            categorie_nom = "couscous"

            incluses, supplements = [], []
            viandes_couscous = []

            for choix in couscous.choixviandecouscous_set.all():
                nom = choix.viande.nom
                supp = choix.viande.supplement_extra if not choix.est_incluse else choix.viande.supplement_inclus
                if choix.est_incluse:
                    incluses.append(nom)
                else:
                    supplements.append(f"+{nom} (+{supp} €)")

                viandes_couscous.append({
                    'nom': nom,
                    'portion': choix.viande.portion,
                    'est_incluse': choix.est_incluse,
                    'supplement': str(supp)
                })

            incluses_count = Counter(incluses)
            for nom, count in incluses_count.items():
                options_list.append(f"{nom} × {count}" if count > 1 else nom)

            if couscous.option_xl:
                options_list.append("+Option XL")

            for acc in couscous.accompagnements.all():
                options_list.append(f"+{acc.nom}")

            options_list.extend(supplements)

        # 🍱 MENU (y compris menu couscous)
        elif article.menu:
            menu = article.menu
            plat_nom = menu.nom
            categorie_nom = "menu"
            
            print(f"🍱 Traitement menu: {plat_nom}")
            
            # Dictionnaire pour organiser les choix par rôle
            choix_par_role = {}
            
            for choix in article.choix_menu.all():
                print(f"   - Choix rôle: {choix.role}")
                
                # 🆕 GESTION SPÉCIALE COUSCOUS DANS LE MENU
                if choix.couscous:
                    print(f"     🍛 Couscous trouvé dans le menu: {choix.couscous}")
                    
                    # Récupérer les viandes du couscous
                    for vc in choix.couscous.choixviandecouscous_set.all():
                        nom_viande = vc.viande.nom
                        if vc.est_incluse:
                            choix_par_role.setdefault('viande', []).append(nom_viande)
                            viandes_couscous.append(nom_viande)
                            print(f"       🥩 Viande incluse: {nom_viande}")
                        else:
                            supp_text = f"+{nom_viande} (+{vc.viande.supplement_inclus}€)"
                            choix_par_role.setdefault('viande', []).append(supp_text)
                            viandes_couscous.append(supp_text)
                            print(f"       🥩 Viande supplément: {supp_text}")
                    
                    # 🆕 CORRECTION : GESTION UNIQUE DES ACCOMPAGNEMENTS
                    for acc in choix.couscous.accompagnements.all():
                        choix_par_role.setdefault('accompagnement', []).append(acc.nom)
                        print(f"       🍟 Accompagnement: {acc.nom}")
                    
                    if choix.couscous.option_xl:
                        choix_par_role.setdefault('option', []).append("+Option XL")
                        print(f"       📏 Option XL")
                    
                    continue
                
                # Gestion des choix classiques
                nom = (
                    choix.plat_choisi.nom if choix.plat_choisi else
                    choix.info_text if choix.info_text else
                    "+Salade personnalisée" if choix.salade else None
                )
                
                if nom:
                    choix_par_role.setdefault(choix.role, []).append(nom)
                    print(f"       ✅ {choix.role}: {nom}")

            # 🆕 CONSTRUCTION OPTIONS ORGANISÉES PAR RÔLE
            # Ordre d'affichage préférentiel
            ordre_roles = ['viande', 'accompagnement', 'boisson', 'dessert', 'entree', 'plat', 'option']

            # 🆕 MAPPING COMPLET DES RÔLES
            role_labels = {
                'plat': 'Plat',
                'accompagnement': 'Accompagnement', 
                'boisson': 'Boisson',
                'dessert': 'Dessert',
                'entree': 'Entrée',
                'viande': 'Viande',
                'cookie': 'Cookie',
                'option': 'Option',
                'supplement': 'Supplément'
            }

            for role in ordre_roles:
                if role in choix_par_role:
                    noms = choix_par_role[role]
                    
                    if role == 'accompagnement':
                        # Accompagnements inclus - pas de "+"
                        options_list.extend(noms)
                    elif role == 'boisson':
                        for nom in noms:
                            options_list.append(f"🥤 {nom}")
                    elif role == 'dessert':
                        for nom in noms:
                            options_list.append(f"🍪 {nom}")
                    elif role == 'viande':
                        options_list.extend(noms)
                    else:
                        # Rôles génériques avec label sécurisé
                        label = role_labels.get(role, role.capitalize())
                        for nom in noms:
                            options_list.append(f"{label}: {nom}")

            # Ajouter les rôles non traités dans l'ordre préférentiel
            roles_restants = [r for r in choix_par_role.keys() if r not in ordre_roles]
            for role in roles_restants:
                noms = choix_par_role[role]
                label = role_labels.get(role, role.capitalize())
                for nom in noms:
                    options_list.append(f"{label}: {nom}")

            print(f"   ✅ Options finales menu: {options_list}")

        # 🧂 SALADE
        elif article.salade_personnalisee:
            salade = article.salade_personnalisee
            salade.calculate_prix_total()
            plat_nom = "Salade personnalisée"
            categorie_nom = "salade"
            if salade.base:
                options_list.append(f"+{salade.base.nom}")
            for label, queryset in [
                ("Protéines", salade.proteines.all()),
                ("Garnitures", salade.garnitures.all()),
                ("Toppings", salade.toppings.all()),
                ("Suppléments", salade.supplement.all())
            ]:
                for item in queryset:
                    nom = f"+{item.nom}"
                    supp = item.prix_supplement_salade or Decimal('0.00')
                    if supp > 0:
                        nom += f" (+{supp:.2f} €)"
                    options_list.append(nom)
            if salade.sauce:
                txt = f"+{salade.sauce.nom}"
                supp = salade.sauce.prix_supplement_salade or Decimal('0.00')
                if supp > 0:
                    txt += f" (+{supp:.2f} €)"
                options_list.append(txt)

        # 🍔 PLAT CLASSIQUE
        elif article.plat:
            plat_nom = article.plat.nom
            categorie_nom = article.plat.categorie.nom if article.plat.categorie else "Autres"
            for opt in article.options.all():
                nom = opt.nom_option
                if not nom.startswith('+'):
                    nom = '+' + nom
                if opt.prix_unitaire_ttc and opt.prix_unitaire_ttc > 0:
                    nom += f" (+{opt.prix_unitaire_ttc} €)"
                options_list.append(nom)

        # 🍟 ACCOMPAGNEMENT
        if article.accompagnement:
            accompagnement_info = {
                'id': article.accompagnement.id,
                'nom': article.accompagnement.nom,
                'prix': str(article.accompagnement.prix_supplement or '0.00')
            }

        cart_item = {
            'article_id': article.id,
            'plat_nom': plat_nom,
            'categorie_nom': categorie_nom,
            'quantite': article.quantite,
            'prix_total': str(article.prix_total),
            'options': options_list,
            'accompagnement': accompagnement_info,
            'tous_les_champs': {
                'accompagnement_id': article.accompagnement.id if article.accompagnement else None,
                'nom_accompagnement': article.accompagnement.nom if article.accompagnement else None,
                'prix_accompagnement': str(article.accompagnement.prix_supplement) if article.accompagnement else '0.00',
                'options_poulet': article.options_poulet_avec_quantites if hasattr(article, 'options_poulet_avec_quantites') and article.options_poulet_avec_quantites else [opt.id for opt in article.options_poulet.all()],
                'options_crousty': [opt.id for opt in article.options_crousty.all()] if article.plat and article.plat.type_plat == 'crousty' else [],
                'options_classiques': [opt.id for opt in article.options.all()] if article.options.exists() else [],
                'viandes_couscous': viandes_couscous,
                'est_menu': bool(article.menu),
                'menu_id': article.menu.id if article.menu else None
            }
        }

        print(f"📟 Article panier #{article.id}: {plat_nom}")
        print(f"   🎯 Catégorie: {categorie_nom}")
        print(f"   📋 Options: {options_list}")
        print(f"   🥩 Viandes couscous: {viandes_couscous}")
        logger.debug(f"[get_cart_items] Article #{article.id} structuré: {cart_item}")
        cart_items.append(cart_item)

    print("✅ Cart final avec", len(cart_items), "articles")
    logger.debug(f"[get_cart_items] Cart_items complet: {cart_items}")
    return cart_items

from decimal import Decimal
from django.http import JsonResponse


def afficher_panier(request):
    if not request.session.session_key:
        request.session.create()

    commande_id = request.session.get('commande_id')
    if not commande_id:
        return JsonResponse({'error': 'Aucune commande associée'}, status=400)

    try:
        commande = Commande.objects.get(id=commande_id)
        panier = commande.panier
        if not panier:
            return JsonResponse({'error': 'Aucun panier associé à la commande'}, status=400)

        # Appliquer le code promo
        code_promo_code = request.session.get('code_promo')
        code_promo = panier.apply_code_promo(code_promo_code)


        # Retourner les données
        return JsonResponse({
            'cart_items': get_cart_items(panier),
            'totals': {
                'sous_total': f"{panier.sous_total:.2f}",
                'frais_livraison': f"{panier.frais_livraison_effectif:.2f}",
                'reduction': f"{panier.promotion:.2f}",
                'prix_total': f"{panier.prix_total:.2f}"
            },
            'code_promo': {
                'code': code_promo.code,
                'reduction_type': code_promo.reduction_type,
                'reduction_amount': f"{code_promo.reduction_amount}"
            } if code_promo else None
        })

    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande non trouvée'}, status=400)



@csrf_exempt
def appliquer_code_promo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code_promo_input = data.get('code_promo', '').strip().upper()

        try:
            code_promo = CodePromo.objects.get(code=code_promo_input)
            if not code_promo.est_valide():
                return JsonResponse({'success': False, 'message': 'Ce code promo est expiré ou invalide.'})

            # Stocker le code promo dans la session
            request.session['code_promo'] = code_promo.code

            # Récupérer la commande à partir de la session
            commande_id = request.session.get('commande_id')
            if not commande_id:
                return JsonResponse({'success': False, 'message': 'Commande non trouvée'}, status=400)

            try:
                # Récupérer la commande
                commande = Commande.objects.get(id=commande_id)

                # Vérifier si la commande a un panier associé
                panier = commande.panier
                if not panier:
                    return JsonResponse({'success': False, 'message': 'Aucun panier associé à la commande'}, status=400)

                # Appliquer le code promo sur le panier et recalculer les totaux
                panier.code_promo = code_promo
                panier.calculate_total_price()  # Cette méthode gère déjà les réductions et le prix total

                # Calculer la réduction basée sur le sous-total et les frais de livraison
                sous_total = panier.sous_total
                frais_livraison = panier.frais_livraison_effectif
                reduction = panier.promotion  # La réduction calculée par `calculate_total_price()`
                prix_total = panier.prix_total

                # Sauvegarder le panier après application de la réduction
                panier.save()

                # Récupérer les articles du panier
                cart_items = get_cart_items(panier)

                return JsonResponse({
                    'success': True,
                    'cart_items': cart_items,
                    'totals': {
                        'sous_total': f"{sous_total:.2f}",
                        'frais_livraison': f"{frais_livraison:.2f}",
                        'reduction': f"{reduction:.2f}",
                        'prix_total': f"{prix_total:.2f}"
                    },
                    'code_promo': {
                        'code': code_promo.code,
                        'reduction_type': code_promo.reduction_type,
                        'reduction_amount': str(code_promo.reduction_amount),
                    }
                })

            except Commande.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Commande non trouvée'}, status=400)

        except CodePromo.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ce code promo est invalide.'})
    else:
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})






from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import stripe
import logging
from .models import Client, Commande  # Assure-toi d'avoir ces modèles

logger = logging.getLogger(__name__)

# --- Fonctions utilitaires ---

def extraire_donnees_client(data):
    """Extraction et validation des données client depuis la requête JSON."""
    nom = data.get('nom')
    prenom = data.get('prenom')
    numero_telephone = data.get('numero_telephone')
    adresse_facturation = data.get('adresse_facturation')
    email = data.get('email')

    if not (nom and prenom and numero_telephone and email):
        raise ValueError("Informations client manquantes")

    return nom, prenom, numero_telephone, adresse_facturation, email


def creer_ou_mettre_a_jour_client(nom, prenom, numero_telephone, adresse_facturation, email,
                                  consent_sms=False, consent_email=False, consent_cookies=False):
    """
    Recherche un client existant sans jamais écraser ses données.
    Recherche par priorité : email → téléphone → nom+prénom.
    Ne met pas à jour un client existant, conserve toutes les nouvelles infos dans la commande.
    Enregistre les consentements uniquement si un nouveau client est créé.
    """
    client = None

    if email:
        client = Client.objects.filter(email=email).first()

    if not client and numero_telephone:
        client = Client.objects.filter(numero_telephone=numero_telephone).first()

    if not client:
        client = Client.objects.filter(nom=nom, prenom=prenom).first()

    if client:
        logger.info(f"Client existant reconnu : {client.nom} {client.prenom} (id={client.id})")
        return client

    # Aucun client trouvé → création avec consentements
    client = Client.objects.create(
        nom=nom,
        prenom=prenom,
        numero_telephone=numero_telephone,
        adresse_facturation=adresse_facturation,
        email=email,
        consent_sms=consent_sms,
        consent_email=consent_email,
        consent_cookies=consent_cookies
    )
    logger.info(f"Nouveau client créé : {client.nom} {client.prenom} (id={client.id})")
    return client







def obtenir_paiements_possibles(commande):
    client = commande.client

    is_nouveau = not Commande.objects.filter(
        client=client,
        is_paid=True
    ).exclude(id=commande.id).exists()

    if commande.is_commande_a_emporter:
        paiements = [
            {'id': 'stripe', 'label': 'Carte Bancaire'},
            {'id': 'especes_retrait', 'label': 'Espèces au retrait'},
            {'id': 'ticket_retrait', 'label': 'Ticket resto au retrait'},
        ]
    else:
        paiements = [
            {'id': 'stripe', 'label': 'Carte Bancaire'},
            {'id': 'especes_livraison', 'label': 'Espèces à la livraison'},
            {'id': 'ticket_livraison', 'label': 'Ticket resto à la livraison'},
        ]

    # Si c’est un nouveau client, marquer tous sauf CB comme désactivés
    if is_nouveau:
        for p in paiements:
            if p['id'] != 'stripe':
                p['disabled'] = True

    return paiements




def preparer_items_stripe(panier, commande=None):
    """Prépare la liste des items à envoyer à Stripe pour paiement."""
    print(f"🛒 [DEBUG] === DÉBUT PREPARER_ITEMS_STRIPE ===")
    print(f"🛒 [DEBUG] Panier ID: {panier.id}")
    print(f"🛒 [DEBUG] Frais livraison: {panier.frais_livraison}")
    
    line_items = []
    articles_count = panier.articlepanier_set.count()
    print(f"🛒 [DEBUG] Nombre d'articles dans le panier: {articles_count}")

    if articles_count == 0:
        print("❌ [DEBUG] PANIER VIDE - aucun article trouvé")
        return line_items

    for index, article in enumerate(panier.articlepanier_set.all()):
        print(f"🛒 [DEBUG] --- Article {index + 1} ---")
        print(f"🛒 [DEBUG] Article ID: {article.id}")
        print(f"🛒 [DEBUG] Quantité: {article.quantite}")
        print(f"🛒 [DEBUG] Prix total article: {article.prix_total}")
        
        nom_produit = ""
        prix_unitaire = None

        # ========== PLAT CLASSIQUE ==========
        if article.plat:
            print(f"🛒 [DEBUG] Type: Plat classique")
            print(f"🛒 [DEBUG] Plat: {article.plat.nom}")
            print(f"🛒 [DEBUG] Prix plat: {article.plat.prix_unitaire_ttc}")
            nom_produit = article.plat.nom
            
            # 🆕 CORRECTION : UTILISER LE PRIX TOTAL DE L'ARTICLE
            prix_unitaire = article.prix_total / article.quantite
            print(f"🛒 [DEBUG] Prix unitaire final (avec options): {prix_unitaire}")
            
            options_text = ', '.join(option.nom_option for option in article.options.all())
            if options_text:
                nom_produit += f" ({options_text})"
                print(f"🛒 [DEBUG] Options: {options_text}")

        # ========== MENU PERSONNALISÉ ==========
        elif article.menu:
            print(f"🛒 [DEBUG] Type: Menu personnalisé")
            print(f"🛒 [DEBUG] Menu: {article.menu.nom}")
            print(f"🛒 [DEBUG] Prix menu de base: {article.menu.prix_ttc}")
            nom_produit = article.menu.nom
            
            # 🆕 CORRECTION : UTILISER LE PRIX TOTAL DE L'ARTICLE (AVEC SUPPLÉMENTS)
            prix_unitaire = article.prix_total / article.quantite
            print(f"🛒 [DEBUG] Prix unitaire final (avec suppléments): {prix_unitaire}")

            # On reconstitue le détail
            details = []
            for choix in article.choix_menu.all():
                if choix.plat_choisi:
                    details.append(f"{choix.get_role_display()} : {choix.plat_choisi.nom}")
                elif getattr(choix, "info_text", None):
                    details.append(f"{choix.role} : {choix.info_text}")
                elif getattr(choix, "accompagnement", None):
                    details.append(f"accompagnement : {choix.accompagnement.nom}")
                elif getattr(choix, "viande", None):
                    details.append(f"viande : {choix.viande.nom}")
                elif choix.salade:
                    details.append(f"{choix.get_role_display()} : Salade personnalisée")
                elif choix.couscous:
                    details.append(f"{choix.get_role_display()} : Couscous personnalisé")
            
            if details:
                nom_produit += " (" + "; ".join(details) + ")"
                print(f"🛒 [DEBUG] Détails menu: {details}")
            
            # 🆕 AJOUTER LES SUPPLÉMENTS DANS LA DESCRIPTION
            if hasattr(article, 'supplements_menu') and article.supplements_menu:
                total_supplements = Decimal(article.supplements_menu.get('total_supplements', 0))
                if total_supplements > 0:
                    nom_produit += f" [Supplément: +{total_supplements}€]"
                    print(f"🛒 [DEBUG] Suppléments appliqués: +{total_supplements}€")

        # ========== SALADE PERSONNALISÉE ==========
        elif article.salade_personnalisee:
            print(f"🛒 [DEBUG] Type: Salade personnalisée")
            print(f"🛒 [DEBUG] Prix salade: {article.salade_personnalisee.prix_total}")
            nom_produit = "Salade personnalisée"
            
            # 🆕 CORRECTION : UTILISER LE PRIX TOTAL
            prix_unitaire = article.prix_total / article.quantite

        # ========== COUSCOUS PERSONNALISÉ ==========
        elif article.couscous_personnalise:
            print(f"🛒 [DEBUG] Type: Couscous personnalisé")
            print(f"🛒 [DEBUG] Prix couscous: {article.couscous_personnalise.prix_total}")
            nom_produit = "Couscous personnalisé"
            
            # 🆕 CORRECTION : UTILISER LE PRIX TOTAL
            prix_unitaire = article.prix_total / article.quantite

        else:
            print(f"🛒 [DEBUG] Type: Produit générique")
            print(f"🛒 [DEBUG] Prix total: {article.prix_total}")
            nom_produit = "Produit"
            
            # 🆕 CORRECTION : UTILISER LE PRIX TOTAL
            prix_unitaire = article.prix_total / article.quantite

        # Sécurité : ne pas envoyer à Stripe un produit à 0€
        print(f"🛒 [DEBUG] Prix unitaire final pour Stripe: {prix_unitaire}")
        if not prix_unitaire or prix_unitaire <= 0:
            print(f"❌ [DEBUG] Article ignoré car prix nul : {nom_produit}")
            continue

        # Préparation de l'item Stripe
        line_item = {
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': nom_produit[:127]},  # Stripe max 127 caractères
                'unit_amount': int(prix_unitaire * 100),
            },
            'quantity': article.quantite,
        }
        
        print(f"✅ [DEBUG] Line_item ajouté: {line_item}")
        line_items.append(line_item)

    # ========== FRAIS DE LIVRAISON ==========
    print(f"🛒 [DEBUG] Vérification frais de livraison...")
    
    # Vérifier si c'est une commande à emporter
    is_emporter = False
    if commande:
        is_emporter = commande.is_commande_a_emporter
        print(f"🛒 [DEBUG] Commande à emporter: {is_emporter}")
    else:
        print(f"🛒 [DEBUG] Aucune commande fournie, vérification alternative...")
    
    print(f"🛒 [DEBUG] Frais de livraison disponibles: {panier.frais_livraison}")
    
    # Ajouter les frais de livraison UNIQUEMENT si ce n'est pas à emporter ET si frais > 0
    if panier.frais_livraison and panier.frais_livraison > 0 and not is_emporter:
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {'name': 'Frais de livraison'},
                'unit_amount': int(panier.frais_livraison * 100),
            },
            'quantity': 1,
        })
        print(f"✅ [DEBUG] Frais de livraison ajoutés (livraison)")
    elif is_emporter:
        print(f"ℹ️ [DEBUG] Frais de livraison NON ajoutés (commande à emporter)")
    else:
        print(f"ℹ️ [DEBUG] Pas de frais de livraison à ajouter")

    print(f"✅ [DEBUG] === FIN PREPARER_ITEMS_STRIPE ===")
    print(f"✅ [DEBUG] Total line_items créés: {len(line_items)}")
    
    if len(line_items) == 0:
        print("❌ [DEBUG] ATTENTION: Aucun line_item valide créé!")
    
    return line_items




def creer_coupon_stripe(code_promo):
    """Crée un coupon Stripe selon le code promo s'il est valide."""
    if not code_promo or not code_promo.est_valide():
        return None
    try:
        if code_promo.reduction_type == 'P':
            coupon = stripe.Coupon.create(
                percent_off=code_promo.reduction_amount,
                duration="once"
            )
        else:
            coupon = stripe.Coupon.create(
                amount_off=int(code_promo.reduction_amount * 100),
                currency="eur",
                duration="once"
            )
        return coupon.id
    except stripe.error.StripeError as e:
        logger.error(f"Erreur création coupon Stripe: {e}")
        raise


def creer_session_stripe(line_items, session_key, commande_id, coupon_id=None):
    """
    Crée une session Stripe Checkout et retourne son identifiant.
    `commande_id` est requis pour rediriger vers la page de succès.
    """
    print(f"🎯 [DEBUG] FONCTION creer_session_stripe APPELÉE")
    print(f"🎯 [DEBUG] BASE_URL utilisé: {settings.BASE_URL}")
    print(f"🎯 [DEBUG] commande_id: {commande_id}")
    print(f"🎯 [DEBUG] session_key: {session_key}")
    print(f"🎯 [DEBUG] coupon_id: {coupon_id}")
    print(f"🎯 [DEBUG] line_items reçus: {line_items}")
    
    # VÉRIFICATION CRITIQUE : la clé Stripe
    print(f"🔑 [DEBUG] Clé Stripe configurée: {stripe.api_key[:20]}..." if stripe.api_key else "❌ CLÉ STRIPE NON CONFIGURÉE")
    
    try:
        # Configuration de base
        session_config = {
            'payment_method_types': ['card'],
            'line_items': line_items,
            'mode': 'payment',
            'success_url': f'{settings.BASE_URL}/success?commande_id={commande_id}',
            'cancel_url': f'{settings.BASE_URL}/cancel',
            'client_reference_id': str(commande_id),
        }
        
        # Ajouter le coupon si disponible
        if coupon_id:
            session_config['discounts'] = [{'coupon': coupon_id}]
            print(f"🎫 [DEBUG] Coupon appliqué: {coupon_id}")
        
        print(f"⚙️ [DEBUG] Configuration session Stripe: {session_config}")
        
        # Création de la session
        session_stripe = stripe.checkout.Session.create(**session_config)
        
        print(f"✅ [DEBUG] Session Stripe créée avec succès!")
        print(f"✅ [DEBUG] Session ID: {session_stripe.id}")
        print(f"✅ [DEBUG] URL publique: {session_stripe.url}")
        print(f"✅ [DEBUG] URL de succès: {session_stripe.success_url}")
        
        logger.info(f"Session Stripe créée avec ID: {session_stripe.id}")
        return session_stripe.id
        
    except stripe.error.StripeError as e:
        print(f"❌ [DEBUG] Erreur Stripe spécifique: {e}")
        print(f"❌ [DEBUG] Type d'erreur: {type(e).__name__}")
        if hasattr(e, 'user_message'):
            print(f"❌ [DEBUG] Message utilisateur: {e.user_message}")
        if hasattr(e, 'code'):
            print(f"❌ [DEBUG] Code erreur: {e.code}")
        logger.error(f"Erreur lors de la création de la session Stripe : {e}")
        raise
        
    except Exception as e:
        print(f"❌ [DEBUG] Erreur générale: {e}")
        import traceback
        print(f"❌ [DEBUG] Stack trace: {traceback.format_exc()}")
        logger.error(f"Erreur générale lors de la création de la session Stripe : {e}")
        raise



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

from django.utils.timezone import localtime, make_aware, is_naive

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import localtime, make_aware, is_naive
from datetime import datetime, timedelta
import json
import logging
from .models import Commande, HoraireDisponible
from .utils import (
    creneau_est_disponible,
    obtenir_paiements_possibles,
    chercher_prochain_creneau_disponible,
    verifier_ou_corriger_creneau_livraison
)

logger = logging.getLogger(__name__)

@csrf_exempt
@csrf_exempt
def confirmer_commande(request):
    if request.method != 'POST':
        logger.warning("❌ Mauvaise méthode HTTP : %s", request.method)
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        print("[📥] JSON reçu :", data)
    except json.JSONDecodeError:
        logger.error("❌ Erreur de décodage JSON")
        return JsonResponse({'error': 'Format JSON invalide'}, status=400)

    # Récupérer toutes les données nécessaires
    moyen_paiement = data.get('moyen_paiement')
    nom = data.get('nom', '').strip()
    prenom = data.get('prenom', '').strip()
    email = data.get('email', '').strip().lower()
    numero_telephone = data.get('numero_telephone', '').strip()
    societe = data.get('societe', '').strip()
    adresse_facturation = data.get('adresse_facturation', '').strip()
    facture_sans_detail = data.get('factureSansDetail', False)
    
    print(f"[💳] Moyen de paiement : {moyen_paiement}")
    print(f"[👤] Client : {prenom} {nom} - {email}")

    if not moyen_paiement:
        logger.warning("❌ Moyen de paiement manquant")
        return JsonResponse({'error': 'Moyen de paiement manquant'}, status=400)

    # Récupérer la commande depuis les données, pas la session
    commande_id = data.get('commande_id')
    if not commande_id:
        # Essayer depuis la session comme fallback
        commande_id = request.session.get('commande_id')
    
    print(f"[🛒] Commande ID : {commande_id}")

    if not commande_id:
        return JsonResponse({'error': 'Commande non trouvée'}, status=400)

    try:
        commande = Commande.objects.get(id=commande_id)
        print(f"[✅] Commande récupérée : {commande.id}")
    except Commande.DoesNotExist:
        logger.error(f"❌ Commande {commande_id} introuvable")
        return JsonResponse({'error': 'Commande introuvable'}, status=400)

    # Mettre à jour les informations client
    try:
        client = commande.client
        if client:
            # Mettre à jour le client existant
            client.nom = nom or client.nom
            client.prenom = prenom or client.prenom
            client.email = email or client.email
            client.numero_telephone = numero_telephone or client.numero_telephone
            client.save()
            print(f"[👤] Client existant mis à jour : {client.id}")
    except Exception as e:
        print(f"[⚠️] Erreur mise à jour client : {e}")

    # Mettre à jour les informations de facturation
    commande.societe = societe
    commande.adresse_facturation_saisie = adresse_facturation
    commande.facture_sans_detail = facture_sans_detail
    commande.nom_saisi = nom
    commande.prenom_saisi = prenom
    commande.email_saisi = email
    commande.telephone_saisi = numero_telephone

    # Vérification/créneau
    print("[🔎] Vérification/créneau personnalisé")
    nouvelle_heure = verifier_ou_corriger_creneau_livraison(commande)

    # Verrouiller le panier
    if commande.panier:
        try:
            print(f"[🧮] Recalcul total pour panier {commande.panier.id}")
            commande.panier.calculate_total_price()
            commande.panier.is_locked = True
            commande.panier.save()
            print(f"[💰] Nouveau total : {commande.panier.prix_total}")
        except ValueError as e:
            logger.warning(f"[⚠️] Erreur panier : {e}")

    # Vérifier les paiements possibles
    paiements_possibles = obtenir_paiements_possibles(commande)
    print(f"[💳] Paiements possibles : {[p['id'] for p in paiements_possibles]}")
    
    if not any(p['id'] == moyen_paiement for p in paiements_possibles):
        logger.warning(f"❌ Moyen de paiement invalide : {moyen_paiement}")
        return JsonResponse({'error': 'Moyen de paiement invalide'}, status=400)

    # Gérer le moyen de paiement
    commande.moyen_paiement = moyen_paiement

    if moyen_paiement == "stripe":
        # Pour Stripe, le paiement est déjà géré dans valider_commande
        # On marque juste comme payé si ce n'est pas déjà fait
        if not commande.is_paid:
            commande.is_paid = True
            commande.commande_is_valid = True
            commande.heure_paiement = timezone.now()
            print(f"[💳] Commande marquée comme payée (Stripe)")
    else:
        # Pour les autres moyens de paiement (espèces, tickets)
        commande.commande_is_valid = True
        commande.is_paid = False  # Sera marqué comme payé à la livraison
        print(f"[💳] Commande validée (paiement à la livraison)")

    commande.save()
    print(f"[✅] Commande sauvegardée : ID {commande.id}, paiement = {moyen_paiement}, is_paid = {commande.is_paid}")

    # Préparer la réponse
    livraison_dt = None
    if commande.date_livraison_specifiee and commande.heure_livraison_specifiee:
        livraison_dt = datetime.combine(commande.date_livraison_specifiee, commande.heure_livraison_specifiee)
        if is_naive(livraison_dt):
            livraison_dt = make_aware(livraison_dt)
        livraison_dt_local = localtime(livraison_dt)
        date_str = livraison_dt_local.strftime('%Y-%m-%d')
        heure_str = livraison_dt_local.strftime('%H:%M')
    else:
        date_str = "ASAP"
        heure_str = "ASAP"

    return JsonResponse({
        'success': True,
        'commande_id': commande.id,
        'message': 'Commande confirmée',
        'nouvelle_date': date_str,
        'nouvelle_heure': heure_str,
        'total': str(commande.panier.prix_total) if commande.panier else None,
        'is_paid': commande.is_paid,
        'commande_is_valid': commande.commande_is_valid
    })





def chercher_prochain_creneau_disponible(horaires, date, service, heure_minimale, mode):
    from datetime import datetime

    mapping_jour = {
        'MON': 'LUN', 'TUE': 'MAR', 'WED': 'MER', 'THU': 'JEU',
        'FRI': 'VEN', 'SAT': 'SAM', 'SUN': 'DIM'
    }

    jour_fr = mapping_jour[date.strftime('%a').upper()]
    horaires_service = [h for h in horaires if h.jour == jour_fr and h.service == service]
    if not horaires_service:
        return None

    for horaire in horaires_service:
        heures = horaire.get_horaires()
        for heure_str in heures:
            h = datetime.strptime(heure_str, '%H:%M').time()
            if h >= heure_minimale.time():
                if creneau_est_disponible(date, h, mode=mode):
                    return (date, h)
    return None




from django.http import JsonResponse
from .models import VilleDesservie, Commande



def get_panier_minimum(request):
    commande_id = request.session.get('commande_id')
    if not commande_id:
        return JsonResponse({'error': 'Commande non trouvée'}, status=404)

    try:
        commande = Commande.objects.select_related('adresse_livraison', 'panier').get(id=commande_id)
        ville = commande.adresse_livraison.ville.strip()
        ville_info = VilleDesservie.objects.get(ville__iexact=ville)
        montant = commande.panier.calculate_total_price() if commande.panier else 0
        return JsonResponse({
            'ville': ville,
            'panier_minimum': float(ville_info.panier_minimal),
            'montant_panier': float(montant)
        })
    except VilleDesservie.DoesNotExist:
        return JsonResponse({'error': 'Ville non desservie.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from datetime import timedelta
from django.utils.timezone import now

def mise_a_jour_creneau_si_necessaire(commande):
    now_dt = now()
    ancien_creneau = commande.heure_livraison_asap
    if not ancien_creneau:
        return  # Pas de créneau → rien à faire

    temps_ecoule = now_dt - commande.heure_creation
    print(f"[⏱️] Temps écoulé depuis création commande : {temps_ecoule}")

    from swigo.utils import estimer_heure_livraison, creneau_est_disponible

    if temps_ecoule < timedelta(minutes=5):
        print("[🟢] Moins de 5 min : pas de recalcul nécessaire")
        return

    elif temps_ecoule < timedelta(minutes=10):
        # Vérifie si le créneau est encore disponible
        dispo = creneau_est_disponible(ancien_creneau.date(), ancien_creneau.time(), mode='LIVRAISON')
        print(f"[🟡] Entre 5-10 min : créneau encore disponible ? {dispo}")
        if not dispo:
            nouveau_creneau = estimer_heure_livraison(commande.adresse_livraison)
            commande.heure_livraison_asap = nouveau_creneau
            commande.save()
            print(f"[🔁] Créneau mis à jour : {nouveau_creneau}")
    else:
        # Trop tard → on recalcule obligatoirement
        nouveau_creneau = estimer_heure_livraison(commande.adresse_livraison)
        commande.heure_livraison_asap = nouveau_creneau
        commande.save()
        print(f"[🔴] Plus de 10 min : créneau forcé à {nouveau_creneau}")



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
import stripe
from django.conf import settings
from .models import Commande

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging

@csrf_exempt
def valider_commande(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    if not request.session.session_key:
        request.session.create()

    if 'commande_id' not in request.session:
        from .models import Panier
        panier = Panier.objects.create()
        commande = Commande.objects.create(panier=panier, session_key=request.session.session_key)
        request.session['commande_id'] = commande.id
    else:
        commande_id = request.session.get('commande_id')
        try:
            commande = Commande.objects.get(id=commande_id)
            panier = commande.panier
        except Commande.DoesNotExist:
            return JsonResponse({'error': 'Commande introuvable'}, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format JSON invalide'}, status=400)

    # Extraction données client
    try:
        nom, prenom, numero_telephone, adresse_facturation, email = extraire_donnees_client(data)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Consentements
    consent_sms = data.get('consent_sms', False)
    consent_email = data.get('consent_email', False)
    consent_cookies = data.get('consent_cookies', False)

    # Création ou mise à jour client
    try:
        client = creer_ou_mettre_a_jour_client(
            nom=nom,
            prenom=prenom,
            numero_telephone=numero_telephone,
            adresse_facturation=adresse_facturation,
            email=email,
            consent_sms=consent_sms,
            consent_email=consent_email,
            consent_cookies=consent_cookies
        )
    except Exception:
        return JsonResponse({'error': 'Erreur serveur client'}, status=500)

    # Vérification minimum livraison
    if not commande.is_commande_a_emporter and commande.adresse_livraison:
        ville_nom = commande.adresse_livraison.ville.strip()
        try:
            ville_info = VilleDesservie.objects.get(ville__iexact=ville_nom)
            panier.calculate_total_price()
            if panier.prix_total < ville_info.panier_minimal:
                return JsonResponse({
                    'error': f"Le minimum de commande pour {ville_nom} est de {ville_info.panier_minimal:.2f} €. Votre panier est de {panier.prix_total:.2f} €."
                }, status=400)
        except VilleDesservie.DoesNotExist:
            return JsonResponse({'error': f"La ville {ville_nom} n'est pas desservie."}, status=400)

    # Paiement
    moyen_paiement = data.get('moyen_paiement')
    is_nouveau = not Commande.objects.filter(client=client, is_paid=True).exclude(id=commande.id).exists()
    if is_nouveau and moyen_paiement in ['especes_livraison', 'ticket_livraison', 'especes_retrait', 'ticket_retrait']:
        return JsonResponse({
            'error': "Le paiement à la livraison est disponible uniquement à partir de votre deuxième commande."
        }, status=400)

    # Mise à jour commande
    commande.client = client
    commande.nom_saisi = nom
    commande.prenom_saisi = prenom
    commande.telephone_saisi = numero_telephone
    commande.email_saisi = email
    commande.societe = data.get('societe', '')
    commande.adresse_facturation_saisie = data.get('adresse_facturation', '')
    commande.message_pour_chef = data.get('message_chef', '')
    commande.message_pour_livreur = data.get('message_livreur', '')
    commande.facture_sans_detail = data.get('factureSansDetail', False)
    if moyen_paiement:
        commande.moyen_paiement = moyen_paiement
    commande.save()

    # Stripe session (si applicable)
    # Stripe session (si applicable)
    stripe_session_id = None
    paiements_possibles = obtenir_paiements_possibles(commande)
    print(f"🔍 [DEBUG] Paiements possibles: {paiements_possibles}")

    if any(p['id'] == 'stripe' for p in paiements_possibles):
        try:
            print("🔄 [DEBUG] Début création session Stripe...")
            
            line_items = preparer_items_stripe(panier, commande)

            print(f"📦 [DEBUG] Line_items retournés: {len(line_items)} items")
            
            # VÉRIFICATION CRITIQUE : y a-t-il des items ?
            if len(line_items) == 0:
                print("❌ [DEBUG] ERREUR: Aucun line_item valide - impossible de créer session Stripe")
                stripe_session_id = None
            else:
                coupon_id = None
                if hasattr(panier, 'code_promo') and panier.code_promo:
                    print(f"🎫 [DEBUG] Code promo détecté: {panier.code_promo}")
                    coupon_id = creer_coupon_stripe(panier.code_promo)
                    print(f"🎫 [DEBUG] Coupon Stripe créé: {coupon_id}")
                
                print(f"🔄 [DEBUG] Appel de creer_session_stripe...")
                stripe_session_id = creer_session_stripe(
                    line_items,
                    request.session.session_key,
                    commande.id,
                    coupon_id
                )
                print(f"✅ [DEBUG] Session Stripe créée: {stripe_session_id}")
                
        except Exception as e:
            print(f"❌ [DEBUG] ERREUR dans création session Stripe: {str(e)}")
            import traceback
            print(f"❌ [DEBUG] Stack trace: {traceback.format_exc()}")
            stripe_session_id = None
    else:
        print("ℹ️ [DEBUG] Stripe non disponible dans les paiements possibles")

    # Heure livraison ASAP : première estimation
    if not commande.is_commande_a_emporter and not commande.heure_livraison_specifiee and not commande.heure_livraison_asap:
        try:
            from swigo.utils import estimer_heure_livraison
            commande.heure_livraison_asap = estimer_heure_livraison(commande.adresse_livraison)
            commande.save()
        except Exception:
            pass

    # 🔁 Mise à jour du créneau uniquement si en mode ASAP ou si créneau planifié est saturé
    if not commande.is_commande_a_emporter:
        try:
            from swigo.utils import estimer_heure_livraison, creneau_est_disponible
            now_dt = now()
            temps_ecoule = now_dt - commande.heure_creation

            if commande.heure_livraison_asap and not commande.heure_livraison_specifiee:
                # Mode ASAP → recalcul si trop ancien ou créneau saturé
                ancien_creneau = commande.heure_livraison_asap

                if temps_ecoule >= timedelta(minutes=10):
                    commande.heure_livraison_asap = estimer_heure_livraison(commande.adresse_livraison)
                    commande.save()
                elif temps_ecoule >= timedelta(minutes=5):
                    if not creneau_est_disponible(ancien_creneau.date(), ancien_creneau.time(), mode='LIVRAISON'):
                        commande.heure_livraison_asap = estimer_heure_livraison(commande.adresse_livraison)
                        commande.save()

            elif commande.heure_livraison_specifiee:
                # Mode planifié → vérifier que le créneau est toujours dispo
                date_liv = commande.date_livraison_specifiee or now_dt.date()
                heure_liv = commande.heure_livraison_specifiee
                dispo = creneau_est_disponible(date_liv, heure_liv, mode='LIVRAISON')
                print(f"[🔍] Vérif du créneau spécifié {heure_liv} le {date_liv} → dispo={dispo}")

                if not dispo:
                    print("[⚠️] Créneau choisi saturé → fallback ASAP")
                    commande.heure_livraison_asap = estimer_heure_livraison(commande.adresse_livraison)
                    commande.heure_livraison_specifiee = None
                    commande.date_livraison_specifiee = None
                    commande.save()

        except Exception as e:
            print(f"[⚠️] Erreur recalcul créneau : {e}")

    return JsonResponse({
        'success': True,
        'paiements_possibles': paiements_possibles,
        'commande_id': commande.id,
        'stripe_session_id': stripe_session_id,
        'premiere_commande': is_nouveau
    })





from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, localtime, make_aware, is_naive
from datetime import datetime, timedelta
from swigo.models import Commande
from swigo.utils import (
    estimer_heure_livraison,
    creneau_est_disponible,
    get_temps_livraison_minutes,
    TEMPS_PREPARATION_MINUTES
)
from swigo.utils import verifier_ou_corriger_creneau_retrait, verifier_ou_corriger_creneau_livraison


def confirmation_commande(request, commande_id):
    from django.utils.timezone import now, is_naive, make_aware, localtime, get_current_timezone
    from swigo.models import Commande
    from swigo.utils import estimer_heure_livraison, estimer_heure_retrait, get_temps_livraison_minutes
    from datetime import timedelta, datetime
    from django.shortcuts import get_object_or_404, render

    print(f"[DEBUG] ➤ Entrée dans confirmation_commande (ID: {commande_id})")

    commande = get_object_or_404(Commande, id=commande_id)
    commande.refresh_from_db()

    print(f"[DEBUG] 🔄 Commande rechargée : ASAP = {commande.heure_livraison_asap}, "
          f"Spécifiée = {commande.heure_livraison_specifiee}, Verrou = {commande.horaire_verrouille}")

    now_dt = now()
    montant_total = commande.panier.prix_total if commande.panier else 0

    # 🏷️ Affichage du moyen de paiement
    MOYENS_PAIEMENT_LABELS = {
        'especes_livraison': 'Espèces (à la livraison)',
        'especes_retrait': 'Espèces (au retrait)',
        'ticket_restaurant_livraison': 'Ticket restaurant (à la livraison)',
        'ticket_restaurant_retrait': 'Ticket restaurant (au retrait)',
        'stripe': 'Carte bancaire (en ligne)',
    }
    moyen_affiche = MOYENS_PAIEMENT_LABELS.get(commande.moyen_paiement, commande.moyen_paiement)

    def formater_creneau(dt):
        print(f"[DEBUG] ➤ formater_creneau() appelée avec : {dt} ({type(dt)})")
        if is_naive(dt):
            print("[⚠️] DATETIME NAÏF détecté → conversion en aware")
            dt = make_aware(dt, get_current_timezone())
        dt = localtime(dt)
        debut = (dt - timedelta(minutes=15)).strftime('%H:%M')
        fin = (dt + timedelta(minutes=15)).strftime('%H:%M')
        print(f"[DEBUG] 🕓 Créneau formaté : {debut} – {fin}")
        return f"{debut} – {fin}"

    creneau_livraison = None
    creneau_retrait = None

    # 🎒 Commande à emporter
    if commande.is_commande_a_emporter:
        print("[DEBUG] 🎒 Commande à emporter")
        if commande.heure_pick_up_specifie:
            creneau_retrait = formater_creneau(commande.heure_pick_up_specifie)
        elif not commande.horaire_verrouille:
            estimation = estimer_heure_retrait()
            commande.heure_pick_up_specifie = estimation
            commande.horaire_verrouille = True
            commande.save(update_fields=['heure_pick_up_specifie', 'horaire_verrouille'])
            creneau_retrait = formater_creneau(estimation)
        else:
            print("[🔒] Horaire verrouillé mais aucun retrait défini")

    # 🚚 Commande en livraison
    else:
        print("[DEBUG] 🚚 Commande en livraison")
        if commande.horaire_verrouille:
            print("[🔒] Horaire verrouillé → aucune modification")
            if commande.heure_livraison_specifiee:
                dt_livraison = make_aware(datetime.combine(
                    commande.date_livraison_specifiee or now_dt.date(),
                    commande.heure_livraison_specifiee
                ))
            else:
                dt_livraison = commande.heure_livraison_asap

            if dt_livraison:
                creneau_livraison = formater_creneau(dt_livraison)
            else:
                print("[⚠️] Horaire verrouillé mais aucune heure définie")

        else:
            if commande.heure_livraison_specifiee:
                dt = make_aware(datetime.combine(
                    commande.date_livraison_specifiee or now_dt.date(),
                    commande.heure_livraison_specifiee
                ))
                marge = timedelta(minutes=TEMPS_PREPARATION_MINUTES + get_temps_livraison_minutes(commande.adresse_livraison))
                if dt >= now_dt + marge:
                    commande.horaire_verrouille = True
                    commande.save(update_fields=['horaire_verrouille'])
                    creneau_livraison = formater_creneau(dt)
                else:
                    print("[⛔] Trop tard pour créneau demandé → fallback ASAP")
                    estimation = estimer_heure_livraison(commande.adresse_livraison)
                    commande.heure_livraison_asap = estimation
                    commande.horaire_verrouille = True
                    commande.save(update_fields=['heure_livraison_asap', 'horaire_verrouille'])
                    creneau_livraison = formater_creneau(estimation)
            else:
                print("[ℹ️] Pas de créneau demandé → estimation directe")
                estimation = estimer_heure_livraison(commande.adresse_livraison)
                commande.heure_livraison_asap = estimation
                commande.horaire_verrouille = True
                commande.save(update_fields=['heure_livraison_asap', 'horaire_verrouille'])
                creneau_livraison = formater_creneau(estimation)

    return render(request, 'swigo/confirmation_commande.html', {
        'commande': commande,
        'message': "Commande confirmée !",
        'montant_total': montant_total,
        'moyen_affiche': moyen_affiche,
        'creneau_livraison': creneau_livraison,
        'creneau_retrait': creneau_retrait,
    })









def appliquer_frais_gestion(self):
    if self.commande and self.commande.moyen_paiement and 'ticket' in self.commande.moyen_paiement:
        self.frais_gestion = Decimal('1.00')
    else:
        self.frais_gestion = Decimal('0.00')
    self.save()


import stripe
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Commande
from django.contrib.sessions.models import Session
from django.utils import timezone


stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    logger.info("🎯 Webhook Stripe appelé!")
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = "whsec_38cdd1b4bfef99b43cd11859a11deb415b2e1d6c2a31fb91a2c350c13de5488a"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        logger.error(f"❌ Erreur vérification signature: {e}")
        return JsonResponse({'error': str(e)}, status=400)

    logger.info(f"✅ Événement reçu: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        logger.info(f"🔍 client_reference_id: {session.get('client_reference_id')}")
        logger.info(f"💰 Montant total: {session.get('amount_total')}")
        logger.info(f"📧 Email client: {session.get('customer_details', {}).get('email')}")
        logger.info(f"🔍 success_url: {session.get('success_url')}")
        
        # ✅ CORRECTION : GÉRER LES ÉVÉNEMENTS DE TEST
        commande_id = session.get('client_reference_id')
        
        # Si c'est un événement de test Stripe (client_reference_id manquant)
        if not commande_id:
            logger.warning("⚠️ Événement de test Stripe détecté - client_reference_id manquant")
            
            # Vérifier si c'est un vrai événement de test Stripe
            customer_email = session.get('customer_details', {}).get('email')
            if customer_email == 'stripe@example.com' or 'httpbin.org' in session.get('success_url', ''):
                logger.info("🎯 Événement de test Stripe confirmé - Ignorer silencieusement")
                return JsonResponse({'status': 'test_event_ignored'}, status=200)
            else:
                logger.error("❌ Événement réel sans commande_id - Création d'urgence")
                # Pour les événements réels sans commande_id, créer une commande d'urgence
                try:
                    from swigo.models import Commande
                    from django.utils import timezone
                    
                    commande_urgence = Commande.objects.create(
                        session_key=f"urgence_webhook_{session.get('id')}",
                        nom_saisi=session.get('customer_details', {}).get('name', 'Client Webhook'),
                        prenom_saisi="",
                        email_saisi=session.get('customer_details', {}).get('email', ''),
                        is_commande_a_emporter=False,
                        commande_is_valid=True,
                        is_paid=True,
                        moyen_paiement='stripe',
                        montant_stripe=session.get('amount_total', 0) / 100,
                        heure_paiement=timezone.now(),
                        statut='payee'
                    )
                    commande_id = str(commande_urgence.id)
                    logger.info(f"📝 Commande d'urgence créée: {commande_urgence.id}")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur création commande urgence: {e}")
                    return JsonResponse({'status': 'emergency_failed'}, status=200)
        
        # ✅ TRAITEMENT NORMAL DE LA COMMANDE
        try:
            commande = Commande.objects.get(id=commande_id)
            logger.info(f"📦 Commande trouvée: {commande.id}, is_paid avant: {commande.is_paid}")
            
            payment_status = session.get('payment_status')
            if payment_status == 'paid':
                commande.is_paid = True
                commande.commande_is_valid = True
                commande.heure_paiement = timezone.now()
                commande.moyen_paiement = 'stripe'
                commande.montant_stripe = session.get('amount_total', 0) / 100
                
                if hasattr(commande, 'stripe_session_id'):
                    commande.stripe_session_id = session.get('id')
                
                commande.save()
                
                # Déduire les ingrédients
                try:
                    commande.deduire_ingredients()
                    logger.info(f"📦 Ingrédients déduits pour la commande {commande.id}")
                except Exception as e:
                    logger.error(f"⚠️ Erreur déduction ingrédients: {e}")
                
                commande.refresh_from_db()
                logger.info(f"🎉 SUCCÈS - Commande {commande.id} marquée comme payée")
                logger.info(f"📊 Statuts: is_paid={commande.is_paid}, commande_is_valid={commande.commande_is_valid}")
                
            else:
                logger.warning(f"⚠️ Statut de paiement non 'paid': {payment_status}")
            
        except Commande.DoesNotExist:
            logger.error(f"❌ Commande {commande_id} non trouvée")
            return JsonResponse({'status': 'commande_not_found'}, status=200)
        except Exception as e:
            logger.error(f"❌ Erreur traitement commande: {e}")
            import traceback
            logger.error(f"❌ Stack trace: {traceback.format_exc()}")
            return JsonResponse({'status': 'processing_error'}, status=200)
        
        return JsonResponse({'status': 'success'}, status=200)

    logger.info(f"ℹ️ Événement ignoré: {event['type']}")
    return JsonResponse({'status': 'ignored'}, status=200)










from django.http import JsonResponse
from .models import Commande

def get_adresse_livraison(request):
    # Récupérer la commande en cours à partir de la session
    commande_id = request.session.get('commande_id')
    
    if not commande_id:
        return JsonResponse({'success': False, 'message': 'Aucune commande trouvée'}, status=400)

    try:
        # Récupérer la commande et l'adresse de livraison
        commande = Commande.objects.get(id=commande_id)
        adresse_livraison = commande.adresse_livraison

        # Formatage de l'adresse de livraison
        adresse_complete = f"{adresse_livraison.adresse}, {adresse_livraison.code_postal} {adresse_livraison.ville}"

        return JsonResponse({'success': True, 'adresse_livraison': adresse_complete})

    except Commande.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Commande non trouvée'}, status=404)



from datetime import datetime, timedelta
from django.utils.timezone import now
from django.shortcuts import render
from .models import Commande, Panier
from swigo.utils import (
    verifier_ou_corriger_creneau_livraison,
    verifier_ou_corriger_creneau_retrait
)


def paiement_succes(request):
    commande_id = request.GET.get('commande_id')
    print(f"🎯 [PAIEMENT_SUCCES] Début - commande_id: {commande_id}")
    
    if not commande_id or not commande_id.isdigit():
        return render(request, 'swigo/error.html', {'message': 'Aucune commande valide trouvée.'})

    try:
        commande = Commande.objects.get(id=int(commande_id))
        print(f"📦 [PAIEMENT_SUCCES] Commande trouvée: #{commande.id}")
        print(f"🔍 [PAIEMENT_SUCCES] Statut ACTUEL - is_paid: {commande.is_paid}")
        
        # ⭐ NE PAS METTRE À JOUR LE STATUT - JUSTE AFFICHER
        if commande.is_paid:
            print(f"✅ [PAIEMENT_SUCCES] Commande déjà payée (par webhook)")
        else:
            print(f"⏳ [PAIEMENT_SUCCES] Commande pas encore marquée payée (webhook en cours)")
            # Optionnel: attendre un peu que le webhook fasse son travail
            import time
            for i in range(5):  # Attendre max 5 secondes
                time.sleep(1)
                commande.refresh_from_db()
                if commande.is_paid:
                    print(f"✅ [PAIEMENT_SUCCES] Commande maintenant payée après {i+1}s")
                    break
            else:
                print(f"⚠️ [PAIEMENT_SUCCES] Commande toujours pas payée après attente")
            
    except Commande.DoesNotExist:
        return render(request, 'swigo/error.html', {'message': 'Commande introuvable.'})
    
    # ... le reste de votre code d'affichage inchangé ...
    
    # 5. RÉCUPÉRATION DU PANIER (existant)
    try:
        panier = Panier.objects.get(commande=commande)
        print(f"[DEBUG] ➤ Panier associé : ID {panier.id} - total = {panier.prix_total}")
    except Panier.DoesNotExist:
        return render(request, 'swigo/error.html', {'message': 'Aucun panier associé à cette commande.'})

    montant_total = panier.prix_total
    moyen_affiche = "Carte bancaire (en ligne)"

    # 6. LOGIQUE DE LIVRAISON (votre code existant)
    def formater_creneau(dt_or_date, heure=None):
        if isinstance(dt_or_date, datetime):
            dt = localtime(dt_or_date)
            print(f"[DEBUG] 🕒 formater_creneau -> datetime reçu, localisé: {dt}")
        else:
            dt_naive = datetime.combine(dt_or_date, heure)
            dt = make_aware(dt_naive) if is_naive(dt_naive) else localtime(dt_naive)
            print(f"[DEBUG] 🕒 formater_creneau -> combiné: {dt}")
        debut = (dt - timedelta(minutes=15)).strftime('%H:%M')
        fin = (dt + timedelta(minutes=15)).strftime('%H:%M')
        return f"{debut} et {fin}"

    livraison_message = ""
    details_livraison = ""
    creneau_livraison = None
    creneau_retrait = None

    if commande.is_commande_a_emporter:
        print(f"[DEBUG] 🎒 Commande à emporter détectée")
        heure_corrigee = verifier_ou_corriger_creneau_retrait(commande)
        if heure_corrigee:
            creneau_retrait = formater_creneau(heure_corrigee)
            livraison_message = f"Votre commande sera prête à être retirée entre {creneau_retrait}."
        else:
            livraison_message = "Votre commande sera prête à emporter dans environ 30 minutes."
        details_livraison = "Veuillez venir la récupérer directement au comptoir à l'heure prévue."
    else:
        print(f"[DEBUG] 🚚 Commande en livraison détectée")
        heure_confirmee = verifier_ou_corriger_creneau_livraison(commande)
        if heure_confirmee:
            creneau_livraison = formater_creneau(heure_confirmee)
            livraison_message = f"Votre livraison est prévue entre {creneau_livraison}."
        else:
            estimation = now() + timedelta(minutes=commande.adresse_livraison.delai_livraison_estime)
            creneau_livraison = formater_creneau(estimation)
            livraison_message = f"Votre livraison est estimée entre {creneau_livraison}."
        details_livraison = "Vous recevrez un SMS quelques minutes avant l'arrivée du livreur."

    return render(request, 'swigo/success.html', {
        'commande': commande,
        'message': "Félicitations ! Votre commande a bien été prise en compte.",
        'livraison_message': livraison_message,
        'details_livraison': details_livraison,
        'montant_total': montant_total,
        'moyen_affiche': moyen_affiche,
        'creneau_livraison': creneau_livraison,
        'creneau_retrait': creneau_retrait,
    })






def paiement_annule(request):
    commande_id = request.GET.get('commande_id')
    context = {'commande_id': commande_id}
    return render(request, 'swigo/cancel.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Commande

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Commande

from django.utils import timezone
from datetime import datetime

def accepter_livraison_asap(request):
    if request.method == 'POST':
        print("[DEBUG] POST reçu")
        print(f"[DEBUG] POST data: {request.POST}")

        commande_id = request.session.get('commande_id')
        print(f"[SESSION] commande_id = {commande_id}")

        if not commande_id:
            print("[ERREUR] commande_id absent de la session")
            return JsonResponse({'error': 'Commande introuvable dans la session'}, status=400)

        
        commande = get_object_or_404(Commande, id=commande_id)

        # Lorsqu'on choisit livraison, on s'assure que is_commande_a_emporter est False
        commande.is_commande_a_emporter = False

        premiere_date = request.POST.get('premiere_date')
        premiere_heure = request.POST.get('premiere_heure')

        if premiere_date and premiere_heure:
            naive_datetime = datetime.strptime(f"{premiere_date} {premiere_heure}", "%Y-%m-%d %H:%M")
            timezone_aware_datetime = timezone.make_aware(naive_datetime, timezone.get_current_timezone())

            commande.heure_livraison_asap = timezone_aware_datetime
            commande.save()

            return JsonResponse({'message': 'Heure de livraison enregistrée avec succès'})
        else:
            return JsonResponse({'error': 'Aucune heure de livraison trouvée'}, status=400)
    
    return JsonResponse({'error': 'Requête non valide'}, status=400)


from django.shortcuts import render

def assets_index(request):
    # Cette vue sert le template index.html du répertoire assets
    return render(request, 'assets/index.html')

from django.shortcuts import render
from django.conf import settings  # Pour accéder à la clé API Google Maps

def map_commandes_payees(request):
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY  # Clé Google Maps depuis les settings
    return render(request, 'assets/logistique.html', {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,  # Passer la clé au template
    })



from django.http import JsonResponse
from .models import Commande


def api_commandes_a_livrer(request):
    commandes = Commande.objects.filter(
        commande_is_valid=True,
        is_in_the_kitchen=False
    ).select_related('adresse_livraison').prefetch_related('tourneecommande_set__tournee')

    results = []
    for c in commandes:
        tournees = [tc.tournee for tc in c.tourneecommande_set.all() if tc.tournee]
        tournee_nom = tournees[0].nom if tournees else None
        livreur = tournees[0].livreur.nom if tournees and tournees[0].livreur else ""
        adresse = c.adresse_livraison
        results.append({
            "id": c.id,
            "adresse_livraison__adresse": adresse.adresse if adresse else "",
            "adresse_livraison__ville": adresse.ville if adresse else "",
            "adresse_livraison__latitude": adresse.latitude if adresse and adresse.latitude else None,
            "adresse_livraison__longitude": adresse.longitude if adresse and adresse.longitude else None,
            "heure_livraison_specifiee": str(c.heure_livraison_specifiee) if c.heure_livraison_specifiee else None,
            "heure_livraison_asap": localtime(c.heure_livraison_asap).strftime('%H:%M') if c.heure_livraison_asap else None,
            "tournee_nom": tournee_nom,
            "moyen_paiement": c.moyen_paiement,
            "livreur": livreur,
            "is_in_the_kitchen": c.is_in_the_kitchen,
        })

    return JsonResponse(results, safe=False)





from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import models  # Assurez-vous d'importer models
from django.db.models import Subquery, OuterRef  # Importez Subquery ici
from .models import Commande, Tournee, TourneeCommande, MouvementStock 
from string import ascii_uppercase
from django.utils import timezone
from django.db.models import Q



from django.http import JsonResponse
from django.db.models import Q
from .models import Commande
from django.urls import reverse


from django.http import JsonResponse

def api_commandes_payees(request):
    from .models import Commande  # ou adapte selon ton organisation

    commandes = Commande.objects.filter(is_paid=True)
    # Filtres GET
    date = request.GET.get('date')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')
    id_commande = request.GET.get('id')
    nom = request.GET.get('nom')
    tel = request.GET.get('tel')
    email = request.GET.get('email')

    if date:
        commandes = commandes.filter(heure_paiement__date=date)
    if date_min:
        commandes = commandes.filter(heure_paiement__date__gte=date_min)
    if date_max:
        commandes = commandes.filter(heure_paiement__date__lte=date_max)
    if id_commande:
        commandes = commandes.filter(id=id_commande)
    if nom:
        commandes = commandes.filter(
            Q(client__nom__icontains=nom) |
            Q(client__prenom__icontains=nom) |
            Q(nom_saisi__icontains=nom) |
            Q(prenom_saisi__icontains=nom)
        )
    if tel:
        commandes = commandes.filter(
            Q(client__numero_telephone__icontains=tel) |
            Q(telephone_saisi__icontains=tel)
        )
    if email:
        commandes = commandes.filter(
            Q(email_saisi__icontains=email) |
            Q(client__email__icontains=email)
        )

    commandes = commandes.select_related('client', 'adresse_livraison', 'panier').prefetch_related('panier__articlepanier_set', 'panier__articlepanier_set__plat')

    results = []
    for c in commandes:
        montant_total = float(c.panier.prix_total) if c.panier and c.panier.prix_total else 0
        details = []
        if c.panier:
            for article in c.panier.articlepanier_set.all():
                plat_nom = article.plat.nom if article.plat else "Salade personnalisée"
                details.append({
                    "plat_nom": plat_nom,
                    "quantite": article.quantite,
                    "prix_total": float(article.prix_total or 0),
                })
        facture_id = c.facture.id if hasattr(c, 'facture') else None
        facture_url = reverse('swigo:facture_detail', args=[facture_id]) if facture_id else ""
        generer_facture_url = reverse('swigo:generer_facture', args=[c.id]) if not facture_id else ""

        results.append({
            "id": c.id,
            "client__nom": c.client.nom if c.client else "",
            "client__prenom": c.client.prenom if c.client else "",
            "client__numero_telephone": c.client.numero_telephone if c.client else "",
            "adresse_livraison__adresse": c.adresse_livraison.adresse if c.adresse_livraison else "",
            "adresse_livraison__ville": c.adresse_livraison.ville if c.adresse_livraison else "",
            "montant_total": montant_total,
            "date_paiement": c.heure_paiement.strftime('%d/%m/%Y %H:%M') if c.heure_paiement else "",
            "moyen_paiement": c.get_moyen_paiement_display() if hasattr(c, "get_moyen_paiement_display") else c.moyen_paiement,
            "details": details,
            "facture_id": facture_id,
            "facture_url": facture_url,
            "generer_facture_url": generer_facture_url,
        })

    return JsonResponse(results, safe=False)




from django.http import JsonResponse

@csrf_exempt
def api_commandes_a_emporter(request):
    commandes_qs = Commande.objects.filter(
        is_commande_a_emporter=True,
        commande_is_valid=True,
        is_picked=False
    ).select_related('client', 'panier').order_by('heure_pick_up_specifie')

    commandes_list = []

    for commande in commandes_qs:
        articles = []
        if commande.panier:
            for article in commande.panier.articlepanier_set.all():
                # Nom du plat (robuste)
                plat_nom = (
                    article.plat.nom if article.plat else
                    "Salade personnalisée" if article.salade_personnalisee else
                    "Couscous personnalisé" if article.couscous_personnalise else
                    article.nom_personnalise or "Article inconnu"
                )

                articles.append({
                    'plat_nom': plat_nom,
                    'quantite': article.quantite,
                })

        try:
            montant = float(commande.calculate_prix_total())
        except Exception:
            montant = 0.0

        commandes_list.append({
            'id': commande.id,
            'client__nom': commande.client.nom if commande.client else '',
            'client__prenom': commande.client.prenom if commande.client else '',
            'client__numero_telephone': commande.client.numero_telephone if commande.client else '',
            'statut': commande.get_statut(),
            'details': articles,
            'montant_total': montant,
            'moyen_paiement': commande.get_moyen_paiement_display() or 'Non spécifié',
            'heure_pick_up_specifie': localtime(commande.heure_pick_up_specifie).strftime("%H:%M") if commande.heure_pick_up_specifie else '',
            'is_picked': commande.is_picked,
            'heure_picked': localtime(commande.heure_picked).strftime("%H:%M") if commande.is_picked and commande.heure_picked else ''
        })

    return JsonResponse(commandes_list, safe=False)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Commande, ArticlePanier
from decimal import Decimal

@csrf_exempt
def api_commandes_a_payer(request):
    commandes_qs = Commande.objects.filter(
        is_paid=False,
        commande_is_valid=True
    ).select_related('client', 'panier')

    commandes_list = []
    print("=== Chargement des commandes à payer ===")

    for commande in commandes_qs:
        print(f"\nCommande ID {commande.id} - Client : {commande.client}")
        articles = []

        if commande.panier:
            print(f"  Panier ID : {commande.panier.id}")
            article_qs = (
                commande.panier.articlepanier_set
                .select_related(
                    'plat__categorie',
                    'salade_personnalisee__base',
                    'salade_personnalisee__sauce',
                    'couscous_personnalise__formule'
                )
                .prefetch_related(
                    'options',
                    'salade_personnalisee__proteines',
                    'salade_personnalisee__garnitures',
                    'salade_personnalisee__toppings',
                    'salade_personnalisee__supplement',
                    'couscous_personnalise__viandes_choisies',
                    'couscous_personnalise__choixviandecouscous_set__viande'
                )
            )

            print(f"  Nombre d'articles : {article_qs.count()}")

            for article in article_qs:
                nom_article = "Article inconnu"
                details = []

                # 🍔 Plat classique
                if article.plat:
                    plat = article.plat
                    cat = getattr(plat.categorie, 'nom', '').lower()
                    nom_article = f"{plat.nom} (bar)" if cat in ['boisson', 'dessert'] else plat.nom
                    print(f"    → Plat classique : {nom_article}")

                # 🥗 Salade personnalisée
                elif article.salade_personnalisee:
                    print("    → Salade personnalisée")
                    salade = article.salade_personnalisee
                    nom_article = "Salade personnalisée"

                    if salade.base:
                        details.append(f"Base : {salade.base.nom}")
                    if salade.sauce:
                        details.append(f"Sauce : {salade.sauce.nom}")

                    # Protéines
                    proteines = salade.proteines.all()
                    if proteines:
                        items = []
                        for p in proteines:
                            label = p.nom
                            if p.prix_unitaire_vente and p.prix_unitaire_vente > 0:
                                label += f" (+{p.prix_unitaire_vente} €)"
                            items.append(label)
                        details.append("Protéines : " + ", ".join(items))

                    # Garnitures
                    garnitures = list(salade.garnitures.all())
                    garniture_items = []
                    for i, g in enumerate(garnitures):
                        label = g.nom
                        if i >= salade.MAX_GARNITURES and g.prix_unitaire_vente > 0:
                            label += f" (+{g.prix_unitaire_vente} €)"
                        garniture_items.append(label)
                    if garniture_items:
                        details.append("Garnitures : " + ", ".join(garniture_items))

                    # Toppings
                    toppings = list(salade.toppings.all())
                    topping_items = []
                    for i, t in enumerate(toppings):
                        label = t.nom
                        if i >= salade.MAX_TOPPINGS and t.prix_unitaire_vente > 0:
                            label += f" (+{t.prix_unitaire_vente} €)"
                        topping_items.append(label)
                    if topping_items:
                        details.append("Toppings : " + ", ".join(topping_items))

                    # Suppléments
                    supplements = salade.supplement.all()
                    if supplements:
                        supplement_list = [
                            f"{s.nom} (+{s.prix_unitaire_vente} €)" if s.prix_unitaire_vente else s.nom
                            for s in supplements
                        ]
                        details.append("Suppléments : " + ", ".join(supplement_list))

                # 🥘 Couscous personnalisé
                elif article.couscous_personnalise:
                    couscous = article.couscous_personnalise
                    print("    → Couscous personnalisé")

                    try:
                        formule = couscous.formule.nom
                    except:
                        formule = "Formule inconnue"

                    nom_article = f"Couscous {formule}"
                    choix_qs = couscous.choixviandecouscous_set.select_related('viande')
                    viandes_suppl = [
                        f"{c.viande.nom} (+{c.viande.supplement_extra}€)"
                        for c in choix_qs if not c.est_incluse
                    ]
                    if viandes_suppl:
                        nom_article += " + " + ", ".join(viandes_suppl)

                else:
                    print("    → Aucun plat, salade ni couscous trouvé")

                articles.append({
                    'plat_nom': nom_article,
                    'quantite': article.quantite,
                    'details': details
                })

        else:
            print("  Aucun panier associé à cette commande.")

        try:
            montant = commande.calculate_prix_total()
        except Exception as e:
            print(f"  ⚠️ Erreur lors du calcul du prix : {e}")
            montant = 0

        print(f"  Total : {montant} €")
        print(f"  Articles extraits : {articles}")

        commandes_list.append({
            'id': commande.id,
            'client__nom': commande.client.nom if commande.client else '',
            'client__prenom': commande.client.prenom if commande.client else '',
            'client__numero_telephone': commande.client.numero_telephone if commande.client else '',
            'statut': commande.get_statut(),
            'montant_total': montant,
            'moyen_paiement': commande.get_moyen_paiement_display() or 'Non renseigné',
            'details': articles
        })

    print("=== Fin ===\n")
    return JsonResponse(commandes_list, safe=False)





from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def commandes_a_payer_view(request):
    return render(request, 'assets/commandes_a_payer.html')

@login_required
def commandes_payees_view(request):
    return render(request, 'assets/commandes_payees.html')


from django.utils.timezone import now
from django.shortcuts import render
from decimal import Decimal
from .models import Commande

def commandes_du_jour(request):
    today = now().date()
    commandes = (
        Commande.objects
        .filter(heure_creation__date=today)
        .filter(heure_creation__date=today, commande_is_valid=True)  # ✅ Ajout du filtre

        .select_related('client', 'adresse_livraison')
    )

    commandes_data = []
    total_journalier = Decimal(0)

    for commande in commandes:
        try:
            panier = commande.panier

        except Commande.panier_associe.RelatedObjectDoesNotExist:
            panier = None

        if panier:
            total_commande = panier.prix_total or panier.calculate_total_price()
        else:
            total_commande = Decimal(0)

        commandes_data.append({
            'commande': commande,
            'total': total_commande
        })

        total_journalier += total_commande

    context = {
        'commandes_data': commandes_data,
        'total_journalier': total_journalier,
        'now': now()
    }

    return render(request, 'assets/commandes_du_jour.html', context)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from .models import Commande, MoyenPaiement



@csrf_exempt
def enregistrer_paiement(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    commande_id = request.POST.get('commande_id')
    mixte = request.POST.get('mixte') == 'true'

    try:
        commande = Commande.objects.get(pk=commande_id)
    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)

    if commande.is_paid:
        return JsonResponse({'error': 'Commande déjà payée'}, status=400)

    if mixte:
        try:
            montant_especes = Decimal(request.POST.get('montant_especes') or 0)
            montant_ticket = Decimal(request.POST.get('montant_ticket') or 0)
            montant_stripe = Decimal(request.POST.get('montant_stripe') or 0)
        except InvalidOperation:
            return JsonResponse({'error': 'Montants invalides'}, status=400)

        total_mixte = montant_especes + montant_ticket + montant_stripe
        total_commande = commande.calculate_prix_total()

        if total_mixte < total_commande:
            return JsonResponse({'error': 'Le montant total est insuffisant.'}, status=400)
        if total_mixte > total_commande:
            return JsonResponse({'error': 'Le montant total dépasse le prix de la commande.'}, status=400)

        commande.set_paiement_mixte(montant_especes, montant_ticket, montant_stripe)

    else:
        moyen = request.POST.get('moyen_paiement')
        if moyen not in dict(MoyenPaiement.choices):
            return JsonResponse({'error': 'Moyen de paiement invalide'}, status=400)

        commande.set_paiement(moyen)

    return JsonResponse({'success': True})



@csrf_exempt
def marquer_emportee(request):
    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        try:
            commande = Commande.objects.get(id=commande_id)
            commande.is_picked = True
            commande.heure_picked = timezone.now()
            commande.save()
            return JsonResponse({'success': True})
        except Commande.DoesNotExist:
            return JsonResponse({'error': 'Commande introuvable'}, status=404)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from swigo.models import Commande, Client
import logging



logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from swigo.models import Commande, Client, ClientBlacklist
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def api_commandes_a_valider(request):
    commandes_qs = Commande.objects.filter(
        moyen_paiement__in=[
            'especes_livraison',
            'ticket_livraison', 
            'especes_retrait',
            'ticket_retrait'
        ],
        is_paid=False,
        commande_is_valid=False
    ).select_related('client', 'panier', 'adresse_livraison')

    commandes_list = []

    for commande in commandes_qs:
        montant = commande.panier.prix_total if commande.panier else 0

        # Détails COMPLETS des articles avec get_cart_items
        details = []
        if commande.panier:
            cart_items = get_cart_items(commande.panier)
            for item in cart_items:
                # Construire le texte détaillé avec accompagnement
                plat_text = f"{item['quantite']} x {item['plat_nom']}"
                
                # Ajouter les options
                if item['options']:
                    plat_text += f" - {', '.join(item['options'])}"
                
                # AJOUTER L'ACCOMPAGNEMENT
                if item['accompagnement']:
                    plat_text += f" | Accompagnement: {item['accompagnement']['nom']}"
                    if item['accompagnement']['prix'] != '0.00':
                        plat_text += f" (+{item['accompagnement']['prix']}€)"
                
                details.append({
                    'plat_nom': item['plat_nom'],
                    'quantite': item['quantite'],
                    'options': item['options'],
                    'accompagnement': item['accompagnement'],
                    'texte_complet': plat_text
                })

        # Adresse livraison
        adresse_livraison = ''
        if commande.adresse_livraison:
            adresse_livraison = f"{commande.adresse_livraison.adresse}, {commande.adresse_livraison.ville}"

        # Retrait ou Livraison
        is_retrait = 'retrait' in commande.moyen_paiement
        heure_retrait = commande.heure_pick_up_specifie or commande.heure_pick_up_specifie
        heure_retrait_str = heure_retrait.strftime("%H:%M") if is_retrait and heure_retrait else None

        livraison_asap = bool(commande.heure_livraison_asap) if not is_retrait else None
        heure_livraison_str = commande.heure_livraison_specifiee.strftime("%H:%M") if commande.heure_livraison_specifiee else None
        date_livraison_str = commande.date_livraison_specifiee.strftime("%d/%m/%Y") if commande.date_livraison_specifiee else None

        # Ordre chrono
        if is_retrait:
            ordre_chronologique = heure_retrait
        else:
            if commande.heure_livraison_asap:
                ordre_chronologique = commande.heure_livraison_asap
            elif commande.date_livraison_specifiee and commande.heure_livraison_specifiee:
                ordre_chronologique = datetime.combine(
                    commande.date_livraison_specifiee,
                    commande.heure_livraison_specifiee
                )
            else:
                ordre_chronologique = None

        # Détection client déjà connu
        match_count = 0
        match_fields = []

        if commande.email_saisi and Client.objects.filter(email__iexact=commande.email_saisi).exists():
            match_count += 1
            match_fields.append("email")

        if commande.telephone_saisi and Client.objects.filter(numero_telephone=commande.telephone_saisi).exists():
            match_count += 1
            match_fields.append("telephone")

        if commande.nom_saisi and commande.prenom_saisi:
            if Client.objects.filter(nom__iexact=commande.nom_saisi, prenom__iexact=commande.prenom_saisi).exists():
                match_count += 1
                match_fields.append("nom_prenom")

        deja_client = match_count >= 2

        # Vérification blacklist
        is_blacklisted = ClientBlacklist.objects.filter(
            Q(email__iexact=commande.email_saisi) |
            Q(numero_telephone=commande.telephone_saisi)
        ).exists()

        commandes_list.append({
            'id': commande.id,
            'client__id': commande.client.id if commande.client else None,
            'client__nom': commande.client.nom if commande.client else '',
            'client__prenom': commande.client.prenom if commande.client else '',
            'client__numero_telephone': commande.client.numero_telephone if commande.client else '',
            'montant_total': montant,
            'moyen_paiement': commande.get_moyen_paiement_display(),
            'adresse_livraison': adresse_livraison,
            'details': details,  # MAINTENANT AVEC ACCOMPAGNEMENTS
            'is_retrait': is_retrait,
            'heure_retrait': heure_retrait_str,
            'livraison_asap': livraison_asap,
            'heure_livraison': heure_livraison_str,
            'date_livraison': date_livraison_str,
            'ordre_chronologique': ordre_chronologique.isoformat() if ordre_chronologique else None,
            'est_nouveau_client': not deja_client,
            'match_par': match_fields,
            'is_blacklisted': is_blacklisted
        })

    return JsonResponse(commandes_list, safe=False)












import json

@csrf_exempt
def api_valider_commande(request, commande_id):
    if request.method == "POST":
        try:
            commande = Commande.objects.get(id=commande_id)
            data = json.loads(request.body)
            force_validation = data.get("force_validation", False)

            if commande.is_paid or force_validation:
                commande.commande_is_valid = True
                commande.save(update_fields=['commande_is_valid'])
                return JsonResponse({'message': '✅ Commande validée'})

            return JsonResponse({'error': '❌ Paiement différé – validation manuelle requise'}, status=403)

        except Commande.DoesNotExist:
            return JsonResponse({'error': 'Commande introuvable'}, status=404)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)






def map_commandes_en_attente_paiement(request):
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY  # Clé Google Maps depuis les settings
    return render(request, 'assets/logistique_en_attente.html', {
        'GOOGLE_MAPS_API_KEY': google_maps_api_key,  # Passer la clé API Google au template
    })

def api_commandes_en_attente_paiement(request):
    maintenant = timezone.now()
    delai = timedelta(minutes=10)

    # Filtrer les commandes en attente de paiement créées il y a moins de 10 minutes
    commandes = Commande.objects.filter(
        is_paid=False,  # Commandes en attente de paiement
        is_delivered=False,  # Non livrées
        commande_is_valid=False,  # ✅ Ajouter ce filtre

        heure_creation__gte=maintenant - delai  # Créées dans les 10 dernières minutes
    ).values('id', 'adresse_livraison__latitude', 'adresse_livraison__longitude')

    return JsonResponse(list(commandes), safe=False)  # Retourner les commandes en JSON

from .models import Livreur


@csrf_exempt
def attribuer_livreur_a_tournee(request, nom_tournee, nom_livreur):
    if request.method == "POST":
        # Vérifiez si request.body contient des données
        if request.body:
            try:
                # Charger et afficher les données JSON reçues
                data = json.loads(request.body)
                print("Données de la requête:", data)  # Affichez les données dans la console

                livreur_nom = data.get("livreur")

                # Récupérer et mettre à jour la tournée et le livreur
                try:
                    tournee = Tournee.objects.get(nom=nom_tournee)
                    livreur = Livreur.objects.get(nom=nom_livreur)
                    tournee.livreur = livreur

                    # Enregistrer des détails supplémentaires si nécessaire
                    tournee.save()

                    return JsonResponse({"message": "Livreur attribué avec succès."})
                except Tournee.DoesNotExist:
                    return JsonResponse({"error": "Tournée non trouvée."}, status=404)
                except Livreur.DoesNotExist:
                    return JsonResponse({"error": "Livreur non trouvé."}, status=404)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Données JSON invalides"}, status=400)
        else:
            return JsonResponse({"error": "Aucune donnée reçue"}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def api_livreurs_positions(request):
    # Filtrer les livreurs qui sont "au travail"
    livreurs = Livreur.objects.filter(au_travaille=True).values('id', 'nom', 'latitude', 'longitude', 'is_booked')

    # Renvoyer les données JSON des livreurs
    return JsonResponse(list(livreurs), safe=False)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Tournee, TourneeCommande, Commande, Livreur

@csrf_exempt  # Désactive la vérification CSRF pour cette API (attention en production, il faudra utiliser des tokens d'authentification)
def update_livreur_position(request):
    if request.method == 'POST':
        # Récupérer les données envoyées par le livreur
        livreur_id = request.POST.get('livreur_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Vérifier que les données sont valides
        if livreur_id and latitude and longitude:
            try:
                livreur = Livreur.objects.get(id=livreur_id)
                livreur.latitude = float(latitude)
                livreur.longitude = float(longitude)
                livreur.save()  # Mettre à jour la position du livreur

                return JsonResponse({'status': 'success', 'message': 'Position mise à jour.'})
            except Livreur.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Livreur non trouvé.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Données invalides.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'})

from .models import Tournee, TourneeCommande, Commande

def api_tournees_existantes(request):
    tournées = Tournee.objects.filter(is_closed=False).values('id', 'nom', 'date_tournee')
    return JsonResponse(list(tournées), safe=False)

def generer_nom_tournee():
    # Récupérer la date d'aujourd'hui et la formater en YYMMDD
    aujourd_hui = date.today().strftime('%y%m%d')

from django.http import JsonResponse

def attribuer_commande_a_tournee(request):
    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        tournee_existante_id = request.POST.get('tournee_existante')
        nouvelle_tournee = request.POST.get('nouvelle_tournee')

        # Récupérer la commande
        commande = get_object_or_404(Commande, id=commande_id)

        # Vérifier les anciennes associations
        anciennes_tournees = TourneeCommande.objects.filter(commande=commande)

        # Supprimer les anciennes associations si elles existent
        if anciennes_tournees.exists():
            anciennes_tournees.delete()  # Supprime toutes les anciennes associations
            messages.info(request, f"La commande {commande.id} a été retirée de sa tournée précédente.")

        # Attribuer à une tournée existante
        if tournee_existante_id:
            tournee = get_object_or_404(Tournee, id=tournee_existante_id)

            # Vérifier si la commande est déjà associée à la tournée choisie
            if not TourneeCommande.objects.filter(commande=commande, tournee=tournee).exists():
                TourneeCommande.objects.create(tournee=tournee, commande=commande, ordre=0)
                commande.is_on_tour = True
                commande.save()
                return JsonResponse({'status': 'success', 'message': f'La commande {commande.id} a été attribuée à la tournée {tournee.nom}.'})
            else:
                return JsonResponse({'status': 'warning', 'message': f'La commande {commande.id} est déjà attribuée à la tournée {tournee.nom}.'})

        # Créer une nouvelle tournée si demandé
        if nouvelle_tournee:
            nom_tournee = generer_nom_tournee()

            nouvelle_tournee = Tournee.objects.create(
                nom=nom_tournee,
                date_tournee=timezone.now().date(),
            )
            
            # Vérifier si la commande est déjà associée à une autre tournée
            if not TourneeCommande.objects.filter(commande=commande).exists():
                TourneeCommande.objects.create(tournee=nouvelle_tournee, commande=commande, ordre=0)
                commande.is_on_tour = True
                commande.save()
                return JsonResponse({'status': 'success', 'message': f'La commande {commande.id} a été attribuée à la nouvelle tournée {nouvelle_tournee.nom}.'})
            else:
                return JsonResponse({'status': 'warning', 'message': 'La commande est déjà associée à une tournée.'})

    return JsonResponse({'status': 'error', 'message': 'Une erreur est survenue lors de l\'attribution de la commande.'})



from datetime import date


def generer_numero_tournee():
    # Récupérer la date d'aujourd'hui
    aujourd_hui = date.today()

    # Compter combien de tournées ont déjà été créées aujourd'hui
    nombre_de_tournees = Tournee.objects.filter(date_tournee=aujourd_hui).count()

    # Le numéro de la nouvelle tournée sera le nombre de tournées existantes + 1
    return nombre_de_tournees + 1

def generer_id_tournee(numero_tournee):
    # Récupérer la date d'aujourd'hui au format YYMMDD
    aujourd_hui = date.today().strftime('%y%m%d')

    # Combiner la date avec le numéro de la tournée
    return f"{aujourd_hui}{numero_tournee}"


import logging
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages

logger = logging.getLogger(__name__)  # Configurer un logger pour cette vue

def creer_nouvelle_tournee(request): 
    logger.info("Vue 'creer_nouvelle_tournee' appelée.")
    
    if request.method == 'POST':
        logger.info("Requête POST reçue.")
        csrf_token = request.POST.get('csrfmiddlewaretoken')
        logger.info(f"Token CSRF reçu : {csrf_token}")

        commande_id = request.POST.get('commande_id')
        logger.info(f"Commande ID reçu : {commande_id}")

        if not commande_id:
            logger.error("Aucun ID de commande reçu dans la requête.")
            return JsonResponse({'status': 'failed', 'error': 'Commande ID manquant.'}, status=400)

        try:
            commande = get_object_or_404(Commande, id=commande_id)
            logger.info(f"Commande trouvée : {commande.id}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la commande : {e}")
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=404)

        anciennes_tournees = TourneeCommande.objects.filter(commande=commande)
        if anciennes_tournees.exists():
            anciennes_tournees.delete()
            logger.info(f"Ancienne association tournée supprimée pour la commande {commande.id}.")

        try:
            numero_tournee = int(Tournee.generer_numero_tournee())
            logger.info(f"Numéro de tournée généré : {numero_tournee}")

            while Tournee.objects.filter(nom=numero_tournee, date_tournee=timezone.now().date()).exists():
                numero_tournee += 1
                logger.info(f"Incrémentation du numéro de tournée : {numero_tournee}")

            id_tournee = generer_id_tournee(str(numero_tournee))
            logger.info(f"ID unique de la tournée généré : {id_tournee}")

            nouvelle_tournee = Tournee.objects.create(
                nom=numero_tournee,
                id_tournee=id_tournee,
                date_tournee=timezone.now().date(),
            )
            logger.info(f"Nouvelle tournée créée : {nouvelle_tournee.nom}")

            TourneeCommande.objects.create(tournee=nouvelle_tournee, commande=commande, ordre=0)
            logger.info(f"Commande {commande.id} ajoutée à la tournée {nouvelle_tournee.nom}.")

            commande.is_on_tour = True
            commande.save()
            logger.info(f"Champ 'is_on_tour' mis à jour pour la commande {commande.id}.")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Erreur lors de la création de la tournée : {e}")
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)

    logger.warning("Requête non-POST reçue.")
    return JsonResponse({'status': 'failed', 'error': 'Requête non autorisée.'}, status=400)







from django.http import JsonResponse
from .models import Tournee
from django.db.models import Count


from django.db.models import Count

from django.http import JsonResponse
from django.db.models import Count

from django.http import JsonResponse
from django.db.models import Count
from .models import Tournee, Livreur

from django.db.models import Count, Q

def api_affichage_tournees(request):
    # Filtrer les tournées non terminées ayant au moins une commande NON à emporter
    tournees = Tournee.objects.filter(
        is_done=False,
        tourneecommande__commande__is_commande_a_emporter=False
    ).annotate(
        num_commandes=Count('tourneecommande')
    ).filter(
        num_commandes__gt=0
    ).distinct().order_by('-heure_cloture')

    livreurs = Livreur.objects.filter(au_travaille=True)

    data = []

    for tournee in tournees:
        tournee_data = {
            'nom': tournee.nom,
            'date_tournee': tournee.date_tournee,
            'livreur': tournee.livreur.nom if tournee.livreur else 'Aucun livreur',
            'is_closed': tournee.is_closed,
            'commandes': []
        }

        for tc in tournee.tourneecommande_set.select_related('commande').all():
            commande = tc.commande
            if commande.is_commande_a_emporter:
                continue  # On saute les commandes à emporter ici aussi si tu veux

            tournee_data['commandes'].append({
                'id': commande.id,
                'client': f"{commande.client.nom} {commande.client.prenom}" if commande.client else "Client non spécifié",
                'adresse_livraison': commande.adresse_livraison.adresse if commande.adresse_livraison else 'Adresse non disponible',
                'ville': commande.adresse_livraison.ville if commande.adresse_livraison else '',
                'latitude': commande.adresse_livraison.latitude if commande.adresse_livraison else None,
                'longitude': commande.adresse_livraison.longitude if commande.adresse_livraison else None,
            })

        # On ajoute la tournée seulement si elle a encore des commandes à afficher
        if tournee_data['commandes']:
            data.append(tournee_data)

    livreurs_data = [{'nom': livreur.nom, 'telephone': livreur.telephone} for livreur in livreurs]

    return JsonResponse({'tournees': data, 'livreurs': livreurs_data}, safe=False)






from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction  # Ajout de transaction pour plus de sécurité
import json
from .models import Tournee, TourneeCommande

@require_POST
@transaction.atomic  # Utilisez une transaction pour garantir que toutes les mises à jour sont faites
def sauvegarder_ordre_commandes(request):
    try:
        # Récupérer les données envoyées
        tournee_nom = request.POST.get('tournee_nom')
        commandes = json.loads(request.POST.get('commandes'))

        # Afficher les données pour vérification
        print(f"Tournée : {tournee_nom}")
        print(f"Commandes reçues : {commandes}")

        # Récupérer la tournée
        tournee = Tournee.objects.get(nom=tournee_nom)

        # Si aucune commande n'est fournie ou que la liste est vide, ne mettez pas à jour l'ordre
        if not commandes:
            print("Aucun ordre de commandes n'a été fourni. L'ordre actuel est conservé.")
            return JsonResponse({'status': 'success', 'message': "L'ordre n'a pas été modifié."}, status=200)

        # Mettre à jour l'ordre des commandes si un ordre est spécifié
        for index, commande_id in enumerate(commandes):
            # Mettre à jour l'ordre dans le modèle TourneeCommande
            tournee_commande = TourneeCommande.objects.filter(commande_id=commande_id, tournee=tournee).update(ordre=index)
            if tournee_commande == 0:
                print(f"Erreur : Commande {commande_id} non trouvée dans la tournée {tournee_nom}")
            else:
                print(f"Commande {commande_id} mise à jour avec l'ordre {index}")

        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de l'ordre des commandes : {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)




from django.http import JsonResponse
from .models import Tournee

def api_adresses_tournee(request, nom_tournee):
    # Récupérer la tournée par son nom (la lettre) et vérifier qu'elle n'est pas fermée
    tournee = Tournee.objects.filter(nom=nom_tournee, is_done=False).first()
    
    if not tournee:
        print(f"Tournée {nom_tournee} non trouvée ou fermée")
        return JsonResponse({'error': 'Tournée non trouvée'}, status=404)

    # Récupérer les commandes associées à la tournée
    commandes = tournee.tourneecommande_set.select_related('commande').all()

    if not commandes.exists():
        print(f"Aucune commande pour la tournée {nom_tournee}")
        return JsonResponse([], safe=False)

    # Préparer la liste des adresses
    data = []
    for tournee_commande in commandes:
        adresse_livraison = tournee_commande.commande.adresse_livraison
        if adresse_livraison:
            print(f"Adresse trouvée pour la commande #{tournee_commande.commande.id}: {adresse_livraison.adresse}")
            data.append({
                'id': tournee_commande.commande.id,
                'adresse': adresse_livraison.adresse,
                'ville': adresse_livraison.ville,
                'latitude': adresse_livraison.latitude,
                'longitude': adresse_livraison.longitude
            })
        else:
            print(f"Aucune adresse pour la commande #{tournee_commande.commande.id}")

    return JsonResponse(data, safe=False)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Commande, TourneeCommande

def api_commande_details(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # Récupérer la tournée associée à la commande, s'il y en a une
    tournee_commande = TourneeCommande.objects.filter(commande=commande).first()
    tournee_nom = tournee_commande.tournee.nom if tournee_commande else 'N/A'

    # Préparer les données de date et heure de livraison
    if commande.date_livraison_specifiee and commande.heure_livraison_specifiee:
        date_heure_livraison = {
            'date_livraison_specifiee': commande.date_livraison_specifiee.strftime('%Y-%m-%d'),
            'heure_livraison_specifiee': commande.heure_livraison_specifiee.strftime('%H:%M')
        }
    elif commande.heure_livraison_asap:
        date_heure_livraison = {
            'heure_livraison_asap': commande.heure_livraison_asap.strftime('%Y-%m-%d %H:%M')
        }
    else:
        date_heure_livraison = {}

    # Ajouter l'heure de paiement si la commande est payée
    paiement_info = {
        'is_paid': commande.is_paid,
        'heure_paiement': commande.heure_paiement.strftime('%Y-%m-%d %H:%M') if commande.heure_paiement else 'N/A',
        'moyen_paiement': commande.get_moyen_paiement_display() if commande.moyen_paiement else 'Non spécifié'
    } if commande.is_paid else {
        'is_paid': False,
        'moyen_paiement': commande.get_moyen_paiement_display() if commande.moyen_paiement else 'Non spécifié'
    }

    adresse_livraison = f"{commande.adresse_livraison.adresse}, {commande.adresse_livraison.code_postal} {commande.adresse_livraison.ville}" if commande.adresse_livraison else 'Aucune adresse'

    data = {
        'id': commande.id,
        'client': f'{commande.client.nom} {commande.client.prenom}' if commande.client else 'N/A',
        'numero_telephone': commande.client.numero_telephone if commande.client and commande.client.numero_telephone else 'N/A',
        'adresse_livraison': adresse_livraison,
        'tournee_nom': tournee_nom,
        **date_heure_livraison,
        **paiement_info,
        'panier': commande.panier.id if commande.panier else 'N/A',
    }

    return JsonResponse(data)



from django.http import JsonResponse
from .models import ArticlePanier

def api_detail_panier(request, commande_id):
    try:
        commande = get_object_or_404(Commande, pk=commande_id)
        articles = ArticlePanier.objects.filter(panier=commande.panier)
        panier_data = []

        for article in articles:
            # Utilisation de 'nom_option' au lieu de 'nom'
            options = [option.nom_option for option in article.options.all()]
            panier_data.append({
                'plat': article.plat.nom,
                'quantite': article.quantite,
                'prix_total': article.prix_total,
                'options': options,
            })

        return JsonResponse({'articles': panier_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Tournee, TourneeCommande

@require_POST
def cloturer_tournee(request, tournee_id):
    try:
        # Rechercher la tournée par son identifiant
        tournee = get_object_or_404(Tournee, nom=tournee_id)
        
        # Clôturer la tournée et enregistrer l'heure de clôture
        tournee.is_closed = True
        tournee.heure_cloture = timezone.now()  # Enregistrer l'heure de clôture

        # Démarrer le chronomètre si ce n'est pas déjà fait
        if not tournee.start_time:
            tournee.start_time = timezone.now()  # Enregistrer le démarrage du chronomètre

        tournee.save(update_fields=['is_closed', 'heure_cloture', 'start_time'])

        # Récupérer toutes les commandes associées à cette tournée via TourneeCommande
        tournee_commandes = TourneeCommande.objects.filter(tournee=tournee).order_by('ordre')

        # Vérifier et mettre à jour l'ordre des commandes si nécessaire
        for index, tournee_commande in enumerate(tournee_commandes):
            if tournee_commande.ordre is None or tournee_commandes[index].ordre != index:
                # Mettre à jour l'ordre s'il est incorrect ou non défini
                tournee_commande.ordre = index
                tournee_commande.save(update_fields=['ordre'])

        # Mettre à jour chaque commande en utilisant la méthode `set_in_the_kitchen`
        for tournee_commande in tournee_commandes:
            commande = tournee_commande.commande
            if not commande.is_in_the_kitchen:  # Si la commande n'est pas déjà en cuisine
                commande.set_in_the_kitchen()  # Appeler la méthode pour marquer comme "en cuisine"

        return JsonResponse({'message': 'Tournée clôturée avec succès et chronomètre démarré !'})

    except Tournee.DoesNotExist:
        return JsonResponse({'error': 'Tournée non trouvée.'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.shortcuts import render
from django.db.models import Q
from .models import Commande, Tournee, TourneeCommande

from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Q
from .models import Commande, Tournee, TourneeCommande

from django.shortcuts import render
from django.utils.timezone import now
from datetime import date
from django.db.models import Q
from .models import Commande, Tournee, TourneeCommande

def cuisine_view(request):
    """
    Vue pour afficher les commandes en cuisine :
    - payées OU validées manuellement,
    - en cuisine (is_in_the_kitchen=True),
    - non cuites (is_cooked=False),
    regroupées par tournées fermées.
    """

    # Étape 1 : créer une tournée fermée pour chaque commande à emporter validée sans tournée
    # CORRECTION: Utiliser le même filtre que get_commandes_cuisine
    commandes_sans_tournee = Commande.objects.filter(
        Q(is_paid=True) | Q(commande_is_valid=True),  # ← Uniformisation du filtre
        is_commande_a_emporter=True,
        is_in_the_kitchen=True,
        is_cooked=False
    ).exclude(
        id__in=TourneeCommande.objects.values_list('commande_id', flat=True)
    )

    for commande in commandes_sans_tournee:
        id_tournee = f"A_EMPORTER_{commande.id}"
        aujourd_hui = date.today()
        prochain_numero = Tournee.objects.filter(date_tournee=aujourd_hui).count() + 1

        tournee, created = Tournee.objects.get_or_create(
            id_tournee=id_tournee,
            defaults={
                'nom': prochain_numero,
                'date_tournee': aujourd_hui,
                'is_closed': True,
                'heure_cloture': now()
            }
        )

        # Créer le lien commande <-> tournée
        TourneeCommande.objects.create(
            commande=commande,
            tournee=tournee,
            ordre=1
        )

    # Étape 2 : récupérer toutes les commandes concernées
    # CORRECTION: Utiliser le même filtre que get_commandes_cuisine
    commandes = Commande.objects.filter(
        Q(is_paid=True) | Q(commande_is_valid=True),  # ← Uniformisation du filtre
        is_in_the_kitchen=True,
        is_cooked=False
    )

    # Étape 3 : récupérer les tournées fermées associées
    tournees_fermees = Tournee.objects.filter(
        is_closed=True,
        tourneecommande__commande__in=commandes
    ).distinct().order_by('heure_cloture')

    # Étape 4 : organiser les commandes par tournée
    tournees_commandes = {}

    for tournee in tournees_fermees:
        commandes_tournee = TourneeCommande.objects.filter(
            tournee=tournee,
            commande__in=commandes
        ).order_by('ordre')
        tournees_commandes[tournee] = commandes_tournee

    # Étape 5 : envoyer au template
    return render(request, 'assets/cuisine.html', {
        'tournees_commandes': tournees_commandes
    })



from django.http import JsonResponse
from django.db.models import Q
from django.utils.timezone import now, localtime
from datetime import timedelta
from .models import Commande, Tournee, TourneeCommande


def get_commandes_cuisine(request):
    try:
        commandes = Commande.objects.filter(
            Q(is_paid=True) | Q(commande_is_valid=True),
            is_in_the_kitchen=True,
            is_cooked=False
        ).select_related('client')  # ✅ IMPORTANT : Inclure le client

        tournees_commandes = []
        five_minutes_ago = now() - timedelta(minutes=5)

        tournees_fermees = Tournee.objects.filter(
            is_closed=True,
            tourneecommande__commande__in=commandes
        ).distinct().order_by('heure_cloture')

        for tournee in tournees_fermees:
            commandes_tournee = []
            aggregated_articles = {}

            tournee_commandes = TourneeCommande.objects.filter(
                tournee=tournee,
                commande__in=commandes
            ).select_related('commande').distinct()

            commande = tournee_commandes.first().commande if tournee_commandes.exists() else None
            is_pickup = commande and commande.is_commande_a_emporter
            heure_emport = commande.heure_pick_up_specifie if is_pickup else None

            cuisson_en_cours = False
            cuisson_start_times = []

            for tc in tournee_commandes:
                commande = tc.commande
                articles, aggregated_articles = extraire_articles_et_aggregats(commande, aggregated_articles, filtrer_cuisine=False)
                if commande.cuisson_en_cours and commande.heure_cuisson_en_cours:
                    cuisson_en_cours = True
                    cuisson_start_times.append(commande.heure_cuisson_en_cours)

                commandes_tournee.append({
                    'commande_id': commande.id,
                    'articles': articles,
                    'cuisson_en_cours': commande.cuisson_en_cours,
                    'has_message_for_chef': bool(commande.message_pour_chef),
                    'message_pour_chef': commande.message_pour_chef.strip() if commande.message_pour_chef else ''
                })

            cuisson_start_time = min(cuisson_start_times) if cuisson_start_times else None

            tournees_commandes.append({
                'tournee_id': tournee.id,
                'tournee_nom': tournee.nom,
                'commandes': commandes_tournee,
                'aggregated_articles': aggregated_articles,
                'recently_closed': tournee.heure_cloture >= five_minutes_ago if tournee.heure_cloture else False,
                'start_time': tournee.heure_cloture.isoformat() if tournee.heure_cloture else None,
                'cuisson_en_cours': cuisson_en_cours,
                'cuisson_start_time': cuisson_start_time.isoformat() if cuisson_start_time else None,
                'is_pickup': is_pickup,
                'heure_emport': localtime(heure_emport).strftime('%H:%M') if heure_emport else None,
                'heure_emport_sort': heure_emport.isoformat() if heure_emport else None,
            })

        # Commandes à emporter sans tournée
        commandes_emporter = commandes.filter(
            is_commande_a_emporter=True,
            commande_is_valid=True
        ).exclude(id__in=TourneeCommande.objects.values_list('commande_id', flat=True))

        for commande in commandes_emporter:
            nom_tournee = f"A_EMPORTER_{commande.id}"
            tournee = Tournee.objects.create(
                nom=nom_tournee,
                is_closed=True,
                heure_cloture=now()
            )

            TourneeCommande.objects.create(
                commande=commande,
                tournee=tournee,
                ordre=1
            )

            articles, aggregated_articles = extraire_articles_et_aggregats(commande)
            heure_emport = commande.heure_pick_up_specifie

            tournees_commandes.append({
                'tournee_id': tournee.id,
                'tournee_nom': tournee.nom,
                'commandes': [{
                    'commande_id': commande.id,
                    'articles': articles,
                    'cuisson_en_cours': commande.cuisson_en_cours,
                    'has_message_for_chef': bool(commande.message_pour_chef),
                    'message_pour_chef': commande.message_pour_chef.strip() if commande.message_pour_chef else ''
                }],
                'aggregated_articles': aggregated_articles,
                'recently_closed': True,
                'start_time': tournee.heure_cloture.isoformat(),
                'cuisson_en_cours': commande.cuisson_en_cours,
                'cuisson_start_time': commande.heure_cuisson_en_cours.isoformat() if commande.heure_cuisson_en_cours else None,
                'is_pickup': True,
                'heure_emport': localtime(heure_emport).strftime('%H:%M') if heure_emport else None,
                'heure_emport_sort': heure_emport.isoformat() if heure_emport else None,
            })

        tournees_emport = [t for t in tournees_commandes if t['is_pickup']]
        tournees_livraison = [t for t in tournees_commandes if not t['is_pickup']]
        tournees_emport.sort(key=lambda t: t['heure_emport_sort'] or '9999-12-31T23:59')
        tournees_commandes = tournees_emport + tournees_livraison

        return JsonResponse({'tournees_commandes': tournees_commandes})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



def extraire_articles_et_aggregats(commande, aggregated_articles=None, filtrer_cuisine=True):
    if aggregated_articles is None:
        aggregated_articles = {}

    articles = []

    if not commande.panier:
        return articles, aggregated_articles

    article_qs = (
        commande.panier.articlepanier_set
        .select_related(
            'plat__categorie',
            'salade_personnalisee__base',
            'salade_personnalisee__sauce',
            'couscous_personnalise__formule',
            'menu',
            'accompagnement'
        )
        .prefetch_related(
            'options',
            'options_crousty',
            'options_poulet',
            'salade_personnalisee__proteines',
            'salade_personnalisee__garnitures',
            'salade_personnalisee__toppings',
            'salade_personnalisee__supplement',
            'couscous_personnalise__accompagnements',
            'couscous_personnalise__choixviandecouscous_set__viande',
            'choix_menu__plat_choisi',
            'choix_menu__salade',
            'choix_menu__couscous',
            'choix_menu__couscous__accompagnements',
            'choix_menu__couscous__choixviandecouscous_set__viande'
        )
    )

    for article in article_qs:
        nom_article = "Article inconnu"
        categorie = "Autres"
        details_data = []
        accompagnement_info = None

        # 🆕 GROUPEMENT PAR CATÉGORIES AVEC COULEURS
        options_grouped = {
            'viandes': [],
            'accompagnements': [],
            'fromages': [],
            'sauces': [],
            'supplements': []
        }

        # Récupérer l'accompagnement principal (sans prix)
        if article.accompagnement:
            accompagnement_info = article.accompagnement.nom
            options_grouped['accompagnements'].append(accompagnement_info)

        # ----------- PLAT CLASSIQUE -----------
        if article.plat:
            nom_article = article.plat.nom
            categorie = article.plat.categorie.nom if article.plat.categorie else "Autres"
            
            # Filtrer boissons/desserts
            cat_lower = categorie.lower()
            is_boisson = (cat_lower == "boisson")
            is_dessert = (cat_lower == "dessert")
            if filtrer_cuisine and (is_boisson or is_dessert):
                continue

            # Options classiques (sans prix)
            if article.options.exists():
                for option in article.options.all():
                    option_text = option.nom_option
                    option_text = option_text.split(' (+')[0]
                    
                    # Catégorisation automatique
                    option_lower = option_text.lower()
                    if any(mot in option_lower for mot in ['fromage', 'emmental', 'cheddar', 'mozzarella']):
                        options_grouped['fromages'].append(option_text)
                    elif any(mot in option_lower for mot in ['sauce', 'ketchup', 'mayo', 'moutarde', 'bbq', 'mild', 'hot', 'épicé', 'doux']):
                        options_grouped['sauces'].append(option_text)
                    elif any(mot in option_lower for mot in ['viande', 'bacon', 'poulet', 'agneau', 'merguez', 'boulette']):
                        options_grouped['viandes'].append(option_text)
                    elif any(mot in option_lower for mot in ['accompagnement', 'frites', 'riz', 'salade', 'couscous', 'coleslaw']):
                        options_grouped['accompagnements'].append(option_text)
                    else:
                        options_grouped['supplements'].append(option_text)
            
            # Options Crousty (sans prix)
            if article.plat.type_plat == 'crousty' and article.options_crousty.exists():
                for option in article.options_crousty.all():
                    option_text = option.nom
                    
                    option_lower = option.nom.lower()
                    if any(mot in option_lower for mot in ['fromage', 'emmental', 'cheddar', 'mozzarella']):
                        options_grouped['fromages'].append(option_text)
                    elif any(mot in option_lower for mot in ['sauce', 'ketchup', 'mayo', 'moutarde', 'bbq']):
                        options_grouped['sauces'].append(option_text)
                    elif any(mot in option_lower for mot in ['bacon', 'viande']):
                        options_grouped['viandes'].append(option_text)
                    else:
                        options_grouped['supplements'].append(option_text)
            
            # Options Poulet (sans prix + priorité sauces)
            if (article.plat.type_plat == 'poulet' or article.plat.categorie.nom.lower() == 'poulet') and article.options_poulet.exists():                
                for option in article.options_poulet.all():
                    option_text = option.nom
                    
                    option_lower = option.nom.lower()
                    if any(mot in option_lower for mot in ['mild', 'hot', 'épicé', 'doux']):
                        options_grouped['sauces'].insert(0, option_text)
                    elif any(mot in option_lower for mot in ['sauce', 'ketchup', 'mayo', 'moutarde', 'bbq']):
                        options_grouped['sauces'].append(option_text)
                    elif any(mot in option_lower for mot in ['coleslaw', 'frites', 'riz', 'couscous', 'galette']):
                        options_grouped['accompagnements'].append(option_text)
                    else:
                        options_grouped['supplements'].append(option_text)

        # ----------- AUTRES TYPES D'ARTICLES -----------
        elif article.salade_personnalisee:
            salade = article.salade_personnalisee
            nom_article = "Salade personnalisée"
            categorie = "Salades"
            
            if salade.base:
                options_grouped['accompagnements'].append(f"Base: {salade.base.nom}")
            if salade.sauce:
                options_grouped['sauces'].append(f"Sauce: {salade.sauce.nom}")
            
            for proteine in salade.proteines.all():
                options_grouped['viandes'].append(f"Protéine: {proteine.nom}")
            for garniture in salade.garnitures.all():
                options_grouped['accompagnements'].append(f"Garniture: {garniture.nom}")
            for topping in salade.toppings.all():
                options_grouped['supplements'].append(f"Topping: {topping.nom}")
            for supplement in salade.supplement.all():
                options_grouped['supplements'].append(f"Supplément: {supplement.nom}")

        elif article.couscous_personnalise:
            couscous = article.couscous_personnalise
            nom_article = f"Couscous {couscous.formule.nom}" if couscous.formule else "Couscous"
            categorie = "Couscous"
            
            for choix in couscous.choixviandecouscous_set.select_related('viande'):
                nom = choix.viande.nom
                nom = nom.split(' (+')[0]
                options_grouped['viandes'].append(nom)
            
            if couscous.option_xl:
                options_grouped['supplements'].append("Option XL")
            
            for accompagnement in couscous.accompagnements.all():
                options_grouped['accompagnements'].append(accompagnement.nom)

        elif article.menu:
            nom_article = article.menu.nom
            categorie = "Menus"
            
            # CORRECTION : Utiliser un set pour éviter les doublons
            accompagnements_couscous_deja_vus = set()
            
            for c in article.choix_menu.all():
                role_lower = c.role.lower()
                label = c.get_role_display() if hasattr(c, 'get_role_display') else c.role.capitalize()

                is_boisson = (role_lower == "boisson")
                is_dessert = (role_lower == "dessert")
                if filtrer_cuisine and (is_boisson or is_dessert):
                    continue

                # CORRECTION : Gestion du couscous personnalisé dans les menus
                if c.couscous:
                    # Extraire les viandes du couscous
                    for choix_viande in c.couscous.choixviandecouscous_set.select_related('viande'):
                        nom_viande = choix_viande.viande.nom.split(' (+')[0]
                        options_grouped['viandes'].append(nom_viande)
                    
                    # Extraire les accompagnements du couscous et les mémoriser
                    for accompagnement in c.couscous.accompagnements.all():
                        accompagnements_couscous_deja_vus.add(accompagnement.nom)
                        options_grouped['accompagnements'].append(accompagnement.nom)
                    
                    if c.couscous.option_xl:
                        options_grouped['supplements'].append("Option XL")
                                
                # CORRECTION : Gestion des accompagnements couscous individuels - Éviter les doublons
                elif c.role == "accompagnement_couscous" and getattr(c, "info_text", None):
                    option_text = c.info_text.split(' (+')[0]
                    # Vérifier si cet accompagnement n'a pas déjà été ajouté via le couscous
                    if option_text not in accompagnements_couscous_deja_vus:
                        options_grouped['accompagnements'].append(option_text)
                                
                elif c.role == "viande" and getattr(c, "info_text", None):
                    option_text = c.info_text.split(' (+')[0]
                    options_grouped['viandes'].append(option_text)
                    
                elif c.role == "accompagnement" and getattr(c, "info_text", None):
                    option_text = c.info_text.split(' (+')[0]
                    options_grouped['accompagnements'].append(option_text)
                    
                elif c.role == "boisson" and getattr(c, "info_text", None):
                    if not filtrer_cuisine:
                        option_text = c.info_text.split(' (+')[0]
                        options_grouped['supplements'].append(f"Boisson: {option_text}")
                        
                # CORRECTION : Les plats choisis de type viande vont dans viandes
                elif c.plat_choisi:
                    plat_nom_lower = c.plat_choisi.nom.lower()
                    # Déterminer si c'est un plat principal (viande)
                    is_plat_principal = (
                        c.role == "plat" or 
                        any(mot in plat_nom_lower for mot in ['tenders', 'poulet', 'viande', 'agneau', 'merguez', 'boulette', 'burger', 'steak', 'wing', 'aile', 'frit'])
                    )
                    
                    if is_plat_principal:
                        options_grouped['viandes'].append(f"Plat: {c.plat_choisi.nom}")
                    else:
                        options_grouped['supplements'].append(f"{label}: {c.plat_choisi.nom}")
                        
                elif getattr(c, "info_text", None):
                    options_grouped['supplements'].append(f"{label}: {c.info_text.split(' (+')[0]}")
                    
                elif c.salade:
                    options_grouped['supplements'].append(f"{label}: Salade personnalisée")

        else:
            continue

        # CONSTRUCTION DE L'AFFICHAGE
        details_data = []
        
        categories_config = [
            ('viandes', '🔴 Viandes:', 'text-danger'),
            ('accompagnements', '🟢 Accompagnements:', 'text-success'), 
            ('fromages', '🟡 Fromages:', 'text-warning'),
            ('sauces', '🔵 Sauces:', 'text-primary'),
            ('supplements', '🟣 Suppléments:', 'text-info')
        ]
        
        for cat_key, cat_label, color_class in categories_config:
            if options_grouped[cat_key]:
                details_data.append({
                    'label': cat_label,
                    'items': options_grouped[cat_key],
                    'color': color_class
                })

        # Ajouter l'article avec options groupées
        articles.append({
            'nom': nom_article,
            'categorie': categorie,
            'quantite': article.quantite,
            'options': details_data,
            'accompagnement': accompagnement_info,
            'prix_total': str(article.prix_total) if article.prix_total else '0.00'
        })

        # Agrégation
        if categorie not in aggregated_articles:
            aggregated_articles[categorie] = {}

        article_key = nom_article
        if details_data:
            options_text = []
            for opt_group in details_data:
                options_text.append(f"{opt_group['label']} {opt_group['items']}")
            article_key += f" - {' | '.join(options_text)}"

        if article_key in aggregated_articles[categorie]:
            aggregated_articles[categorie][article_key]['quantite'] += article.quantite
        else:
            aggregated_articles[categorie][article_key] = {
                'nom': nom_article,
                'options': details_data,
                'quantite': article.quantite
            }

    return articles, aggregated_articles




@csrf_exempt
def activer_cuisson(request, commande_id):
    try:
        commande = Commande.objects.get(id=commande_id)
        commande.set_cuisson_en_cours()
        return JsonResponse({'success': True})
    except Commande.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Commande introuvable'})







from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Tournee, TourneeCommande
import traceback



def set_cooked(request, tournee_id):
    if request.method == 'POST':
        try:
            # Récupérer la tournée PAR ID (clé primaire Django)
            tournee = get_object_or_404(Tournee, id=tournee_id)
            tournee_commandes = TourneeCommande.objects.filter(tournee=tournee)

            if not tournee_commandes.exists():
                return JsonResponse({'success': False, 'error': 'Aucune commande associée à cette tournée'}, status=400)

            # Marquer chaque commande comme cuite
            for tc in tournee_commandes:
                commande = tc.commande
                commande.is_cooked = True
                commande.heure_cooked = timezone.now()
                commande.save(update_fields=['is_cooked', 'heure_cooked'])
                commande.check_ready()

            # Vérification si la tournée est prête pour la livraison
            tournee.check_and_mark_ready_for_delivery()

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Erreur lors de la mise à jour des commandes pour la tournée {tournee_id}: {e}")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=400)



from django.db.models import Q

def bar_view(request):
    """
    Vue pour afficher les commandes au bar qui sont payées 
    ou validées manuellement, en cuisine mais pas encore prêtes pour le bar,
    classées par tournées fermées.
    """
    commandes = Commande.objects.filter(
        Q(is_paid=True) | Q(commande_is_valid=True),
        is_in_the_kitchen=True,
        is_cooked=False,
        is_ok_bar=False
    ).exclude(panier__isnull=True)  # ✅ Important : sécurise panier

    tournees_fermees = Tournee.objects.filter(
        is_closed=True,
        tourneecommande__commande__in=commandes
    ).distinct()

    tournees_commandes = {}

    for tournee in tournees_fermees:
        commandes_tournee = TourneeCommande.objects.filter(
            tournee=tournee,
            commande__in=commandes
        ).order_by('ordre')

        commandes_tournee_filtered = []

        for tc in commandes_tournee:
            commande = tc.commande
            panier = commande.panier

            if not panier:
                print(f"⚠️ Commande {commande.id} ignorée : pas de panier.")
                continue

            articles = [
                article for article in panier.articlepanier_set.select_related("plat__categorie").all()
                if article.plat and article.plat.categorie and article.plat.categorie.nom.lower() in ["boisson", "dessert"]
            ]

            if articles:
                commandes_tournee_filtered.append({
                    'commande': commande,
                    'articles': articles
                })

        if commandes_tournee_filtered:
            tournees_commandes[tournee] = commandes_tournee_filtered

    return render(request, 'assets/bar.html', {
        'tournees_commandes': tournees_commandes
    })


def extraire_articles_bar(commande, aggregated_articles=None):
    if aggregated_articles is None:
        aggregated_articles = {}

    articles = []

    article_qs = commande.panier.articlepanier_set.select_related("plat__categorie").prefetch_related("options")

    for article in article_qs:
        # Ne garde que les boisson ou dessert
        if not article.plat or not article.plat.categorie:
            continue

        categorie = article.plat.categorie.nom
        if categorie.lower() not in ["boisson", "dessert"]:
            continue

        options = [opt.nom_option for opt in article.options.all()]
        options_str = ', '.join(options)
        article_key = f"{article.plat.nom} - {options_str}"

        articles.append({
            'nom': article.plat.nom,
            'categorie': categorie,
            'quantite': article.quantite,
            'options': options
        })

        if categorie not in aggregated_articles:
            aggregated_articles[categorie] = {}

        if article_key in aggregated_articles[categorie]:
            aggregated_articles[categorie][article_key]['quantite'] += article.quantite
        else:
            aggregated_articles[categorie][article_key] = {
                'nom': article.plat.nom,
                'options': options_str,
                'quantite': article.quantite
            }

    return articles, aggregated_articles



from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Commande, Tournee, TourneeCommande

def get_commandes_bar(request):
    print(">>> get_commandes_bar appelée")

    try:
        commandes = Commande.objects.filter(
            Q(is_paid=True) | Q(commande_is_valid=True),
            is_in_the_kitchen=True,
            is_ok_bar=False  # Toujours indispensable pour le bar
        ).exclude(panier__isnull=True)

        tournees_commandes = []
        five_minutes_ago = now() - timedelta(minutes=5)

        tournees_fermees = Tournee.objects.filter(
            is_closed=True,
            tourneecommande__commande__in=commandes
        ).distinct().order_by('heure_cloture')

        for tournee in tournees_fermees:
            commandes_tournee = []
            aggregated_articles = {}

            tournee_commandes = TourneeCommande.objects.filter(
                tournee=tournee,
                commande__in=commandes
            ).distinct()

            commande_ref = tournee_commandes.first().commande if tournee_commandes.exists() else None
            is_pickup = commande_ref and commande_ref.is_commande_a_emporter
            heure_emport = commande_ref.heure_pick_up_specifie if is_pickup else None

            for tc in tournee_commandes:
                commande = tc.commande
                if not commande.panier:
                    print(f"⚠️ Commande {commande.id} ignorée (pas de panier)")
                    continue

                articles, aggregated_articles = extraire_articles_et_aggregats(commande, aggregated_articles, filtrer_cuisine=False)
                commandes_tournee.append({
                    'commande_id': commande.id,
                    'articles': articles,
                    'has_message_for_chef': bool(commande.message_pour_chef),
                    'message_pour_chef': commande.message_pour_chef.strip() if commande.message_pour_chef else ''
                })

            tournees_commandes.append({
                'tournee_id': tournee.id,
                'tournee_nom': tournee.nom,
                'commandes': commandes_tournee,
                'aggregated_articles': aggregated_articles,
                'recently_closed': tournee.heure_cloture >= five_minutes_ago if tournee.heure_cloture else False,
                'start_time': tournee.heure_cloture.isoformat() if tournee.heure_cloture else None,
                'is_pickup': is_pickup,
                'heure_emport': localtime(heure_emport).strftime('%H:%M') if heure_emport else None,
                'heure_emport_sort': heure_emport.isoformat() if heure_emport else None,
            })

        return JsonResponse({'tournees_commandes': tournees_commandes})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)









def set_ok_bar(request, tournee_id):
    if request.method == 'POST':
        try:
            tournee = get_object_or_404(Tournee, id=tournee_id)
            tournee_commandes = TourneeCommande.objects.filter(tournee=tournee)

            if not tournee_commandes.exists():
                return JsonResponse({'success': False, 'error': 'Aucune commande associée à cette tournée'}, status=400)

            for tc in tournee_commandes:
                commande = tc.commande
                commande.is_ok_bar = True
                commande.heure_ok_bar = timezone.now()
                commande.save(update_fields=['is_ok_bar', 'heure_ok_bar'])
                commande.check_ready()

            tournee.check_and_mark_ready_for_delivery()
            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Erreur lors de la mise à jour des commandes pour la tournée {tournee_id} : {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=400)



from django.shortcuts import render, get_object_or_404
from swigo.models import Tournee

def vue_livreur(request, tournee_nom):
    # Récupération de la tournée
    tournee = get_object_or_404(Tournee, nom=tournee_nom, is_sent_livreur=True)

    # Préparation des données enrichies par commande
    commandes_data = [
        {
            'id': tc.commande.id,
            'adresse': tc.commande.adresse_livraison.adresse,
            'ville': tc.commande.adresse_livraison.ville,
            'latitude': tc.commande.adresse_livraison.latitude,
            'longitude': tc.commande.adresse_livraison.longitude,
            'telephone': tc.commande.client.numero_telephone if tc.commande.client else None,
            'is_delivered': tc.commande.is_delivered
        }
        for tc in tournee.tourneecommande_set.select_related('commande__client', 'commande__adresse_livraison').all()
    ]

    # Structure unique pour le template
    tournees_data = [
        {
            'tournee': tournee,
            'commandes': commandes_data
        }
    ]

    return render(request, 'assets/tournee_livreur.html', {
        'tournees_data': tournees_data
    })




def valider_livreur(request, tournee_nom):
    if request.method == "POST":
        logger.info(f"Tentative de validation de la tournée : {tournee_nom}")
        
        try:
            # Récupérer la tournée par son nom
            tournee = get_object_or_404(Tournee, nom=tournee_nom)
            logger.info(f"Tournée {tournee_nom} trouvée avec succès.")

            # Récupérer le nom du livreur depuis la requête
            livreur_nom = request.POST.get('livreur_nom')
            if not livreur_nom:
                logger.error("Aucun livreur n'a été sélectionné.")
                return JsonResponse({'error': 'Aucun livreur sélectionné.'}, status=400)
            
            # Récupérer le nouveau livreur
            nouveau_livreur = get_object_or_404(Livreur, nom=livreur_nom)

            # Si un livreur est déjà affecté, le libérer
            if tournee.livreur and tournee.livreur != nouveau_livreur:
                ancien_livreur = tournee.livreur
                ancien_livreur.is_booked = False
                ancien_livreur.save(update_fields=['is_booked'])
                logger.info(f"Ancien livreur {ancien_livreur.nom} libéré.")

            # Attribuer le nouveau livreur et mettre à jour la tournée
            tournee.livreur = nouveau_livreur
            tournee.is_sent_livreur = True
            tournee.save()

            # Marquer le nouveau livreur comme réservé
            nouveau_livreur.is_booked = True
            nouveau_livreur.save(update_fields=['is_booked'])

            logger.info(f"Livreur {livreur_nom} est maintenant réservé pour la tournée {tournee_nom}.")
            return JsonResponse({'message': 'Livreur attribué et tournée envoyée avec succès.'})
        
        except Tournee.DoesNotExist:
            logger.error(f"Tournée avec le nom {tournee_nom} introuvable.")
            return JsonResponse({'error': 'Tournée introuvable.'}, status=404)
        
        except Livreur.DoesNotExist:
            logger.error(f"Livreur avec le nom {livreur_nom} introuvable.")
            return JsonResponse({'error': 'Livreur introuvable.'}, status=404)
        
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la validation de la tournée {tournee_nom}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    logger.warning(f"Méthode non autorisée pour la tournée {tournee_nom}.")
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)




import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_aware
from .models import Tournee, TourneeCommande, Commande

logger = logging.getLogger(__name__)

def envoyer_tournee(request, tournee_nom):
    if request.method != "POST":
        return JsonResponse({"message": "Méthode non autorisée."}, status=405)

    logger.info(f"Requête d'envoi pour la tournée avec nom : {tournee_nom}")
    try:
        tournee = Tournee.objects.get(nom=tournee_nom)
        tournee.is_sent_livreur = True
        tournee.save()

        commandes = tournee.tourneecommande_set.select_related('commande').all()
        commandes_data = [
            {
                'id': tc.commande.id,
                'adresse': tc.commande.adresse_livraison.adresse,
                'ville': tc.commande.adresse_livraison.ville,
                'latitude': tc.commande.adresse_livraison.latitude,
                'longitude': tc.commande.adresse_livraison.longitude,
            }
            for tc in commandes
        ]

        return JsonResponse({
            "message": "Tournée envoyée au livreur avec succès.",
            "commandes": commandes_data
        })

    except Tournee.DoesNotExist:
        logger.error(f"Tournée avec nom {tournee_nom} introuvable.")
        return JsonResponse({"message": "Tournée introuvable."}, status=404)
    except Exception as e:
        logger.error(f"Erreur dans envoyer_tournee : {e}")
        return JsonResponse({"message": f"Erreur: {e}"}, status=500)


@csrf_exempt
def demarrer_tournee(request):
    """Démarre une tournée en fixant l'heure de départ (si pas déjà figée)."""
    if request.method != 'POST':
        logger.warning("[demarrer_tournee] Méthode non autorisée.")
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)

    tournee_nom = request.POST.get('tournee_nom')
    heure_depart_str = request.POST.get('heure_depart')
    logger.info(f"[demarrer_tournee] POST avec tournee_nom={tournee_nom}, heure_depart={heure_depart_str}")

    try:
        tournee = Tournee.objects.get(nom=tournee_nom)
        if getattr(tournee, "is_figee", False):
            logger.warning(f"[demarrer_tournee] Tournée {tournee_nom} déjà figée, démarrage interdit.")
            return JsonResponse({'success': False, 'message': 'Tournée déjà figée, démarrage interdit.'}, status=409)

        heure_depart_dt = parse_datetime(heure_depart_str)
        if heure_depart_dt and not is_aware(heure_depart_dt):
            heure_depart_dt = make_aware(heure_depart_dt)
        tournee.heure_depart = heure_depart_dt
        tournee.is_started = True
        tournee.is_figee = True
        tournee.save()

        commandes = Commande.objects.filter(tourneecommande__tournee=tournee)
        logger.info(f"[demarrer_tournee] {commandes.count()} commandes liées à la tournée {tournee_nom}")

        for commande in commandes:
            commande.set_shipped()
            logger.info(f"[demarrer_tournee] Commande {commande.id} set_shipped à {heure_depart_str}")

        logger.info(f"[demarrer_tournee] La tournée {tournee_nom} a bien démarré à {heure_depart_str}.")
        return JsonResponse({'success': True, 'message': 'La tournée a démarré avec succès.'})

    except Tournee.DoesNotExist:
        logger.error(f"[demarrer_tournee] Tournée {tournee_nom} introuvable.")
        return JsonResponse({'success': False, 'message': 'Tournée introuvable.'}, status=404)
    except Exception as e:
        logger.error(f"[demarrer_tournee] Erreur : {e}")
        return JsonResponse({'success': False, 'message': f'Erreur: {e}'}, status=500)


@csrf_exempt
def update_heures_passage(request):
    """Met à jour les heures de passage (datetime ISO) et la durée de trajet pour chaque commande."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=405)
    try:
        data = json.loads(request.body)
        if not data:
            return JsonResponse({"success": False, "message": "Aucune donnée reçue."}, status=400)

        logger.info(f"[update_heures_passage] Payload reçu: {data}")
        tc_first = TourneeCommande.objects.filter(commande_id=data[0]["commande_id"]).first()
        if not tc_first:
            logger.error("[update_heures_passage] Impossible de trouver la tournée pour la première commande.")
            return JsonResponse({"success": False, "message": "Tournée introuvable."}, status=404)
        tournee = tc_first.tournee

        for item in data:
            commande_id = item.get("commande_id")
            heure_passage_str = item.get("heure_passage")  # ex: '2025-06-05T17:15:35'
            duree_trajet = item.get("duree_trajet")
            heure_passage_dt = parse_datetime(heure_passage_str)
            logger.info(f"[update_heures_passage] commande_id={commande_id}, heure_passage={heure_passage_str}, dt={heure_passage_dt}, duree_trajet={duree_trajet}")
            tc = TourneeCommande.objects.filter(commande_id=commande_id, tournee=tournee).first()
            if tc:
                logger.info(f"[update_heures_passage] tc trouvé pour commande {commande_id}")
                if heure_passage_dt:
                    from django.utils.timezone import make_aware, is_aware
                    if not is_aware(heure_passage_dt):
                        heure_passage_dt = make_aware(heure_passage_dt)
                    tc.heure_passage = heure_passage_dt
                if duree_trajet is not None:
                    tc.duree_trajet = duree_trajet
                tc.save(update_fields=["heure_passage", "duree_trajet"])
                logger.info(f"[update_heures_passage] Après save: {tc.commande.id}, {tc.heure_passage}, {tc.duree_trajet}")
            else:
                logger.warning(f"[update_heures_passage] TourneeCommande NON trouvée pour commande {commande_id} dans tournée {tournee.id}")

        # Figer la tournée si tout est ok
        if all(tc.heure_passage for tc in tournee.tourneecommande_set.all()) and tournee.heure_retour_estime:
            tournee.is_figee = True
            tournee.save(update_fields=["is_figee"])

        return JsonResponse({"success": True, "message": "Heures de passage mises à jour avec succès."})

    except Exception as e:
        logger.error(f"Erreur dans update_heures_passage : {e}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
def update_heure_retour_estime(request, nomTournee):
    """Met à jour l'heure de retour estimée (datetime ISO)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=405)
    try:
        heure_retour_estime_str = request.POST.get("heure_retour_estime")
        heure_retour_estime_dt = parse_datetime(heure_retour_estime_str)
        if heure_retour_estime_dt and not is_aware(heure_retour_estime_dt):
            heure_retour_estime_dt = make_aware(heure_retour_estime_dt)
        if not heure_retour_estime_dt:
            return JsonResponse({"success": False, "error": "Heure de retour au mauvais format."})

        tournee = Tournee.objects.get(nom=nomTournee, is_done=False)
        tournee.heure_retour_estime = heure_retour_estime_dt
        tournee.save(update_fields=["heure_retour_estime"])

        # Figer la tournée si tout est ok
        if all(tc.heure_passage for tc in tournee.tourneecommande_set.all()):
            tournee.is_figee = True
            tournee.save(update_fields=["is_figee"])
        
        return JsonResponse({"success": True, "message": "Heure de retour estimée mise à jour avec succès."})
    except Exception as e:
        logger.error(f"Erreur dans update_heure_retour_estime : {e}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)})





@csrf_exempt
def set_delivered(request, commande_id):
    """Marquer la commande comme livrée"""
    try:
        commande = Commande.objects.get(id=commande_id)
        commande.set_delivered()
        return JsonResponse({'status': 'success', 'message': 'Commande marquée comme livrée.'})
    except Commande.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Commande introuvable.'}, status=404)
    
@csrf_exempt
def set_tournee_shipped(request, tournee_nom):
    if request.method == 'POST':
        try:
            tournee = Tournee.objects.get(nom=tournee_nom, is_sent_livreur=True)
            heure_shipped = timezone.now()

            commandes = tournee.tourneecommande_set.select_related('commande')
            for tournee_commande in commandes:
                commande = tournee_commande.commande
                commande.is_shipped = True
                commande.heure_shipped = heure_shipped
                commande.save(update_fields=['is_shipped', 'heure_shipped'])

            return JsonResponse({'status': 'success', 'message': 'Tournée et commandes marquées comme expédiées.'})
        except Tournee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournée introuvable.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Requête non valide.'}, status=400)


@csrf_exempt
@require_POST
def mark_tournee_as_done(request, tournee_nom):
    try:
        # Récupérer la tournée par son nom et la marquer comme terminée
        tournee = get_object_or_404(Tournee, nom=tournee_nom)
        tournee.is_done = True
        
        # Mettre à jour le champ is_booked du livreur associé
        if tournee.livreur:
            tournee.livreur.is_booked = False
            tournee.livreur.save(update_fields=['is_booked'])
        
        tournee.save(update_fields=['is_done'])
        
        return JsonResponse({'status': 'success', 'message': 'La tournée est maintenant terminée.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@csrf_exempt
def update_heure_retour_reel(request, nomTournee):
    if request.method == "POST":
        try:
            tournee = Tournee.objects.get(nom=nomTournee, is_done=False)
            heure_retour_reel = timezone.localtime()  # <--- ici ! c'est un datetime, pas un time
            tournee.heure_retour_reel = heure_retour_reel
            tournee.is_done = True
            tournee.save(update_fields=["heure_retour_reel", "is_done"])
            return JsonResponse({
                "success": True, 
                "message": "Heure de retour réelle mise à jour avec succès.",
                "heure_retour_reel": heure_retour_reel.strftime("%Y-%m-%d %H:%M:%S")
            })
        except Tournee.DoesNotExist:
            return JsonResponse({"success": False, "error": "Tournée introuvable."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Méthode non autorisée"})


from django.shortcuts import render
from .models import Tournee

from django.core.serializers.json import DjangoJSONEncoder
import json
import pprint


import logging

logger = logging.getLogger("swigo.tournee")

def vue_livreurs_tournees(request):
    from .models import Tournee  # adapte si besoin
    tournees = Tournee.objects.filter(
        is_ready_for_delivery=True,
        is_sent_livreur=True,
        is_done=False,
        livreur__isnull=False
    ).select_related('livreur')

    tournees_data = []

    for tournee in tournees:
        commandes = tournee.tourneecommande_set.select_related('commande').all()

        commandes_data = [
            {
                'id': tc.commande.id,
                'adresse': tc.commande.adresse_livraison.adresse,
                'ville': tc.commande.adresse_livraison.ville,
                'latitude': tc.commande.adresse_livraison.latitude,
                'longitude': tc.commande.adresse_livraison.longitude,
                'telephone': tc.commande.client.numero_telephone if tc.commande.client else None,
                'is_delivered': tc.commande.is_delivered,
                'has_message_for_livreur': 'true' if tc.commande.message_pour_livreur else 'false',
                'message_pour_livreur': tc.commande.message_pour_livreur or '',
                'paiement_a_recevoir': 'true' if not tc.commande.is_paid else 'false',
                # Format local "HH:MM", ou '-' si None
                'heure_passage': localtime(tc.heure_passage).strftime('%H:%M') if tc.heure_passage else '-',
            }
            for tc in commandes
        ]

        tournees_data.append({
            'tournee': {
                'nom': str(tournee.nom),
                'livreur': tournee.livreur.nom,
                'date_tournee': tournee.date_tournee.strftime('%Y-%m-%d'),
                'heure_depart': localtime(tournee.heure_depart).strftime('%H:%M') if tournee.heure_depart else '-',
                'heure_retour_estime': localtime(tournee.heure_retour_estime).strftime('%H:%M') if tournee.heure_retour_estime else '-',
                'is_started': tournee.is_started,
                'is_figee': getattr(tournee, 'is_figee', False),
            },
            'commandes': commandes_data
        })

    context = {
        'tournees_data': tournees_data,
        'tournees_data_json': json.dumps(tournees_data, cls=DjangoJSONEncoder),
    }

    return render(request, 'assets/tournees_livreurs.html', context)







from django.shortcuts import render, get_object_or_404
from .models import Tournee, TourneeCommande

from django.core.serializers.json import DjangoJSONEncoder
import pprint


def tournee_detail(request, tournee_nom):
    from django.core.exceptions import ObjectDoesNotExist

    tournee = get_object_or_404(Tournee, nom=tournee_nom)
    
    commandes = TourneeCommande.objects.filter(
        tournee=tournee
    ).select_related('commande__adresse_livraison', 'commande__client')

    commandes_data = []
    for commande in commandes:
        cmd = commande.commande
        try:
            montant = str(cmd.panier_associe.prix_total)
        except ObjectDoesNotExist:
            montant = '0.00'

        commandes_data.append({
            'commande_id': cmd.id,
            'adresse': cmd.adresse_livraison.adresse,
            'heure_passage': commande.heure_passage.strftime('%H:%M:%S') if commande.heure_passage else '-',
            'latitude': cmd.adresse_livraison.latitude,
            'longitude': cmd.adresse_livraison.longitude,
            'telephone': cmd.client.numero_telephone if cmd.client else "Numéro non disponible",
            'has_message_for_livreur': 'true' if cmd.message_pour_livreur else 'false',
            'message_pour_livreur': cmd.message_pour_livreur or '',
            'is_delivered': cmd.is_delivered,
            'paiement_a_recevoir': 'true' if not cmd.is_paid else 'false',
            'montant': montant,
            'mode_paiement': cmd.moyen_paiement or 'Non précisé',
        })

    return render(request, 'assets/tournee_detail.html', {
        'tournee': tournee,
        'commandes': commandes_data,
    })





def get_livreurs_disponibles(request):
    livreurs = Livreur.objects.filter(au_travaille=True)

    # Log et print pour le débogage
    logger.info(f"Nombre de livreurs au travail: {livreurs.count()}")
    print(f"Nombre de livreurs au travail: {livreurs.count()}")

    livreurs_data = []
    for livreur in livreurs:
        # Récupérer toutes les tournées non terminées pour lesquelles le livreur est réservé
        tournees = Tournee.objects.filter(livreur=livreur, is_done=False)
        heures_retour_estimees = [tournee.heure_retour_estime.strftime('%H:%M') for tournee in tournees if tournee.heure_retour_estime]
        num_tournees = [tournee.nom for tournee in tournees]  # Récupérer tous les numéros de tournées

        # Si aucune heure de retour estimée n'est trouvée, définir sur 'Non spécifiée'
        heures_retour_estimees = heures_retour_estimees if heures_retour_estimees else ['-']

        # Log et print pour le débogage
        logger.info(f"Livreur: {livreur.nom}, Téléphone: {livreur.telephone}, is_booked: {livreur.is_booked}, Heures de retour estimées: {heures_retour_estimees}, Numéros de tournées: {num_tournees}")
        print(f"Livreur: {livreur.nom}, Téléphone: {livreur.telephone}, is_booked: {livreur.is_booked}, Heures de retour estimées: {heures_retour_estimees}, Numéros de tournées: {num_tournees}")

        livreurs_data.append({
            'nom': livreur.nom,
            'telephone': livreur.telephone,
            'is_booked': livreur.is_booked,
            'heures_retour_estimees': heures_retour_estimees,
            'num_tournees': num_tournees  # Ajouter tous les numéros de tournées
        })

    return JsonResponse({'livreurs': livreurs_data})


def get_livreurs_disponibles_bar(request):
    livreurs = Livreur.objects.filter(au_travaille=True)

    # Log et print pour le débogage
    logger.info(f"Nombre de livreurs au travail pour le bar: {livreurs.count()}")
    print(f"Nombre de livreurs au travail pour le bar: {livreurs.count()}")

    livreurs_data = []
    for livreur in livreurs:
        # Récupérer toutes les tournées non terminées pour lesquelles le livreur est réservé
        tournees_actuelles = Tournee.objects.filter(livreur=livreur, is_done=False)
        heures_retour_estimees = []
        num_tournees = []

        # Si des tournées actuelles existent, récupérer les numéros de tournées et les heures de retour estimées
        for tournee in tournees_actuelles:
            num_tournees.append(tournee.nom)
            if tournee.heure_retour_estime:
                heures_retour_estimees.append(tournee.heure_retour_estime.strftime('%H:%M'))

        # Si aucune heure de retour estimée n'est trouvée, définir sur 'Non spécifiée'
        heures_retour_estimees = heures_retour_estimees if heures_retour_estimees else ['-']
        num_tournees = num_tournees if num_tournees else ['-']

        # Log et print pour le débogage
        logger.info(f"Livreur: {livreur.nom}, Téléphone: {livreur.telephone}, is_booked: {livreur.is_booked}, Heures de retour estimées: {heures_retour_estimees}, Numéros de tournées: {num_tournees}")
        print(f"Livreur: {livreur.nom}, Téléphone: {livreur.telephone}, is_booked: {livreur.is_booked}, Heures de retour estimées: {heures_retour_estimees}, Numéros de tournées: {num_tournees}")

        livreurs_data.append({
            'nom': livreur.nom,
            'telephone': livreur.telephone,
            'is_booked': livreur.is_booked,
            'heures_retour_estimees': heures_retour_estimees,
            'num_tournees': num_tournees
        })

    return JsonResponse({'livreurs': livreurs_data})




from django.shortcuts import render
from collections import OrderedDict
from .models import Ingredient, GROUPE_CHOICES, Fournisseur

from .models import ListeDeCourses


# swigo/views.py

def assets_gestionnaire_stock(request):
    print("assets_gestionnaire_stock appelée")
    
    # Initialiser un OrderedDict avec les groupes définis dans GROUPE_CHOICES
    groupes = OrderedDict(GROUPE_CHOICES)
    print(f"Groupes : {groupes}")
    
    # Préparer un OrderedDict pour stocker les ingrédients par groupe
    ingredients_par_groupe = OrderedDict((groupe, []) for groupe, _ in GROUPE_CHOICES)
    print(f"Ingrédients par groupe initialisé")
    
    # Récupérer tous les ingrédients, ordonnés par groupe et nom
    ingredients = Ingredient.objects.all().order_by('groupe', 'nom')
    print(f"Nombre d'ingrédients récupérés : {ingredients.count()}")
    
    # Organiser les ingrédients par groupe
    for ingredient in ingredients:
        ingredients_par_groupe[ingredient.groupe].append(ingredient)
    print(f"Ingrédients organisés par groupe")
    
    # Convertir en liste de tuples pour itération facile dans le template
    groupes_ingredients = [
        (groupes[groupe], ingredients_par_groupe[groupe])
        for groupe in groupes.keys()
    ]
    print(f"Groupes et ingrédients préparés pour le contexte")
    
    # Récupérer tous les fournisseurs (si nécessaire pour d'autres fonctionnalités)
    fournisseurs = Fournisseur.objects.all()
    fournisseurs_list = [
        {'id': fournisseur.id, 'nom': fournisseur.nom}
        for fournisseur in fournisseurs
    ]
    
    # Récupérer uniquement les fournisseurs ayant au moins une liste de courses active (non archivée)
    fournisseurs_actifs = Fournisseur.objects.filter(
        listes_de_courses__archived=False
    ).distinct()
    fournisseurs_actifs_list = [
        {'id': fournisseur.id, 'nom': fournisseur.nom}
        for fournisseur in fournisseurs_actifs
    ]
    print(f"Fournisseurs actifs : {fournisseurs_actifs_list}")
    
    context = {
        'groupes_ingredients': groupes_ingredients,
        'fournisseurs': fournisseurs_list,            # Tous les fournisseurs (si nécessaire)
        'fournisseurs_actifs': fournisseurs_actifs_list,  # Fournisseurs avec des listes actives
    }
    print(f"Contexte préparé : {context.keys()}")
    
    return render(request, 'assets/gestionnaire_stock.html', context)





# swigo/views.py

import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from .models import Fournisseur, ListeDeCourses, ArticleListeDeCourses, Ingredient

def generate_unique_nom(fournisseur, liste_date):
    """
    Génère un nom unique pour la liste de courses basé sur le fournisseur, la date et un compteur.
    Exemple : METRO_20241117_1, METRO_20241117_2, etc.
    """
    date_str_formatted = liste_date.strftime("%Y%m%d")
    base_nom = f"{fournisseur.nom}_{date_str_formatted}"
    compteur = 1
    unique_nom = f"{base_nom}_{compteur}"
    
    while ListeDeCourses.objects.filter(nom=unique_nom).exists():
        compteur += 1
        unique_nom = f"{base_nom}_{compteur}"
    
    return unique_nom

@require_POST
def ajouter_a_la_liste_de_courses(request, ingredient_id, fournisseur_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))
        date_str = data.get('date')  # Format attendu : YYYY-MM-DD
        liste_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
    except (ValueError, json.JSONDecodeError) as e:
        messages.error(request, "Données invalides fournies.")
        return redirect('swigo:assets_gestionnaire_stock')
    
    # Tenter de récupérer une liste active (non archivée) pour le fournisseur et la date
    liste_de_courses, created = ListeDeCourses.objects.get_or_create(
        fournisseur=fournisseur,
        date=liste_date,
        archived=False,
        defaults={
            'nom': generate_unique_nom(fournisseur, liste_date)
        }
    )
    
    if created:
        print(f"Nouvelle liste de courses créée : {liste_de_courses.nom}")
    else:
        print(f"Liste de courses existante récupérée : {liste_de_courses.nom}")
    
    # Ajout ou mise à jour de l'article dans la liste
    article, article_cree = ArticleListeDeCourses.objects.get_or_create(
        liste=liste_de_courses,
        ingredient=ingredient,
        defaults={
            'quantite': quantity,
            'unite': ingredient.unite_stock,
            'prix_unitaire_achat': ingredient.prix_unitaire_achat
        }
    )
    
    if not article_cree:
        # Mise à jour de la quantité existante
        print(f"Article existant trouvé : {article}")
        article.quantite += quantity
        article.save()
        print(f"Quantité mise à jour pour l'article {article.id} : {article.quantite}")
    else:
        print(f"Nouvel article créé avec quantité : {article.quantite}")
    
    messages.success(request, f"L'ingrédient '{ingredient.nom}' a été ajouté à votre liste de courses '{liste_de_courses.nom}' chez {fournisseur.nom}.")
    return redirect('swigo:liste_de_courses', fournisseur_id=fournisseur.id)









def afficher_liste_de_courses(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    
    # Récupérer toutes les listes non archivées pour le fournisseur, triées par date décroissante
    listes_de_courses = ListeDeCourses.objects.filter(fournisseur=fournisseur, archived=False).order_by('-date', '-archived_at')
    
    context = {
        'fournisseur': fournisseur,
        'listes_de_courses': listes_de_courses,
    }
    
    return render(request, 'assets/liste_de_courses.html', context)




# swigo/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def supprimer_article_liste_de_courses(request, article_id):
    try:
        article = get_object_or_404(ArticleListeDeCourses, id=article_id)
        liste = article.liste
        fournisseur = liste.fournisseur
        article.delete()
        
        message = f"L'article a été supprimé de la liste de courses '{liste.nom}' chez {fournisseur.nom}."
        
        return JsonResponse({'status': 'success', 'message': message})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



def archiver_liste_de_courses(request, liste_id):
    # Récupérer la liste de courses active
    liste = get_object_or_404(ListeDeCourses, id=liste_id, archived=False)
    
    # Archiver la liste
    liste.archived = True
    liste.archived_at = timezone.now()
    liste.save()
    
    # Ajouter un message de succès
    messages.success(request, f"La liste de courses '{liste.nom}' a été archivée.")
    
    # Rediriger vers la page des listes de courses pour le fournisseur
    return redirect('swigo:liste_de_courses', fournisseur_id=liste.fournisseur.id)
    
def supprimer_liste_de_courses(request, liste_id):
    liste = get_object_or_404(ListeDeCourses, id=liste_id)
    fournisseur_id = liste.fournisseur.id
    liste.delete()
    messages.success(request, f"La liste de courses '{liste.nom}' a été supprimée.")
    return redirect('swigo:liste_de_courses', fournisseur_id=fournisseur_id)




def toggle_article_achete(request, article_id):
    if request.method == "POST":
        article = get_object_or_404(ArticleListeDeCourses, id=article_id)
        article.est_achete = not article.est_achete  # Change l'état
        article.save()  # Enregistre l'état dans la base de données
        return JsonResponse({"success": True, "est_achete": article.est_achete})
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

def save_article_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = data.get('order', [])
        
        for index, article_id in enumerate(order):
            ArticleListeDeCourses.objects.filter(id=article_id).update(order=index)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


import logging
logger = logging.getLogger(__name__)

from decimal import Decimal, InvalidOperation

def ajouter_stock(request, ingredient_id):
    if request.method == 'POST':
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        try:
            data = json.loads(request.body)
            quantity_input = data.get('quantity', '0')
            price_per_unit_input = data.get('price_per_unit', '0.0')

            # Convertir les entrées en Decimal
            quantity = Decimal(str(quantity_input))
            price_per_unit = Decimal(str(price_per_unit_input))

            if quantity <= 0 or price_per_unit <= 0:
                return JsonResponse({'error': 'Quantité et prix doivent être supérieurs à zéro.'}, status=400)

            # Récupérer les anciennes valeurs
            ancienne_quantite = ingredient.quantite_stock or Decimal('0')
            ancien_prix = ingredient.prix_unitaire_achat or Decimal('0')

            # Calculer la nouvelle quantité totale
            nouvelle_quantite = ancienne_quantite + quantity

            # Calculer le nouveau prix moyen pondéré
            if ancienne_quantite == 0:
                nouveau_prix = price_per_unit
            else:
                cout_total_ancien = ancienne_quantite * ancien_prix
                cout_total_nouveau = quantity * price_per_unit
                cout_total = cout_total_ancien + cout_total_nouveau
                nouveau_prix = cout_total / nouvelle_quantite

            # Mettre à jour l'ingrédient
            ingredient.quantite_stock = nouvelle_quantite
            ingredient.prix_unitaire_achat = nouveau_prix
            ingredient.save()

            # Enregistrer le mouvement de stock
            MouvementStock.objects.create(
                ingredient=ingredient,
                quantity=quantity,
                price_per_unit=price_per_unit
            )

            return JsonResponse({'success': True, 'message': 'Stock ajouté avec succès.'})
        except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError) as e:
            print(f"Exception during ajouter_stock: {e}")
            return JsonResponse({'error': 'Données invalides.'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    

def afficher_mouvements_stock(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    mouvements = ingredient.mouvements_stock.order_by('-date')
    context = {
        'ingredient': ingredient,
        'mouvements': mouvements,
    }
    return render(request, 'swigo/afficher_mouvements_stock.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import SaladePersonnalisee
from .forms import SaladePersonnaliseeForm
from decimal import Decimal

@csrf_exempt
def creer_salade_personnalisee(request):
    if request.method == 'POST':
        form = SaladePersonnaliseeForm(request.POST)
        if form.is_valid():
            # Étape 1 : Création sans M2M
            salade = form.save(commit=False)
            salade.save()  # Enregistre l'objet principal

            # Étape 2 : Ajout des M2M
            form.save_m2m()

            # Étape 3 : Calcul du prix total
            salade.calculate_prix_total()
            salade.save(update_fields=['prix_total'])

            # Étape 4 : Déduction du stock
            try:
                salade.deduire_ingredients_stock()
            except Exception as e:
                print(f"⚠️ Erreur déduction stock : {e}")

            return redirect('confirmation_salade')  # Page de confirmation
    else:
        form = SaladePersonnaliseeForm()

    return render(request, 'creer_salade_personnalisee.html', {'form': form})


from django.http import JsonResponse
from .forms import SaladePersonnaliseeForm

def get_salade_options(request):
    form = SaladePersonnaliseeForm()
    data = {
        'base': form.fields['base'].choices,
        'proteine': form.fields['proteine'].choices,
        'garnitures': form.fields['garnitures'].choices,
        'toppings': form.fields['toppings'].choices,
        'sauce': form.fields['sauce'].choices,
    }
    return JsonResponse(data)



from decimal import Decimal
import json
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from swigo.models import Commande, Plat, Ingredient, SaladePersonnalisee, ArticlePanier


@csrf_exempt
def ajouter_salade_personnalisee(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        print("✅ Données reçues :", data)

        base_id = data.get('base')
        sauce_id = data.get('sauce')

        if not base_id or not sauce_id:
            return JsonResponse({'error': 'Base ou sauce manquante ou invalide.'}, status=400)

        commande_id = request.session.get('commande_id')
        if not commande_id:
            return JsonResponse({'error': 'Commande non trouvée'}, status=400)

        commande = Commande.objects.get(id=commande_id)
        panier = commande.panier
        if not panier:
            return JsonResponse({'error': 'Panier introuvable'}, status=400)

        plat_salade = Plat.objects.get(nom__iexact="Salade Personnalisée")
        base = Ingredient.objects.get(id=base_id)
        sauce = Ingredient.objects.get(id=sauce_id)

        with transaction.atomic():
            # 1. Création et sauvegarde initiale
            salade = SaladePersonnalisee(base=base, sauce=sauce)
            salade.save()  # nécessaire avant les .set()

            def assign(field_name, ids, set_func):
                ids = [int(i) for i in ids if str(i).isdigit()]
                if not ids:
                    print(f"⚠️ Aucun ID pour {field_name}")
                    return
                ingredients = Ingredient.objects.filter(id__in=ids)
                found_ids = set(ingredients.values_list('id', flat=True))
                missing = set(ids) - found_ids
                if missing:
                    raise Ingredient.DoesNotExist(f"{field_name} manquants : {', '.join(str(i) for i in missing)}")
                set_func(ingredients)
                print(f"🟢 {field_name.title()} : {[f'{i.nom} ({i.id})' for i in ingredients]}")

            # 2. Affectation M2M
            assign("protéines", data.get("proteines", []), salade.proteines.set)
            assign("garnitures", data.get("garnitures", []), salade.garnitures.set)
            assign("toppings", data.get("toppings", []), salade.toppings.set)
            assign("suppléments", data.get("supplements", []), salade.supplement.set)

            # 3. Vérification après set()
            print("📦 Vérif ingrédients après .set()")
            print(" - Protéines :", list(salade.proteines.values_list("nom", flat=True)))
            print(" - Garnitures :", list(salade.garnitures.values_list("nom", flat=True)))
            print(" - Toppings :", list(salade.toppings.values_list("nom", flat=True)))
            print(" - Suppléments :", list(salade.supplement.values_list("nom", flat=True)))

            # 4. Calcul prix & sauvegarde finale
            prix_calcule = salade.calculate_prix_total()
            salade.save()
            print(f"🧮 Prix total salade : {prix_calcule} € TTC")

            # 5. Déduction stock
            salade.deduire_ingredients_stock()

            # 6. Création article panier
            article = ArticlePanier.objects.create(
                panier=panier,
                plat=plat_salade,
                quantite=1,
                prix_total=prix_calcule,
                salade_personnalisee=salade
            )
            print(f"🧾 Article ajouté au panier : {article} ({article.quantite}x, {article.prix_total} €)")

            # 7. Mise à jour panier
            panier.calculate_total_price()
            print(f"🛒 Total panier : {panier.prix_total} €")

            # 8. Données de retour
            cart_items_data = get_cart_items(panier)
            totals_data = {
                'sous_total': str(panier.sous_total),
                'frais_livraison': str(panier.frais_livraison_effectif),
                'reduction': str(panier.promotion or 0),
                'prix_total': str(panier.prix_total)
            }

            code_promo_data = None
            if panier.code_promo and panier.code_promo.est_valide():
                code_promo_data = {
                    'code': panier.code_promo.code,
                    'valeur': str(panier.promotion)
                }

            return JsonResponse({
                'success': True,
                'cart_items': cart_items_data,
                'totals': totals_data,
                'code_promo': code_promo_data
            })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except (Commande.DoesNotExist, Plat.DoesNotExist, Ingredient.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=404)
    except transaction.TransactionManagementError as e:
        return JsonResponse({'error': "Erreur transactionnelle : " + str(e)}, status=500)
    except Exception as e:
        print("❌ Erreur inattendue :", e)
        return JsonResponse({'error': str(e)}, status=500)







@csrf_exempt  # à enlever si tu gères déjà CSRF avec token dans ton JS
@require_POST
def changer_mode_livraison(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    nouveau_mode = request.POST.get('mode')  # attend 'emporter' ou 'livraison'

    if nouveau_mode not in ['emporter', 'livraison']:
        return JsonResponse({'error': 'Mode invalide'}, status=400)

    if nouveau_mode == 'emporter':
        commande.is_commande_a_emporter = True
        # Ici tu peux aussi adapter le statut si besoin
        commande.statut = 'EN_ATTENTE_EMPORTER'  # adapte selon tes statuts
    else:
        commande.is_commande_a_emporter = False
        commande.statut = 'EN_ATTENTE_LIVRAISON'  # adapte selon tes statuts

    commande.save()
    return JsonResponse({'success': True, 'nouveau_mode': nouveau_mode})



from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import Facture, LigneFacture, Commande

def generer_numero_facture():
    today = timezone.now().date()
    prefix = f"FAC-{today.year}-"
    last = Facture.objects.filter(numero__startswith=prefix).order_by('numero').last()
    if last:
        last_number = int(last.numero.split('-')[-1])
        return f"{prefix}{last_number + 1:04d}"
    return f"{prefix}0001"

from decimal import Decimal
from collections import defaultdict
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from .models import Facture, LigneFacture, Commande
import logging

logger = logging.getLogger(__name__)

def generer_facture_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if hasattr(commande, 'facture'):
        return redirect('swigo:facture_detail', facture_id=commande.facture.id)

    if not commande.is_paid:
        return HttpResponse("Impossible de générer une facture pour une commande non payée.", status=400)

    panier = commande.panier
    client = commande.client
    numero = generer_numero_facture()
    societe = getattr(commande, 'societe', '') or ''
    adresse_facturation = (
        getattr(commande, 'adresse_facturation_saisie', '') or
        (client.adresse_facturation.strip() if client and client.adresse_facturation else
        (f"{commande.adresse_livraison.adresse}, {commande.adresse_livraison.code_postal} {commande.adresse_livraison.ville}" if commande.adresse_livraison else ""))
    )
    facture_sans_detail = getattr(commande, 'facture_sans_detail', False)

    montant_ht = Decimal('0.00')
    montant_tva = Decimal('0.00')
    montant_ttc = panier.prix_total or Decimal('0.00')
    tva_par_taux = defaultdict(Decimal)

    facture = Facture.objects.create(
        numero=numero,
        commande=commande,
        client=client,
        societe=societe,
        date_emission=timezone.now(),
        montant_ht=Decimal('0.00'),
        montant_tva=Decimal('0.00'),
        montant_ttc=montant_ttc,
        deja_reglee=commande.is_paid,
        adresse_facturation=adresse_facturation,
        facture_sans_detail=facture_sans_detail,
    )

    def ajouter_ligne(description, quantite, prix_ttc, taux_tva):
        nonlocal montant_ht, montant_tva, tva_par_taux
        prix_ht = prix_ttc / (Decimal('1.0') + taux_tva / Decimal('100.0'))
        montant_ht_ligne = prix_ht * quantite
        montant_tva_ligne = montant_ht_ligne * taux_tva / Decimal('100.0')

        LigneFacture.objects.create(
            facture=facture,
            description=description,
            quantite=quantite,
            prix_unitaire_ht=prix_ht,
            taux_tva=taux_tva,
            montant_ht=montant_ht_ligne,
            montant_tva=montant_tva_ligne,
            montant_ttc=prix_ttc * quantite
        )

        montant_ht += montant_ht_ligne
        montant_tva += montant_tva_ligne
        tva_par_taux[taux_tva] += montant_tva_ligne

    for article in panier.articlepanier_set.all():
        quantite = article.quantite
        if not quantite:
            continue

        if article.plat:
            prix_ttc = article.plat.prix_unitaire_ttc
            taux_tva = Decimal(str(article.plat.taux_tva))
            description = article.plat.nom
        elif article.salade_personnalisee:
            prix_ttc = article.salade_personnalisee.prix_total
            taux_tva = Decimal('10.0')
            description = str(article.salade_personnalisee)
        elif article.couscous_personnalise:
            prix_ttc = article.couscous_personnalise.prix_total
            taux_tva = Decimal('10.0')
            description = str(article.couscous_personnalise)
        else:
            continue

        if prix_ttc:
            if facture_sans_detail:
                ht = (prix_ttc * quantite) / (Decimal('1.0') + taux_tva / Decimal('100.0'))
                tva = ht * taux_tva / Decimal('100.0')
                montant_ht += ht
                montant_tva += tva
                tva_par_taux[taux_tva] += tva
            else:
                ajouter_ligne(description, quantite, prix_ttc, taux_tva)

    for frais, taux, label in [
        (panier.frais_livraison_effectif, Decimal('20.0'), "Frais de livraison"),
        (panier.frais_gestion, Decimal('20.0'), "Frais de gestion")
    ]:
        if frais and frais > 0:
            if facture_sans_detail:
                ht = frais / (Decimal('1.0') + taux / Decimal('100.0'))
                tva = ht * taux / Decimal('100.0')
                montant_ht += ht
                montant_tva += tva
                tva_par_taux[taux] += tva
            else:
                ajouter_ligne(label, 1, frais, taux)

    facture.montant_ht = montant_ht
    facture.montant_tva = montant_tva
    facture.tva_par_taux = {str(float(k)): float(v) for k, v in tva_par_taux.items()}
    facture.save()

    return redirect('swigo:facture_detail', facture_id=facture.id)












def facture_detail(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    tva_par_taux = request.session.pop('tva_par_taux', None)

    if not isinstance(tva_par_taux, dict) or not tva_par_taux:
        tva_par_taux = {}
        panier = getattr(facture.commande, 'panier', None)

        if facture.facture_sans_detail and panier:
            # 💡 Recalcul TVA si facture sans détail
            def ajouter_tva(ttc, taux):
                ht = ttc / (1 + taux / 100)
                tva = ht * taux / 100
                tva_par_taux[taux] = tva_par_taux.get(taux, 0.0) + float(tva)

            for article in panier.articlepanier_set.all():
                quantite = article.quantite or 0
                if quantite == 0:
                    continue

                if article.plat:
                    taux = float(article.plat.taux_tva)
                    prix_ttc = article.plat.prix_unitaire_ttc
                elif article.salade_personnalisee:
                    taux = 10.0
                    prix_ttc = article.salade_personnalisee.prix_total
                elif article.couscous_personnalise:
                    taux = 10.0
                    prix_ttc = article.couscous_personnalise.prix_total
                else:
                    continue

                if prix_ttc:
                    ajouter_tva(float(prix_ttc) * quantite, taux)

            # TVA sur frais fixes (livraison et gestion)
            for frais, taux in [(panier.frais_livraison_effectif, 20.0), (panier.frais_gestion, 20.0)]:
                if frais and frais > 0:
                    ajouter_tva(float(frais), taux)

        else:
            # 💡 TVA directe depuis les lignes de la facture
            for ligne in facture.lignes.all():
                taux = float(ligne.taux_tva)
                montant_tva = float(ligne.montant_tva)
                tva_par_taux[taux] = tva_par_taux.get(taux, 0.0) + montant_tva

    return render(request, "assets/facture_detail.html", {
        "facture": facture,
        "tva_par_taux": tva_par_taux
    })




def mentions_rgpd(request):
    return render(request, 'swigo/mentions_et_rgpd.html')

from .models import (
    ArticlePanier,
    CouscousPersonnalise,
    FormuleCouscous,
    ViandeCouscous,
    ChoixViandeCouscous,
    OptionXL,
)

def personnaliser_couscous(request):
    if request.method == 'POST':
        formule_id = request.POST.get('formule_id')
        viandes_inclues_ids = request.POST.getlist('viandes_inclues')
        viandes_supp_ids = request.POST.getlist('viandes_supplement')
        option_xl = request.POST.get('option_xl') == 'on'

        couscous = CouscousPersonnalise.objects.create(
            client=request.user.client,
            formule_id=formule_id,
            option_xl=option_xl
        )

        for viande_id in viandes_inclues_ids:
            ChoixViandeCouscous.objects.create(couscous=couscous, viande_id=viande_id, est_incluse=True)

        for viande_id in viandes_supp_ids:
            ChoixViandeCouscous.objects.create(couscous=couscous, viande_id=viande_id, est_incluse=False)

        couscous.calculate_prix_total()
        couscous.save()

        return redirect('ajouter_au_panier_couscous', couscous_id=couscous.id)

    else:
        formules = FormuleCouscous.objects.all()
        viandes = ViandeCouscous.objects.all()
        option_xl = OptionXL.objects.first()
        return render(request, 'commande/couscous_form.html', {
            'formules': formules,
            'viandes': viandes,
            'option_xl': option_xl,
        })


def get_panier_utilisateur(request):
    client = request.user.client
    panier, _ = Panier.objects.get_or_create(client=client, en_cours=True)
    return panier

def ajouter_au_panier_couscous(request, couscous_id):
    panier = get_panier_utilisateur(request)
    couscous = CouscousPersonnalise.objects.get(id=couscous_id)

    article = ArticlePanier.objects.create(
        panier=panier,
        couscous_personnalise=couscous,
        quantite=1
    )
    article.calculate_total_price()

    return redirect('page_panier')


from django.http import JsonResponse
from .models import FormuleCouscous, ViandeCouscous, OptionXL

from django.http import JsonResponse
from .models import FormuleCouscous, ViandeCouscous, AccompagnementCouscous

def get_couscous_options(request):
    formules = FormuleCouscous.objects.all().values_list('id', 'nom', 'prix_base_ttc')
    viandes_incluses = ViandeCouscous.objects.all().values_list('id', 'nom', 'supplement_inclus')
    accompagnements = AccompagnementCouscous.objects.all().values_list('code', 'nom')

    return JsonResponse({
        'formules': list(formules),
        'viandes_incluses': list(viandes_incluses),
        'accompagnements': list(accompagnements),
    })



from django.shortcuts import render, redirect
from .forms import CouscousPersonnaliseForm
from .models import ViandeCouscous

def creer_couscous_personnalise(request):
    if request.method == 'POST':
        form = CouscousPersonnaliseForm(request.POST)
        if form.is_valid():
            couscous = form.save(commit=False)
            couscous.save()

            # Récupérer les données brutes pour savoir quelles viandes ont été cochées comme incluses
            viandes_ids = request.POST.getlist('viandes_choisies')
            incluses_ids = request.POST.getlist('viandes_incluses')  # checkbox séparée pour "inclus"

            for viande_id in viandes_ids:
                est_incluse = viande_id in incluses_ids
                CouscousChoix = couscous.choixviandecouscous_set.create(
                    viande=ViandeCouscous.objects.get(id=viande_id),
                    est_incluse=est_incluse
                )

                # Déduction du stock
                viande = CouscousChoix.viande
                viande.quantite_stock -= 1
                viande.save(update_fields=['quantite_stock'])

            # Option XL stock (si tu veux gérer comme un ingrédient réel)
            if couscous.option_xl:
                # Déduire si tu veux un ingrédient spécifique (à définir dans le modèle)
                pass

            couscous.calculate_prix_total()
            couscous.save(update_fields=['prix_total'])

            return redirect('confirmation_couscous')

    else:
        form = CouscousPersonnaliseForm()

    return render(request, 'creer_couscous_personnalise.html', {'form': form})


from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import (
    Commande, Plat, Panier, ArticlePanier,
    CouscousPersonnalise, ChoixViandeCouscous,
    FormuleCouscous, ViandeCouscous, OptionXL
)

from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def ajouter_couscous_personnalise(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        print("Données reçues dans ajouter_couscous_personnalise:", data)

        formule_id = data.get('formule_id')
        viandes_choisies = data.get('viandes_choisies', [])
        accompagnements = data.get('accompagnements', [])  # facultatif
        xl = data.get('option_xl', False)

        commande_id = request.session.get('commande_id')
        if not commande_id:
            return JsonResponse({'error': 'Commande non trouvée'}, status=400)

        commande = Commande.objects.get(id=commande_id)
        panier = commande.panier
        if not panier:
            return JsonResponse({'error': 'Panier non trouvé pour cette commande'}, status=400)

        formule = FormuleCouscous.objects.get(id=formule_id)

        couscous = CouscousPersonnalise.objects.create(
            formule=formule,
            option_xl=xl
        )

        inclus_restants = formule.nombre_viandes_incluses
        prix_total = formule.prix_base_ttc

        viande_counts = {}
        for viande_id in viandes_choisies:
            viande_counts[viande_id] = viande_counts.get(viande_id, 0) + 1

        viande_labels = []
        for viande_id, quantite in viande_counts.items():
            viande = ViandeCouscous.objects.get(id=viande_id)
            for _ in range(quantite):
                est_incluse = inclus_restants > 0
                ChoixViandeCouscous.objects.create(
                    couscous=couscous,
                    viande=viande,
                    est_incluse=est_incluse
                )
                if est_incluse:
                    prix_total += viande.supplement_inclus
                    inclus_restants -= 1
                else:
                    prix_total += viande.supplement_extra
            viande_labels.append(f"{viande.nom} × {quantite}")

        acc_labels = []
        if accompagnements:
            for code in accompagnements:
                acc = AccompagnementCouscous.objects.filter(code=code).first()
                if acc:
                    couscous.accompagnements.add(acc)
                    acc_labels.append(acc.nom)

            # 🔍 Vérification immédiate de ce qui est bien lié
            enregistrés = list(couscous.accompagnements.values_list('nom', flat=True))
            print(f"✅ Accompagnements liés au couscous #{couscous.id} : {enregistrés}")
        else:
            print(f"⚠️ Aucun accompagnement reçu pour couscous #{couscous.id}")


        if xl:
            prix_total += Decimal("2.00")

        couscous.prix_total = prix_total
        couscous.save()

        # 🧾 Créer l'article avec un nom lisible = nom de formule
        ArticlePanier.objects.create(
            panier=panier,
            plat=None,
            quantite=1,
            couscous_personnalise=couscous,
            nom_personnalise=formule.nom,
            prix_total=prix_total
        )

        panier.calculate_total_price()

        # 🧾 Reformater les données du panier avec affichage adapté
        cart_items_data = get_cart_items(panier)
        for item in cart_items_data:
            if item.get('couscous_personnalise_id') == couscous.id:
                options = []
                if viande_labels:
                    options.append(f"Viandes incluses : {', '.join(viande_labels)}")
                if xl:
                    options.append("Option XL : Oui")
                if acc_labels:
                    options.append(f"Accompagnements : {', '.join(acc_labels)}")
                item['plat_nom'] = formule.nom
                item['options'] = options

        totals_data = {
            'sous_total': str(panier.sous_total),
            'frais_livraison': str(panier.frais_livraison_effectif),
            'reduction': str(panier.promotion or 0),
            'prix_total': str(panier.prix_total)
        }

        code_promo_data = None
        if panier.code_promo and panier.code_promo.est_valide():
            code_promo_data = {
                'code': panier.code_promo.code,
                'valeur': str(panier.promotion)
            }

        return JsonResponse({
            'success': True,
            'cart_items': cart_items_data,
            'totals': totals_data,
            'code_promo': code_promo_data
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Erreur de décodage JSON'}, status=400)
    except Commande.DoesNotExist:
        return JsonResponse({'error': 'Commande non trouvée'}, status=404)
    except FormuleCouscous.DoesNotExist:
        return JsonResponse({'error': 'Formule couscous non trouvée'}, status=404)
    except ViandeCouscous.DoesNotExist:
        return JsonResponse({'error': 'Une viande sélectionnée est introuvable'}, status=404)
    except Exception as e:
        print("Erreur inattendue:", e)
        return JsonResponse({'error': str(e)}, status=500)



from django.http import JsonResponse
from swigo.models import IngredientSaladeTag, Menu

from django.http import JsonResponse

def get_salade_options(request):
    """
    Retourne les ingrédients disponibles pour chaque type de composant de salade.
    Format : liste [id, nom, prix_supplement_salade] par catégorie (base, protéine, garniture, etc.)
    """

    def get_par_type(type_salade):
        tags = IngredientSaladeTag.objects.filter(type_salade=type_salade).select_related('ingredient')
        return [
            [
                tag.ingredient.id,
                tag.ingredient.nom,
                float(tag.ingredient.prix_supplement_salade or 0.00)
            ]
            for tag in tags
            if tag.ingredient  # sécurité supplémentaire
        ]

    data = {
        'base': get_par_type('base'),
        'proteine': get_par_type('proteine'),
        'garnitures': get_par_type('garniture'),
        'toppings': get_par_type('topping'),
        'sauces': get_par_type('sauce'),
    }

    return JsonResponse(data)


# views.py
from django.http import JsonResponse
from .models import Menu




def menus_par_categorie_ajax(request):
    try:
        menus = Menu.objects.filter(disponible=True)

        data = []
        for menu in menus:
            # Déterminer le type de menu pour l'affichage
            description_courte = "Menu à composer"
            description_longue = "Choisissez vos composants"
            
            # Adapter les descriptions selon le type de menu
            if "Burger ERC" in menu.nom:
                description_courte = "Burger + Accompagnement + Boisson"
                description_longue = "Burger ERC avec accompagnement au choix et boisson"
            elif "Couscous" in menu.nom:
                description_courte = "Couscous personnalisé"
                description_longue = "Choisissez vos viandes et accompagnements"
            elif "Crousty Tenders" in menu.nom:
                description_courte = "Crousty Tenders + Boisson"
                description_longue = "Crousty Tenders Original avec boisson"
            elif "Poulet Frit" in menu.nom:
                description_courte = "5 Tenders OU 5 Wings frits"
                description_longue = "Au choix avec accompagnement et boisson"
            elif "Poulet Josper" in menu.nom:
                description_courte = "5 Wings Grillés Josper"
                description_longue = "Wings grillés au Josper avec accompagnement et boisson"

            data.append({
                "id": menu.id,
                "nom": menu.nom,
                "description_courte": description_courte,
                "description_longue": description_longue,
                "prix_unitaire_ttc": str(menu.prix_ttc),
                "photo_url": menu.photo.url if menu.photo else "/static/images/default.jpg"
            })

        return JsonResponse({"menus": data})

    except Exception as e:
        import logging
        logging.exception("Erreur dans menus_par_categorie_ajax")
        return JsonResponse({"error": str(e)}, status=500)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import logging
from .models import Menu, Plat, ArticlePanier, ChoixMenuArticle, Panier, SaladePersonnalisee, CouscousPersonnalise

logger = logging.getLogger(__name__)

@csrf_exempt
def ajouter_menu_personnalise(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        logger.debug(f"[MENU PERSONNALISÉ] Données reçues : {data}")
        print("[MENU PERSONNALISÉ] Données reçues :", data)

        menu_id = int(data.get("menu_id"))
        choix = data.get("choix", {})
        viandes = data.get("viandes", {})
        
        print("=== DEBUG DONNÉES ===")
        print("Menu ID:", menu_id)
        print("Choix:", choix)
        print("Viandes:", viandes)
        print("=====================")

        # Gestion de la commande et panier
        commande_id = request.session.get("commande_id")
        if not commande_id:
            from swigo.models import Commande, Panier
            commande = Commande.objects.create(client=None, is_paid=False)
            request.session['commande_id'] = commande.id
            panier = Panier.objects.create(commande=commande, session_key=request.session.session_key)
        else:
            from swigo.models import Commande, Panier
            commande = Commande.objects.get(id=commande_id)
            panier = getattr(commande, 'panier_associe', None) or Panier.objects.create(commande=commande, session_key=request.session.session_key)

        menu = Menu.objects.get(id=menu_id)
        if menu.prix_ttc is None:
            return JsonResponse({"success": False, "error": "Le menu n'a pas de prix défini"}, status=400)

        # ==================== CONFIGURATION DES SUPPLÉMENTS ====================
        DESSERTS_AVEC_SUPPLEMENTS = [
            (111, 'Brownie Maison', Decimal('4.90'), Decimal('2.00'), True),
            (112, 'Cookie Maison', Decimal('2.90'), Decimal('0.00'), False),
            (113, 'Fondant Chocolat', Decimal('5.90'), Decimal('3.00'), True),
            (114, 'Tiramisu Café Classique', Decimal('5.20'), Decimal('2.30'), True),
            (115, 'Tiramisu Choco-Caramel', Decimal('5.50'), Decimal('2.60'), True),
            (116, 'Corne De Gazelle', Decimal('2.50'), Decimal('0.00'), False),
            (117, 'Chebakia Miel et Sésame', Decimal('2.50'), Decimal('0.00'), False),
            (118, 'Makrout Datte', Decimal('2.50'), Decimal('0.00'), False),
            (119, 'Briouate Amandes et Miel', Decimal('2.50'), Decimal('0.00'), False),
            (120, 'Assortiment marocain (4 pièces)', Decimal('8.90'), Decimal('6.00'), True),
        ]

        BOISSONS_AVEC_SUPPLEMENTS = [
            (99, 'Coca-Cola', Decimal('2.50'), Decimal('0.00'), False),
            (100, 'Coca-Cola Zero', Decimal('2.50'), Decimal('0.00'), False),
            (101, 'Fanta Orange', Decimal('2.50'), Decimal('0.00'), False),
            (102, 'Fanta Citron', Decimal('2.50'), Decimal('0.00'), False),
            (103, 'Ice Tea Pêche', Decimal('2.50'), Decimal('0.00'), False),
            (104, 'Oasis Tropical', Decimal('2.50'), Decimal('0.00'), False),
            (105, 'Sprite', Decimal('2.50'), Decimal('0.00'), False),
            (106, 'Schweppes Agrumes', Decimal('2.50'), Decimal('0.00'), False),
            (107, 'Hawai', Decimal('2.50'), Decimal('0.00'), False),
            (108, 'Red Bull', Decimal('3.50'), Decimal('1.00'), True),
            (109, 'Eau minérale', Decimal('2.00'), Decimal('0.00'), False),
            (110, 'Eau Pétillante', Decimal('2.00'), Decimal('0.00'), False),
            (121, 'Orangina', Decimal('2.50'), Decimal('0.00'), False),
        ]

        def calculer_supplement(choix_utilisateur):
            """Calcule le supplément total pour les desserts et boissons"""
            supplement_total = Decimal('0.00')
            supplements_detail = {}
            
            # Supplément desserts
            if 'dessert' in choix_utilisateur:
                for dessert_val in choix_utilisateur['dessert']:
                    if isinstance(dessert_val, str) and dessert_val.isdigit():
                        dessert_id = int(dessert_val)
                        for dessert_info in DESSERTS_AVEC_SUPPLEMENTS:
                            if dessert_info[0] == dessert_id and dessert_info[4]:
                                supplement_total += dessert_info[3]
                                supplements_detail['dessert'] = {
                                    'nom': dessert_info[1],
                                    'prix': str(dessert_info[3]),
                                    'id': dessert_id
                                }
                                print(f"🍰 Supplément dessert: {dessert_info[1]} +{dessert_info[3]}€")
            
            # Supplément boissons  
            if 'boisson' in choix_utilisateur:
                for boisson_val in choix_utilisateur['boisson']:
                    if isinstance(boisson_val, str) and boisson_val.isdigit():
                        boisson_id = int(boisson_val)
                        for boisson_info in BOISSONS_AVEC_SUPPLEMENTS:
                            if boisson_info[0] == boisson_id and boisson_info[4]:
                                supplement_total += boisson_info[3]
                                supplements_detail['boisson'] = {
                                    'nom': boisson_info[1],
                                    'prix': str(boisson_info[3]),
                                    'id': boisson_id
                                }
                                print(f"🥤 Supplément boisson: {boisson_info[1]} +{boisson_info[3]}€")
            
            return supplement_total, supplements_detail

        # ==================== GESTION COUSCOUS PERSONNALISÉ ====================
        couscous_perso_id = None
        supplement_couscous = Decimal('0.00')
        supplements_couscous_detail = {}

        # Vérifier si c'est un menu couscous
        choix_couscous_menu = menu.choix.filter(autorise_couscous_personnalise=True).first()

        if choix_couscous_menu and "incluses" in viandes and viandes["incluses"]:
            print("🎯 DÉTECTION MENU COUSCOUS PERSONNALISÉ")
            print(f"🥩 Viandes reçues: {viandes['incluses']}")
            
            # Récupérer les viandes choisies
            viandes_ids = viandes.get("incluses", [])
            viandes_choisies = ViandeCouscous.objects.filter(id__in=viandes_ids)
            
            # Déterminer la formule (1 viande incluse pour les menus midi)
            from swigo.models import FormuleCouscous, CouscousPersonnalise, ChoixViandeCouscous, AccompagnementCouscous
            formule_midi, created = FormuleCouscous.objects.get_or_create(
                nom="Menu Midi Couscous",
                defaults={
                    'nombre_viandes_incluses': 1,
                    'prix_base_ttc': Decimal('0.00'),
                    'description': 'Formule pour menus midi couscous'
                }
            )
            
            # Créer le couscous personnalisé
            couscous_perso = CouscousPersonnalise.objects.create(
                formule=formule_midi
            )
            
            # Ajouter les viandes avec gestion des inclusions/suppléments
            nombre_viandes_incluses = choix_couscous_menu.nombre_viandes_incluses or 1
            viandes_ajoutees = 0
            
            for viande in viandes_choisies:
                est_incluse = (viandes_ajoutees < nombre_viandes_incluses)
                
                # Créer le choix de viande
                ChoixViandeCouscous.objects.create(
                    couscous=couscous_perso,
                    viande=viande,
                    est_incluse=est_incluse
                )
                
                # Calculer le supplément si la viande n'est pas incluse
                if not est_incluse:
                    supplement_couscous += viande.supplement_inclus
                    supplements_couscous_detail[f'viande_{viande.id}'] = {
                        'nom': viande.nom,
                        'prix': str(viande.supplement_inclus),
                        'type': 'supplément'
                    }
                    print(f"🥩 Supplément viande: {viande.nom} +{viande.supplement_inclus}€")
                
                viandes_ajoutees += 1
            
            # Ajouter les accompagnements
            accompagnements_ids = viandes.get("accompagnements", [])
            if accompagnements_ids:
                accompagnements = AccompagnementCouscous.objects.filter(id__in=accompagnements_ids)
                couscous_perso.accompagnements.set(accompagnements)
                print(f"🥗 {accompagnements.count()} accompagnements ajoutés")
            
            couscous_perso_id = couscous_perso.id
            print(f"✅ Couscous personnalisé créé (ID: {couscous_perso_id})")
            print(f"   Viandes: {[v.nom for v in viandes_choisies]}")
            print(f"   Supplément couscous: {supplement_couscous}€")
            
            # ✅ CONSERVER CETTE PARTIE POUR LA COMPATIBILITÉ
            if 'couscous' not in choix:
                choix['couscous'] = []
            choix['couscous'].append(f"couscous_{couscous_perso_id}")
            print(f"✅ Couscous ajouté aux choix: couscous_{couscous_perso_id}")

        # ==================== CALCUL DU PRIX FINAL ET SUPPLÉMENTS ====================
        supplement_desserts_boissons, supplements_db_detail = calculer_supplement(choix)
        prix_final = menu.prix_ttc + supplement_desserts_boissons + supplement_couscous
        
        # 🆕 CONSTRUIRE L'OBJET SUPPLÉMENTS COMPLET
        total_supplements = supplement_desserts_boissons + supplement_couscous
        supplements_complet = {
            'total_supplements': str(total_supplements),
            'details': {**supplements_db_detail, **supplements_couscous_detail}
        }
        
        print(f"💰 CALCUL DU PRIX FINAL:")
        print(f"   - Prix menu de base: {menu.prix_ttc}€")
        print(f"   - Supplément desserts/boissons: {supplement_desserts_boissons}€")
        print(f"   - Supplément couscous: {supplement_couscous}€")
        print(f"   - Prix final: {prix_final}€")
        print(f"   - Suppléments sauvegardés: {supplements_complet}")

        # ==================== FONCTIONS UTILITAIRES ====================
        def detect_type_id(val):
            type_obj = None
            obj_id = None
            if isinstance(val, str):
                if val.startswith("plat_"):
                    type_obj = "plat"
                    obj_id = int(val.replace("plat_", ""))
                elif val.startswith("salade_"):
                    type_obj = "salade"
                    obj_id = int(val.replace("salade_", ""))
                elif val.startswith("couscous_"):
                    type_obj = "couscous"
                    obj_id = int(val.replace("couscous_", ""))
                elif val.isdigit():
                    type_obj = "plat"
                    obj_id = int(val)
            elif isinstance(val, int):
                type_obj = "plat"
                obj_id = val
            return type_obj, obj_id

        def article_correspond(article, choix_utiles, viandes_data):
            """Vérifie si un article correspond exactement à la configuration"""
            # Collecte des choix existants dans l'article
            choix_existants = {}
            for c in article.choix_menu.all():
                if c.plat_choisi:
                    choix_existants.setdefault(c.role, []).append(("plat", c.plat_choisi_id))
                elif c.salade:
                    choix_existants.setdefault(c.role, []).append(("salade", c.salade_id))
                elif c.couscous:
                    choix_existants.setdefault(c.role, []).append(("couscous", c.couscous_id))
                elif getattr(c, "info_text", None):
                    choix_existants.setdefault(c.role, []).append(("info", c.info_text))

            # Comparaison des choix
            for role, valeurs in choix_utiles.items():
                exist = choix_existants.get(role, [])
                attendues = []
                for typ, id in valeurs:
                    if typ and id:
                        attendues.append((typ, id))
                if sorted(exist) != sorted(attendues):
                    return False

            return True

        # ==================== RECHERCHE D'ARTICLE EXISTANT ====================
        choix_utiles = {}
        for role, vals in choix.items():
            if not isinstance(vals, list):
                vals = [vals]
            choix_utiles[role] = [detect_type_id(v) for v in vals]

        articles_existants = ArticlePanier.objects.filter(panier=panier, menu=menu)
        found = False
        article = None
        
        for art in articles_existants:
            if article_correspond(art, choix_utiles, viandes):
                # Article existant trouvé - incrémenter la quantité
                art.quantite += 1
                art.supplements_menu = supplements_complet
                
                # 🔥 CORRECTION : METTRE À JOUR L'ACCOMPAGNEMENT SI NÉCESSAIRE
                if 'accompagnement' in choix and choix['accompagnement']:
                    try:
                        accompagnement_id = choix['accompagnement'][0]
                        if isinstance(accompagnement_id, str) and accompagnement_id.isdigit():
                            accompagnement_id = int(accompagnement_id)
                            accompagnement = Accompagnement.objects.get(id=accompagnement_id)
                            art.accompagnement = accompagnement
                            print(f"✅ Accompagnement mis à jour: {accompagnement.nom}")
                    except (Accompagnement.DoesNotExist, ValueError, IndexError) as e:
                        print(f"❌ Erreur mise à jour accompagnement: {e}")
                
                art.calculate_total_price()
                logger.debug(f"[MENU PERSONNALISÉ] Article existant trouvé → incrémenté (ID {art.id})")
                print(f"✅ Article existant trouvé, incrémenté (ID {art.id})")
                found = True
                article = art
                break

        # ==================== CRÉATION D'UN NOUVEL ARTICLE ====================
        if not found:
            # 🔥 CORRECTION : MAPPING ENTRE Plat ID ET Accompagnement ID
            accompagnement_obj = None
            if 'accompagnement' in choix and choix['accompagnement']:
                try:
                    accompagnement_id = choix['accompagnement'][0]
                    if isinstance(accompagnement_id, str) and accompagnement_id.isdigit():
                        accompagnement_id = int(accompagnement_id)
                        
                        # 🔥 MAPPING CORRECT Plat ID -> Accompagnement ID
                        mapping_plat_vers_accompagnement = {
                            # ID Plat (vrai) -> ID Accompagnement (vrai)
                            129: 1,   # Frites Maison Croustillantes -> Frites Classiques (ID 1)
                            130: 6,   # Coleslaw Maison -> Coleslaw (ID 6)
                            131: 7,   # Onion Rings Maison (6 pcs) -> Onion Rings (ID 7)
                            132: 9,   # Mozzarella Sticks Maison (2 pcs) -> Mozzarella Sticks (2 pcs) (ID 9)
                            133: 8,   # Galette Rösti Maison (1 pcs) -> Galette Rösti (ID 8) ⭐ CELUI-CI
                            134: 4,   # Salade et Vinaigrette Maison -> Salade Verte (ID 4)
                            135: 2,   # Riz et Sauce Maison -> Riz Basmati (ID 2)
                            136: 3,   # Couscous et Sauce -> Couscous (ID 3)
                        }
                        
                        if accompagnement_id in mapping_plat_vers_accompagnement:
                            acc_id = mapping_plat_vers_accompagnement[accompagnement_id]
                            accompagnement_obj = Accompagnement.objects.get(id=acc_id)
                            print(f"✅ Accompagnement lié via mapping: {accompagnement_obj.nom} (+{accompagnement_obj.prix_supplement}€)")
                        else:
                            print(f"⚠️  Aucun mapping trouvé pour Plat ID {accompagnement_id}")
                            # 🔥 DEBUG : Afficher les informations du Plat
                            try:
                                plat_info = Plat.objects.get(id=accompagnement_id)
                                print(f"🔍 Plat trouvé: {plat_info.nom} (ID: {plat_info.id}, Prix: {plat_info.prix_unitaire_ttc}€)")
                            except Plat.DoesNotExist:
                                print(f"🔍 Plat ID {accompagnement_id} n'existe pas")
                                
                except (Accompagnement.DoesNotExist, ValueError, IndexError) as e:
                    print(f"❌ Erreur récupération accompagnement: {e}")

            # Créer l'article avec le prix initial ET l'accompagnement
            article = ArticlePanier.objects.create(
                panier=panier,
                menu=menu,
                quantite=1,
                supplements_menu=supplements_complet,
                prix_total=prix_final,
                accompagnement=accompagnement_obj  # 🔥 LIER L'ACCOMPAGNEMENT DIRECTEMENT
            )
            print(f"✅ Nouvel ArticlePanier créé : {article.quantite} x {article.menu.nom} (Total initial: {article.prix_total})")
            if accompagnement_obj:
                print(f"✅ Accompagnement lié à la création: {accompagnement_obj.nom} (+{accompagnement_obj.prix_supplement}€)")
            else:
                print(f"⚠️  Aucun accompagnement lié à l'article")

            # 🔥 CORRECTION CRITIQUE : FORCER LE RECALCUL POUR UTILISER calculate_base_price()
            article.calculate_total_price()
            print(f"💰 Prix après calculate_total_price(): {article.prix_total}€")

            # Enregistrement des choix (sauf accompagnement qui est déjà géré)
            for role, vals in choix.items():
                # 🔥 NE PAS CRÉER DE ChoixMenuArticle POUR L'ACCOMPAGNEMENT (déjà géré par le champ accompagnement)
                if role == 'accompagnement':
                    print(f"⏭️  Accompagnement ignoré dans ChoixMenuArticle (déjà lié directement)")
                    continue
                    
                if not isinstance(vals, list):
                    vals = [vals]
                for val in vals:
                    type_obj, obj_id = detect_type_id(val)
                    
                    if type_obj == "plat" and obj_id:
                        plat = Plat.objects.get(id=obj_id)
                        ChoixMenuArticle.objects.create(
                            article_panier=article,
                            role=role,
                            plat_choisi=plat
                        )
                        print(f"✅ ChoixMenuArticle plat ajouté : role={role}, plat={plat.nom}")
                    
                    elif type_obj == "salade" and obj_id:
                        from swigo.models import SaladePersonnalisee
                        salade = SaladePersonnalisee.objects.get(id=obj_id)
                        ChoixMenuArticle.objects.create(
                            article_panier=article,
                            role=role,
                            salade=salade
                        )
                        print(f"✅ ChoixMenuArticle salade ajouté : role={role}, salade={salade.nom}")
                    
                    elif type_obj == "couscous" and obj_id:
                        from swigo.models import CouscousPersonnalise
                        couscous = CouscousPersonnalise.objects.get(id=obj_id)
                        ChoixMenuArticle.objects.create(
                            article_panier=article,
                            role=role,
                            couscous=couscous
                        )
                        print(f"✅ ChoixMenuArticle couscous ajouté : role={role}, couscous_id={couscous.id}")
                    
                    else:
                        logger.warning(f"[MENU PERSONNALISÉ] Choix ignoré (role={role}, val={val}, type={type_obj}, id={obj_id})")
                        ChoixMenuArticle.objects.create(article_panier=article, role=role)
                        print(f"❌ ChoixMenuArticle ignoré : role={role}, val={val}, type={type_obj}, id={obj_id}")

            # Enregistrement des accompagnements couscous
            accompagnements_ids = viandes.get("accompagnements", [])
            if accompagnements_ids:
                from .models import AccompagnementCouscous
                for acc_id in accompagnements_ids:
                    try:
                        acc = AccompagnementCouscous.objects.get(id=acc_id)
                        ChoixMenuArticle.objects.create(
                            article_panier=article,
                            role="accompagnement_couscous",  # 🔥 CHANGER LE RÔLE POUR ÉVITER LA CONFUSION
                            info_text=acc.nom
                        )
                        print(f"✅ Ajouté accompagnement couscous : {acc.nom}")
                    except Exception as e:
                        logger.warning(f"AccompagnementCouscous introuvable (id={acc_id}): {e}")
                        print(f"❌ AccompagnementCouscous introuvable (id={acc_id}): {e}")

        # ==================== RECALCUL FINAL DU PANIER ====================
        # 🔥 FORCER LE RECALCUL DE L'ARTICLE
        article.calculate_total_price()
        
        # 🔥 RECALCULER LE PANIER COMPLET
        panier.calculate_total_price()
        panier.refresh_from_db()

        # ==================== APPLICATION PROMOTION ====================
        panier.apply_code_promo(request.session.get("code_promo"))

        # Récupérer les items du panier avec votre fonction existante
        cart_items = get_cart_items(panier)

        return JsonResponse({
            "success": True,
            "cart_items": cart_items,
            "totals": {
                'sous_total': f"{panier.sous_total:.2f}",
                'frais_livraison': f"{panier.frais_livraison_effectif:.2f}",
                'promotion': f"{panier.promotion:.2f}",
                'prix_total': f"{panier.prix_total:.2f}"
            },
            "supplement": f"{supplement_desserts_boissons + supplement_couscous:.2f}",
            "prix_final": f"{prix_final:.2f}"
        })

    except Exception as e:
        logger.exception("❌ Erreur dans ajouter_menu_personnalise")
        print("❌ Erreur dans ajouter_menu_personnalise :", e)
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# swigo/swigo_views.py

from django.http import JsonResponse
from .models import ChoixMenu

@csrf_exempt
@csrf_exempt
def api_choix_menu(request, menu_id):
    try:
        logger.info(f"🔍 API choix_menu appelée pour menu_id: {menu_id}")
        
        try:
            menu = Menu.objects.get(id=menu_id)
            logger.info(f"✅ Menu trouvé: {menu.nom}")
        except Menu.DoesNotExist:
            logger.error(f"❌ Menu introuvable: {menu_id}")
            return JsonResponse({'error': 'Menu introuvable', 'menu_id': menu_id}, status=404)

        choix_list = []
        utilise_couscous = False

        if not menu.choix.exists():
            logger.warning(f"⚠️ Menu {menu_id} n'a aucun choix configuré")
            return JsonResponse({
                'menu_id': menu_id,
                'menu_nom': menu.nom,
                'choix': [],
                'warning': 'Aucun choix configuré pour ce menu'
            })

        # 🆕 TOUS LES SUPPLÉMENTS CONFIGURÉS
        DESSERTS_AVEC_SUPPLEMENTS = [
            (111, 'Brownie Maison', Decimal('4.90'), Decimal('2.00'), True),
            (112, 'Cookie Maison', Decimal('2.90'), Decimal('0.00'), False),
            (113, 'Fondant Chocolat', Decimal('5.90'), Decimal('3.00'), True),
            (114, 'Tiramisu Café Classique', Decimal('5.20'), Decimal('2.30'), True),
            (115, 'Tiramisu Choco-Caramel', Decimal('5.50'), Decimal('2.60'), True),
            (116, 'Corne De Gazelle', Decimal('2.50'), Decimal('0.00'), False),
            (117, 'Chebakia Miel et Sésame', Decimal('2.50'), Decimal('0.00'), False),
            (118, 'Makrout Datte', Decimal('2.50'), Decimal('0.00'), False),
            (119, 'Briouate Amandes et Miel', Decimal('2.50'), Decimal('0.00'), False),
            (120, 'Assortiment marocain (4 pièces)', Decimal('8.90'), Decimal('6.00'), True),
        ]

        BOISSONS_AVEC_SUPPLEMENTS = [
            (99, 'Coca-Cola', Decimal('2.50'), Decimal('0.00'), False),
            (100, 'Coca-Cola Zero', Decimal('2.50'), Decimal('0.00'), False),
            (101, 'Fanta Orange', Decimal('2.50'), Decimal('0.00'), False),
            (102, 'Fanta Citron', Decimal('2.50'), Decimal('0.00'), False),
            (103, 'Ice Tea Pêche', Decimal('2.50'), Decimal('0.00'), False),
            (104, 'Oasis Tropical', Decimal('2.50'), Decimal('0.00'), False),
            (105, 'Sprite', Decimal('2.50'), Decimal('0.00'), False),
            (106, 'Schweppes Agrumes', Decimal('2.50'), Decimal('0.00'), False),
            (107, 'Hawai', Decimal('2.50'), Decimal('0.00'), False),
            (108, 'Red Bull', Decimal('3.50'), Decimal('1.00'), True),
            (109, 'Eau minérale', Decimal('2.00'), Decimal('0.00'), False),
            (110, 'Eau Pétillante', Decimal('2.00'), Decimal('0.00'), False),
            (121, 'Orangina', Decimal('2.50'), Decimal('0.00'), False),
        ]

        # 🆕 ACCOMPAGNEMENTS AVEC SUPPLÉMENTS (identique à accompagnements_burger_ajax)
        ACCOMPAGNEMENTS_AVEC_SUPPLEMENTS = [
            (1001, 'Frites', Decimal('0.00')),
            (1002, 'Riz', Decimal('0.00')),
            (1003, 'Couscous', Decimal('1.00')),
            (1004, 'Salade', Decimal('0.00')),
            (1005, 'Kemia', Decimal('0.00')),
            (1006, 'Coleslaw', Decimal('0.00')),
            (1007, 'Onion Rings', Decimal('1.00')),
            (1008, 'Galette Rösti', Decimal('0.70')),
            (1009, 'Mozzarella Sticks (2 pcs)', Decimal('0.90')),
        ]

        for choix in menu.choix.all():
            logger.info(f"📋 Traitement choix: {choix.role}")
            
            if choix.autorise_couscous_personnalise:
                utilise_couscous = True
                logger.info("🍛 Menu couscous détecté")

            # 🆕 CONSTRUCTION DES DONNÉES AVEC TOUS LES PRIX
            plats_data = []
            for p in choix.plats_possibles.all():
                prix_supplement = Decimal('0.00')
                
                # Chercher dans les desserts
                for dessert_info in DESSERTS_AVEC_SUPPLEMENTS:
                    if dessert_info[0] == p.id:
                        prix_supplement = dessert_info[3] if dessert_info[4] else Decimal('0.00')
                        break
                
                # Chercher dans les boissons si pas trouvé
                if prix_supplement == 0:
                    for boisson_info in BOISSONS_AVEC_SUPPLEMENTS:
                        if boisson_info[0] == p.id:
                            prix_supplement = boisson_info[3] if boisson_info[4] else Decimal('0.00')
                            break
                
                # 🆕 CHERCHER DANS LES ACCOMPAGNEMENTS
                if prix_supplement == 0:
                    for acc_info in ACCOMPAGNEMENTS_AVEC_SUPPLEMENTS:
                        if acc_info[0] == p.id:
                            prix_supplement = acc_info[2]
                            break
                
                # Si non trouvé, vérifier par nom (fallback)
                if prix_supplement == 0:
                    nom_lower = p.nom.lower()
                    if any(mot in nom_lower for mot in ['brownie', 'fondant', 'tiramisu', 'assortiment']):
                        prix_supplement = Decimal('2.00')
                    elif 'red bull' in nom_lower:
                        prix_supplement = Decimal('1.00')
                    # 🆕 FALLBACK POUR ACCOMPAGNEMENTS PAR NOM
                    elif any(mot in nom_lower for mot in ['couscous', 'onion rings', 'onion']):
                        prix_supplement = Decimal('1.00')
                    elif 'rösti' in nom_lower or 'rosti' in nom_lower:
                        prix_supplement = Decimal('0.70')
                    elif 'mozzarella' in nom_lower:
                        prix_supplement = Decimal('0.90')
                
                plat_data = {
                    "id": p.id, 
                    "nom": p.nom,
                    "prix_unitaire_ttc": str(p.prix_unitaire_ttc) if p.prix_unitaire_ttc else "0.00",
                    "prix_supplement": str(prix_supplement),
                    "description_courte": getattr(p, 'description_courte', '') or "",
                    "photo_url": p.photo.url if hasattr(p, 'photo') and p.photo else None
                }
                plats_data.append(plat_data)
                logger.info(f"💰 Plat {p.nom}: supplément = {prix_supplement}€")

            choix_data = {
                "id": choix.id,
                "role": choix.role,
                "nombre_elements_inclus": choix.nombre_elements_inclus,
                "autorise_salade_personnalisee": choix.autorise_salade_personnalisee,
                "autorise_couscous_personnalise": choix.autorise_couscous_personnalise,
                "plats": plats_data
            }

            if choix.autorise_couscous_personnalise:
                choix_data["nombre_viandes_incluses"] = getattr(choix, 'nombre_viandes_incluses', 1)
                
                viandes_data = []
                viandes_possibles = getattr(choix, 'viandes_possibles', None)
                
                if viandes_possibles:
                    for v in viandes_possibles.all():
                        viande_data = {
                            "id": v.id, 
                            "nom": v.nom,
                            "prix_supplement": str(getattr(v, 'supplement_inclus', 0)) if getattr(v, 'supplement_inclus', None) else "0.00"
                        }
                        viandes_data.append(viande_data)
                        logger.info(f"💰 Viande {v.nom}: supplément = {viande_data['prix_supplement']}€")
                
                choix_data["viandes_possibles"] = viandes_data

            choix_list.append(choix_data)

        response_data = {
            "menu_id": menu_id,
            "menu_nom": menu.nom,
            "choix": choix_list,
            # 🆕 AJOUTER LA LISTE DES ACCOMPAGNEMENTS POUR RÉFÉRENCE
            "accompagnements_config": ACCOMPAGNEMENTS_AVEC_SUPPLEMENTS
        }

        if utilise_couscous:
            try:
                accompagnements = list(AccompagnementCouscous.objects.all().values("id", "nom"))
                # 🆕 AJOUTER LES PRIX AUX ACCOMPAGNEMENTS COUSCOUS
                accompagnements_avec_prix = []
                for acc in accompagnements:
                    prix_acc = Decimal('0.00')
                    for acc_info in ACCOMPAGNEMENTS_AVEC_SUPPLEMENTS:
                        if acc_info[0] == acc['id']:
                            prix_acc = acc_info[2]
                            break
                    accompagnements_avec_prix.append({
                        'id': acc['id'],
                        'nom': acc['nom'],
                        'prix_supplement': str(prix_acc)
                    })
                
                response_data["accompagnements_couscous"] = accompagnements_avec_prix
                logger.info(f"🍟 {len(accompagnements_avec_prix)} accompagnements chargés avec prix")
            except Exception as e:
                logger.error(f"❌ Erreur chargement accompagnements: {e}")
                response_data["accompagnements_couscous"] = []

        response_data["menu_type"] = detecter_type_menu(menu.nom)
        
        logger.info(f"✅ API choix_menu réussie pour {menu.nom}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.exception(f"❌ Erreur critique dans api_choix_menu: {e}")
        return JsonResponse({
            "error": "Erreur interne du serveur",
            "details": str(e),
            "menu_id": menu_id
        }, status=500)

def calculer_prix_supplement_plat(plat_id, plat_nom):
    """
    Calcule le prix supplémentaire réel d'un plat basé sur votre logique
    """
    # 🎯 UTILISER LA MÊME LOGIQUE QUE DANS ajouter_menu_personnalise
    DESSERTS_AVEC_SUPPLEMENTS = [
        (111, 'Brownie Maison', Decimal('4.90'), Decimal('2.00'), True),
        (112, 'Cookie Maison', Decimal('2.90'), Decimal('0.00'), False),
        (113, 'Fondant Chocolat', Decimal('5.90'), Decimal('3.00'), True),
        (114, 'Tiramisu Café Classique', Decimal('5.20'), Decimal('2.30'), True),
        (115, 'Tiramisu Choco-Caramel', Decimal('5.50'), Decimal('2.60'), True),
        (116, 'Corne De Gazelle', Decimal('2.50'), Decimal('0.00'), False),
        (117, 'Chebakia Miel et Sésame', Decimal('2.50'), Decimal('0.00'), False),
        (118, 'Makrout Datte', Decimal('2.50'), Decimal('0.00'), False),
        (119, 'Briouate Amandes et Miel', Decimal('2.50'), Decimal('0.00'), False),
        (120, 'Assortiment marocain (4 pièces)', Decimal('8.90'), Decimal('6.00'), True),
    ]

    BOISSONS_AVEC_SUPPLEMENTS = [
        (99, 'Coca-Cola', Decimal('2.50'), Decimal('0.00'), False),
        (100, 'Coca-Cola Zero', Decimal('2.50'), Decimal('0.00'), False),
        (101, 'Fanta Orange', Decimal('2.50'), Decimal('0.00'), False),
        (102, 'Fanta Citron', Decimal('2.50'), Decimal('0.00'), False),
        (103, 'Ice Tea Pêche', Decimal('2.50'), Decimal('0.00'), False),
        (104, 'Oasis Tropical', Decimal('2.50'), Decimal('0.00'), False),
        (105, 'Sprite', Decimal('2.50'), Decimal('0.00'), False),
        (106, 'Schweppes Agrumes', Decimal('2.50'), Decimal('0.00'), False),
        (107, 'Hawai', Decimal('2.50'), Decimal('0.00'), False),
        (108, 'Red Bull', Decimal('3.50'), Decimal('1.00'), True),
        (109, 'Eau minérale', Decimal('2.00'), Decimal('0.00'), False),
        (110, 'Eau Pétillante', Decimal('2.00'), Decimal('0.00'), False),
        (121, 'Orangina', Decimal('2.50'), Decimal('0.00'), False),
    ]

    # Chercher dans les desserts
    for dessert_info in DESSERTS_AVEC_SUPPLEMENTS:
        if dessert_info[0] == plat_id:
            return dessert_info[3] if dessert_info[4] else Decimal('0.00')
    
    # Chercher dans les boissons
    for boisson_info in BOISSONS_AVEC_SUPPLEMENTS:
        if boisson_info[0] == plat_id:
            return boisson_info[3] if boisson_info[4] else Decimal('0.00')
    
    # Si non trouvé, vérifier par nom (fallback)
    nom_lower = plat_nom.lower()
    if any(mot in nom_lower for mot in ['brownie', 'fondant', 'tiramisu', 'assortiment']):
        # Ces desserts ont généralement un supplément
        return Decimal('2.00')
    elif 'red bull' in nom_lower:
        return Decimal('1.00')
    
    # Par défaut, pas de supplément
    return Decimal('0.00')

def detecter_type_menu(nom_menu):
    """Détermine le type de menu pour l'interface frontend"""
    nom_lower = nom_menu.lower()
    
    if "burger" in nom_lower:
        return "burger"
    elif "couscous" in nom_lower:
        return "couscous" 
    elif "tenders" in nom_lower:
        return "tenders_simple"
    elif "poulet frit" in nom_lower:
        return "poulet_choix"
    elif "josper" in nom_lower:
        return "poulet_josper"
    else:
        return "standard"






@csrf_exempt
@require_POST
def ajouter_couscous_personnalise_ajax(request):
    form = CouscousPersonnaliseForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    # ✅ Données nettoyées et sécurisées
    formule = form.cleaned_data["formule"]
    viandes_inclues = form.cleaned_data["viandes_inclues"]
    viandes_supplement = form.cleaned_data["viandes_supplement"]
    option_xl = form.cleaned_data.get("option_xl", False)

    # ✅ Création du couscous personnalisé
    couscous = formule.creer_instance_personnalisee(option_xl=option_xl)  # méthode à créer ou adapter si besoin

    # ✅ Sauvegarde des viandes incluses
    for viande in viandes_inclues:
        ChoixViandeCouscous.objects.create(
            couscous=couscous,
            viande=viande,
            est_incluse=True
        )
        viande.quantite_stock -= 1
        viande.save(update_fields=['quantite_stock'])

    # ✅ Sauvegarde des viandes en supplément
    for viande in viandes_supplement:
        ChoixViandeCouscous.objects.create(
            couscous=couscous,
            viande=viande,
            est_incluse=False
        )
        viande.quantite_stock -= 1
        viande.save(update_fields=['quantite_stock'])

    # ✅ Calcul du prix
    couscous.calculate_prix_total()
    couscous.save(update_fields=['prix_total'])

    return JsonResponse({
        "success": True,
        "couscous_id": couscous.id,
        "prix_total": float(couscous.prix_total)
    })



def historique_commandes_client(request, client_id):
    commandes = Commande.objects.filter(client_id=client_id).exclude(is_paid=False).order_by('-heure_creation')[:10]
    data = {
        "commandes": [
            {
                "id": c.id,
                "date": c.heure_creation.strftime("%d/%m/%Y %H:%M"),
                "montant": float(c.calculate_prix_total()),
                "details": ", ".join([a.plat.nom for a in c.panier.articlepanier_set.all() if a.plat]),
                "moyen_paiement": c.get_moyen_paiement_display() or "—"
            }
            for c in commandes
        ]
    }
    return JsonResponse(data)


from django.http import JsonResponse

# === Production ===

def ingredients_base(request):
    """
    Liste ou gestion des ingrédients de base (matières premières).
    """
    return JsonResponse({"endpoint": "ingredients_base", "status": "ok"})


def produits_transformes(request):
    """
    Liste ou gestion des produits transformés (ex : buns, sauces, etc.).
    """
    return JsonResponse({"endpoint": "produits_transformes", "status": "ok"})


def recettes(request):
    """
    Liste ou gestion des recettes et fiches techniques.
    """
    return JsonResponse({"endpoint": "recettes", "status": "ok"})


def ordres_production(request):
    """
    Création et suivi des ordres de production.
    """
    return JsonResponse({"endpoint": "ordres_production", "status": "ok"})


def suivi_production(request):
    """
    Suivi global du stock (base + transformés).
    """
    return JsonResponse({"endpoint": "suivi_production", "status": "ok"})


from .models import ProduitTransforme

def assets_produits_transformes(request):
    produits = ProduitTransforme.objects.select_related("recette").all()

    return render(request, "assets/produits_transformes.html", {
        "produits_boulangerie": produits.filter(categorie="boulangerie"),
        "produits_sauces": produits.filter(categorie="sauces"),
        "produits_viandes": produits.filter(categorie="viandes"),
        "produits_legumes": produits.filter(categorie="legumes"),
        "produits_desserts": produits.filter(categorie="desserts"),
    })


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ProduitTransforme, Plat, Cuisson

@csrf_exempt
def produit_out_of_stock(request, produit_id):
    """
    Met un produit transformé en rupture et désactive les plats liés.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        produit = ProduitTransforme.objects.get(id=produit_id)
    except ProduitTransforme.DoesNotExist:
        return JsonResponse({"error": "Produit introuvable"}, status=404)

    # 1. Stock à 0
    produit.quantite_disponible = 0
    produit.save(update_fields=["quantite_disponible"])

    # 2. Plats concernés
    plats_affectes = Plat.objects.filter(cuissons__produit_transforme=produit).distinct()
    nb_plats = plats_affectes.update(disponible=False)

    return JsonResponse({
        "message": f"{produit.nom} mis en rupture de stock.",
        "plats_desactives": nb_plats
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Recette, ProduitTransforme, Ingredient

# === 1. Fiche technique ===
def fiche_technique(request, produit_id):
    produit = get_object_or_404(ProduitTransforme, id=produit_id)
    recette = getattr(produit, "recette", None)
    return render(request, "assets/fiche_technique.html", {
        "produit": produit,
        "recette": recette,
    })



# === 2. Recette (étapes) ===
def recette_detail(request, produit_id):
    produit = get_object_or_404(ProduitTransforme, id=produit_id)
    recette = getattr(produit, "recette", None)
    return render(request, "assets/recette_detail.html", {
        "produit": produit,
        "recette": recette,
    })


# === 3. Ordre de fabrication ===
def ordre_fabrication(request, produit_id):
    produit = get_object_or_404(ProduitTransforme, id=produit_id)
    recette = getattr(produit, "recette", None)
    ingredients_requis = []
    stock_ok = True

    if request.method == "POST" and recette:
        quantite = int(request.POST.get("quantite", 0))
        if quantite > 0:
            try:
                ingredients_requis = recette.ingredients_totaux(quantite)
                # Vérif stock
                for item in ingredients_requis:
                    ingr = item["ingredient"]
                    if ingr.quantite_stock < item["quantite"]:
                        stock_ok = False
                        messages.error(request, f"Stock insuffisant pour {ingr.nom}")
                if stock_ok:
                    # Déduction + ajout au stock produit transformé
                    recette.deduire_du_stock(quantite)
                    messages.success(request, f"✅ {quantite} {produit.nom} fabriqués avec succès !")
                    return redirect("swigo:ordre_fabrication", produit_id=produit.id)
            except Exception as e:
                messages.error(request, f"Erreur : {e}")

    return render(request, "assets/ordre_fabrication.html", {
        "produit": produit,
        "recette": recette,
        "ingredients_requis": ingredients_requis,
        "stock_ok": stock_ok,
    })


from django.http import JsonResponse
from .models import Plat, Categorie

def burgers_par_type_ajax(request, burger_type):
    """Retourne les burgers filtrés par type"""
    try:
        # Trouver la catégorie "burger"
        categorie_burger = Categorie.objects.get(nom__iexact='burger')
        
        # Filtrer les burgers par type
        burgers = Plat.objects.filter(
            categorie=categorie_burger,
            type_burger=burger_type,
            disponible=True
        ).select_related('categorie')
        
        burgers_data = []
        for burger in burgers:
            burgers_data.append({
                'id': burger.id,
                'nom': burger.nom,
                'description_courte': burger.description_courte,
                'description_longue': burger.description_longue,
                'prix_unitaire_ttc': str(burger.prix_unitaire_ttc),
                'photo_url': burger.photo.url if burger.photo else '',
                'type_burger': burger.type_burger,
            })
        
        return JsonResponse({
            'success': True,
            'burgers': burgers_data,
            'count': len(burgers_data)
        })
        
    except Categorie.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Catégorie burger non trouvée'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
    


from django.http import JsonResponse
from .models import CroustyOption, Plat

def get_crousty_options_ajax(request, plat_id):
    """Retourne les options Crousty groupées par catégorie pour un plat donné"""
    try:
        plat = Plat.objects.get(id=plat_id)
        
        if plat.type_plat != 'crousty':
            return JsonResponse({
                'success': False,
                'message': 'Ce plat n\'est pas un Crousty'
            })
        
        options = CroustyOption.objects.filter(disponible=True)
        options_par_categorie = {}
        
        for option in options:
            if option.categorie not in options_par_categorie:
                options_par_categorie[option.categorie] = []
            
            options_par_categorie[option.categorie].append({
                'id': option.id,
                'nom': option.nom,
                'prix_supplement': float(option.prix_supplement),
                'categorie': option.get_categorie_display()
            })
        
        return JsonResponse({
            'success': True,
            'plat_id': plat_id,
            'plat_nom': plat.nom,
            'options_par_categorie': options_par_categorie
        })
        
    except Plat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Plat non trouvé'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        })


from django.http import JsonResponse
from .models import Plat, CroustyOption
import json

@csrf_exempt
def ajouter_crousty_personnalise(request):
    if request.method == 'POST':
        if not request.session.session_key:
            request.session.create()

        data = json.loads(request.body)
        plat_id = data.get('plat_id')
        options_crousty_ids = data.get('options_crousty', [])
        prix_supplement = data.get('prix_supplement', 0)

        try:
            plat = Plat.objects.get(id=plat_id, type_plat='crousty')
            
            # Récupérer les options Crousty sélectionnées
            options_crousty = CroustyOption.objects.filter(id__in=options_crousty_ids)
            
            # Gérer la commande et le panier
            commande_id = request.session.get('commande_id')
            if not commande_id:
                commande = Commande.objects.create(client=None, is_paid=False)
                request.session['commande_id'] = commande.id
                panier = Panier.objects.create(commande=commande)
            else:
                commande = Commande.objects.get(id=commande_id)
                panier = commande.panier or Panier.objects.create(commande=commande)

            # Créer un nom personnalisé pour le Crousty
            nom_personnalise = f"{plat.nom} (Personnalisé)"
            
            # Vérifier si un article similaire existe déjà
            article_existant = None
            for article in ArticlePanier.objects.filter(panier=panier, plat=plat):
                # Vérifier si les options Crousty correspondent
                options_article_ids = list(article.options_crousty.values_list('id', flat=True))
                if set(options_article_ids) == set(options_crousty_ids):
                    article_existant = article
                    break

            if article_existant:
                # Incrémenter la quantité si l'article existe déjà
                article_existant.quantite += 1
                article_existant.calculate_total_price()  # Recalculer le prix
                article_existant.save()
                article = article_existant
            else:
                # Créer un nouvel article
                article = ArticlePanier.objects.create(
                    panier=panier, 
                    plat=plat, 
                    quantite=1,
                    nom_personnalise=nom_personnalise
                )
                
                # Associer les options Crousty
                article.options_crousty.set(options_crousty)
                
                # Calculer automatiquement le prix avec la méthode
                article.calculate_total_price()

            # Appliquer le code promo si présent
            code_promo_code = request.session.get('code_promo')
            code_promo = panier.apply_code_promo(code_promo_code)

            # Retourner les données mises à jour
            return JsonResponse({
                'success': True,
                'message': 'Crousty ajouté au panier',
                'cart_items': get_cart_items(panier),
                'totals': {
                    'sous_total': f"{panier.sous_total:.2f}",
                    'frais_livraison': f"{panier.frais_livraison_effectif:.2f}",
                    'promotion': f"{panier.promotion:.2f}",
                    'prix_total': f"{panier.prix_total:.2f}"
                },
                'code_promo': {
                    'code': code_promo.code,
                    'reduction_type': code_promo.reduction_type,
                    'reduction_amount': f"{code_promo.reduction_amount}"
                } if code_promo else None
            })

        except Plat.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Plat Crousty non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)



def get_poulet_options_ajax(request, plat_id):
    """Retourne les options Poulet groupées par catégorie pour un plat donné"""
    try:
        plat = Plat.objects.get(id=plat_id)
        
        options = PouletOption.objects.filter(disponible=True)
        options_par_categorie = {}
        
        # Récupérer les limites spécifiques au plat
        limites_plat = LimiteOptionsPoulet.objects.filter(plat=plat)
        limites_dict = {
            limite.categorie: {
                'limite': limite.limite_selection,
                'obligatoire': limite.est_obligatoire
            } for limite in limites_plat
        }
        
        # Configuration par défaut si non spécifiée
        limites_par_defaut = {
            'assaisonnement': {'limite': 1, 'obligatoire': True},
            'accompagnement': {'limite': 1, 'obligatoire': False},
            'sauce': {'limite': 1, 'obligatoire': True},
            'supplement': {'limite': 99, 'obligatoire': False}
        }
        
        for option in options:
            if option.categorie not in options_par_categorie:
                # Utiliser la limite du plat ou la limite par défaut
                limite_data = limites_dict.get(option.categorie, limites_par_defaut.get(option.categorie, {'limite': 1, 'obligatoire': True}))
                
                options_par_categorie[option.categorie] = {
                    'options': [],
                    'limite': limite_data['limite'],
                    'obligatoire': limite_data['obligatoire'],
                    'categorie_display': option.get_categorie_display()
                }
            
            options_par_categorie[option.categorie]['options'].append({
                'id': option.id,
                'nom': option.nom,
                'prix_supplement': float(option.prix_supplement),
                'categorie': option.categorie
            })
        
        return JsonResponse({
            'success': True,
            'plat_id': plat_id,
            'plat_nom': plat.nom,
            'options_par_categorie': options_par_categorie
        })
        
    except Plat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Plat non trouvé'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        })

# Dans votre vue ajouter_poulet_personnalise
@csrf_exempt
def ajouter_poulet_personnalise(request):
    if request.method == 'POST':
        print("=" * 60)
        print("🍗 DEBUG AJOUT POULET PERSONNALISÉ - BYPASS TEMPORAIRE")
        print("=" * 60)
        
        if not request.session.session_key:
            request.session.create()

        data = json.loads(request.body)
        plat_id = data.get('plat_id')
        options_poulet_ids = data.get('options_poulet', [])
        prix_supplement = data.get('prix_supplement', 0)

        print(f"📥 DONNÉES BRUTES: {data}")

        try:
            plat = Plat.objects.get(id=plat_id)
            print(f"✅ PLAT: {plat.nom} (Type actuel: {plat.type_plat})")
            
            # Convertir les IDs
            options_poulet_ids = [int(opt_id) for opt_id in options_poulet_ids]
            print(f"🔄 OPTIONS: {options_poulet_ids}")
            
            # 🆕 COMPTER LES OCCURRENCES
            from collections import Counter
            options_counter = Counter(options_poulet_ids)
            print(f"🔢 OPTIONS AVEC QUANTITÉS: {dict(options_counter)}")
            
            # Récupérer les options uniques pour ManyToMany
            options_poulet_ids_uniques = list(set(options_poulet_ids))
            options_poulet = PouletOption.objects.filter(id__in=options_poulet_ids_uniques)
            print(f"✅ OPTIONS TROUVÉES: {options_poulet.count()}")
            
            # Gérer panier
            commande_id = request.session.get('commande_id')
            if not commande_id:
                commande = Commande.objects.create(client=None, is_paid=False)
                request.session['commande_id'] = commande.id
                panier = Panier.objects.create(commande=commande)
            else:
                commande = Commande.objects.get(id=commande_id)
                panier = commande.panier or Panier.objects.create(commande=commande)

            # 🆕 CRÉATION AVEC STOCKAGE DES QUANTITÉS
            article = ArticlePanier.objects.create(
                panier=panier, 
                plat=plat, 
                quantite=1,
                nom_personnalise=f"{plat.nom} (Personnalisé)",
                # 🆕 STOCKER LES OPTIONS AVEC QUANTITÉS
                options_poulet_avec_quantites=options_poulet_ids  # Stocke [5, 10, 10, 16, 16]
            )
            print(f"✅ ARTICLE CRÉÉ: #{article.id}")

            # 🆕 ASSOCIATION DES OPTIONS UNIQUES (pour la relation ManyToMany)
            if options_poulet.exists():
                print(f"🔗 ASSOCIATION OPTIONS...")
                
                for option in options_poulet:
                    article.options_poulet.add(option)
                    print(f"   - ✅ {option.id}: {option.nom}")
                
                # 🆕 AFFICHER LES QUANTITÉS RÉELLES
                for option_id, quantite in options_counter.items():
                    option = PouletOption.objects.get(id=option_id)
                    print(f"   - 📦 {option_id}: {option.nom} x{quantite}")
                
                count_final = article.options_poulet.count()
                print(f"✅ OPTIONS ASSOCIÉES: {count_final} (uniques)")
                print(f"📦 QUANTITÉS RÉELLES: {dict(options_counter)}")
            else:
                print("⚠️ AUCUNE OPTION À ASSOCIER")

            # Calcul prix (🆕 UTILISE MAINTENANT LES QUANTITÉS)
            article.calculate_total_price()
            print(f"💰 PRIX: {article.prix_total}")

            # Mettre à jour panier
            panier.calculate_totals()

            # Récupérer les articles
            cart_items = get_cart_items(panier)
            
            print("=" * 60)
            print("✅ RÉPONSE ENVOYÉE")
            print("=" * 60)

            return JsonResponse({
                'success': True,
                'message': 'Poulet personnalisé ajouté au panier',
                'cart_items': cart_items,
                'totals': {
                    'sous_total': f"{panier.sous_total:.2f}",
                    'frais_livraison': f"{panier.frais_livraison_effectif:.2f}",
                    'promotion': f"{panier.promotion:.2f}",
                    'prix_total': f"{panier.prix_total:.2f}"
                },
                'code_promo': None
            })

        except Exception as e:
            print(f"❌ ERREUR: {str(e)}")
            import traceback
            print(f"🔍 STACK TRACE: {traceback.format_exc()}")
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    # Dans views.py
def accompagnements_burger_ajax(request):
    """Retourne la liste des accompagnements disponibles pour les burgers"""
    accompagnements = [
        {'id': 1001, 'nom': 'Frites', 'prix': 0.00},
        {'id': 1002, 'nom': 'Riz', 'prix': 0.00},
        {'id': 1003, 'nom': 'Couscous', 'prix': 1.00},
        {'id': 1004, 'nom': 'Salade', 'prix': 0.00},
        {'id': 1005, 'nom': 'Kemia', 'prix': 0.00},
        {'id': 1006, 'nom': 'Coleslaw', 'prix': 0.00},
        {'id': 1007, 'nom': 'Onion Rings', 'prix': 1.00},
        {'id': 1008, 'nom': 'Galette Rösti', 'prix': 0.70},
        {'id': 1009, 'nom': 'Mozzarella Sticks (2 pcs)', 'prix': 0.90},
    ]
    
    return JsonResponse({
        'success': True,
        'accompagnements': accompagnements
    })


def get_plats_par_categorie(request):
    """Version optimisée utilisant principalement le champ type_plat"""
    try:
        categories_plats = {}
        
        # Mapping direct type_plat → catégorie d'affichage
        TYPE_TO_CATEGORY = {
            'burger': 'burgers',
            'poulet': 'poulet', 
            'crousty': 'crousty',
            'couscous': 'couscous_base'
        }
        
        # Plats par type_plat
        for type_plat, categorie_key in TYPE_TO_CATEGORY.items():
            plats = Plat.objects.filter(
                type_plat=type_plat,
                disponible=True
            )
            categories_plats[categorie_key] = [
                {
                    "id": p.id, 
                    "nom": p.nom, 
                    "prix_ttc": str(p.prix_unitaire_ttc),
                    "type_plat": p.type_plat,
                    "type_burger": p.type_burger if type_plat == 'burger' else None,
                    "options": p.get_poulet_options_par_categorie() if type_plat == 'poulet' else 
                              p.get_crousty_options_par_categorie() if type_plat == 'crousty' else {}
                } 
                for p in plats
            ]
        
        # Catégories spéciales (non couvertes par type_plat)
        
        # Accompagnements
        accompagnements = Plat.objects.filter(
            categorie__nom__icontains='accompagnement'
        ).filter(disponible=True)
        categories_plats['accompagnements'] = [
            {
                "id": p.id, 
                "nom": p.nom, 
                "prix_ttc": str(p.prix_unitaire_ttc),
                "type_plat": p.type_plat
            } 
            for p in accompagnements
        ]
        
        # Boissons
        boissons = Plat.objects.filter(
            categorie__nom__icontains='boisson'
        ).filter(disponible=True)
        categories_plats['boissons'] = [
            {
                "id": p.id, 
                "nom": p.nom, 
                "prix_ttc": str(p.prix_unitaire_ttc),
                "type_plat": p.type_plat
            } 
            for p in boissons
        ]
        
        # Desserts
        desserts = Plat.objects.filter(
            categorie__nom__icontains='dessert'
        ).filter(disponible=True)
        categories_plats['desserts'] = [
            {
                "id": p.id, 
                "nom": p.nom, 
                "prix_ttc": str(p.prix_unitaire_ttc),
                "type_plat": p.type_plat
            } 
            for p in desserts
        ]

        response_data = {
            "plats_par_categorie": categories_plats,
            "viandes_couscous": list(ViandeCouscous.objects.all().values("id", "nom")),
            "accompagnements_couscous": list(AccompagnementCouscous.objects.all().values("id", "nom")),
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.exception("Erreur dans get_plats_par_categorie")
        return JsonResponse({"error": str(e)}, status=500)
    


def get_plat_detail(request, plat_id):
    """API pour récupérer le détail d'un plat avec ses options"""
    try:
        plat = Plat.objects.get(id=plat_id, disponible=True)
        
        data = {
            "id": plat.id,
            "nom": plat.nom,
            "description_courte": plat.description_courte,
            "description_longue": plat.description_longue,
            "prix_ttc": str(plat.prix_unitaire_ttc),
            "type_plat": plat.type_plat,
            "type_burger": plat.type_burger,
            "photo_url": plat.photo.url if plat.photo else None,
        }
        
        # Ajouter les options selon le type de plat
        if plat.type_plat == 'crousty':
            data["options_crousty"] = plat.get_crousty_options_par_categorie()
        elif plat.type_plat == 'poulet':
            data["options_poulet"] = plat.get_poulet_options_par_categorie()
        elif plat.type_plat == 'burger':
            data["options_burger"] = []  # Vous pourriez ajouter des options burgers
        
        return JsonResponse(data)
        
    except Plat.DoesNotExist:
        return JsonResponse({"error": "Plat introuvable"}, status=404)
    except Exception as e:
        logger.exception("Erreur dans get_plat_detail")
        return JsonResponse({"error": str(e)}, status=500)
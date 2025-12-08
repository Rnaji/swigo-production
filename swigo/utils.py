# utils.py
from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, time

from django.apps import apps
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone

logger = logging.getLogger(__name__)

# =========================
# Constantes de configuration
# =========================
MAX_LIVRAISONS_PAR_CRENEAU = 2
MAX_EMPORTES_PAR_CRENEAU = 1
HEURE_DEBUT_SOIR = time(18, 0)
TEMPS_PREPARATION_MINUTES = 30  # MODIFICATION : 20 minutes → 30 minutes

# =========================
# Outils généraux
# =========================
def now():
    """Datetime local timezone-aware."""
    return timezone.localtime()

def arrondir_au_quart_heure(dt: datetime) -> datetime:
    """Arrondit au quart d'heure supérieur."""
    minute = dt.minute
    mod = minute % 15
    minutes_to_add = 0 if mod == 0 else (15 - mod)
    dt_arrondi = dt + timedelta(minutes=minutes_to_add)
    return dt_arrondi.replace(second=0, microsecond=0)

# =========================
# Créneaux & disponibilité
# =========================
def creneau_est_disponible(date, heure, mode: str = "livraison") -> bool:
    """
    Vérifie si un créneau de 15 minutes [date, heure] est disponible
    pour le 'mode' demandé: 'livraison' ou 'emporter' (alias: 'retrait').
    """
    Commande = apps.get_model('swigo', 'Commande')

    mode = (mode or "").lower().strip()
    if mode == "retrait":
        mode = "emporter"

    tz = get_current_timezone()
    dt_debut = make_aware(datetime.combine(date, heure), timezone=tz)
    dt_fin = dt_debut + timedelta(minutes=15)

    logger.debug(f"[CRÉNEAU] Vérif dispo {mode.upper()} — Début: {dt_debut}, Fin: {dt_fin}")

    filtre_commande_valide = (
        Q(is_delivered=False) &
        ~Q(moyen_paiement__isnull=True) &
        ~Q(moyen_paiement='')
    )

    if mode == 'livraison':
        commandes = (Commande.objects
                     .filter(
                         is_commande_a_emporter=False,
                         date_livraison_specifiee=date,
                         heure_livraison_specifiee__gte=dt_debut.time(),
                         heure_livraison_specifiee__lt=dt_fin.time()
                     )
                     .filter(filtre_commande_valide))
        logger.debug(f"[LIVRAISON] Commandes valides sur créneau: {commandes.count()}")
        return commandes.count() < MAX_LIVRAISONS_PAR_CRENEAU

    elif mode == 'emporter':
        commandes = (Commande.objects
                     .filter(
                         is_commande_a_emporter=True,
                         heure_pick_up_specifie__gte=dt_debut,
                         heure_pick_up_specifie__lt=dt_fin
                     )
                     .filter(filtre_commande_valide))
        logger.debug(f"[EMPORTER] Commandes valides sur créneau: {commandes.count()}")
        return commandes.count() < MAX_EMPORTES_PAR_CRENEAU

    logger.warning(f"[CRÉNEAU] Mode inconnu: {mode}")
    return False


def chercher_prochain_creneau_disponible(dt_initial: datetime, mode: str = "livraison") -> datetime:
    """
    Cherche le prochain créneau de 15 minutes disponible à partir de dt_initial.
    Limite: 30 essais (7h30).
    """
    dt = arrondir_au_quart_heure(dt_initial)
    essais = 0
    while essais < 30:
        date = dt.date()
        heure = dt.time()
        if creneau_est_disponible(date, heure, mode=mode):
            logger.info(f"[DISPO] Créneau trouvé : {date} à {heure} ({mode})")
            return dt
        logger.debug(f"[NEXT] {date} {heure} indisponible ({mode}), on avance +15min…")
        dt += timedelta(minutes=15)
        essais += 1

    logger.warning("[ECHEC] Aucun créneau disponible dans la fenêtre de recherche")
    return dt_initial

# =========================
# Horaires
# =========================
def get_heure_debut_service(jour_semaine: str, service: str, fallback: time) -> time:
    """
    Récupère la première heure de début pour un jour/service via HoraireDisponible.
    """
    HoraireDisponible = apps.get_model('swigo', 'HoraireDisponible')
    dispo = HoraireDisponible.objects.filter(jour=jour_semaine, service=service).first()
    if dispo and hasattr(dispo, "get_horaires") and dispo.get_horaires():
        return datetime.strptime(dispo.get_horaires()[0], "%H:%M").time()
    return fallback

# =========================
# Estimation Livraison
# =========================
def estimer_heure_livraison(adresse_livraison, maintenant: datetime | None = None):
    """
    Estime la prochaine heure de livraison possible selon adresse, horaires et disponibilité livreurs.
    Retourne un datetime (aware) ou un dict {'error': '...'}.
    """
    HoraireDisponible = apps.get_model('swigo', 'HoraireDisponible')
    JourFermeture = apps.get_model('swigo', 'JourFermeture')
    VilleDesservie = apps.get_model('swigo', 'VilleDesservie')
    Livreur = apps.get_model('swigo', 'Livreur')
    Tournee = apps.get_model('swigo', 'Tournee')

    if maintenant is None:
        maintenant = timezone.localtime()

    logger.debug(f"[NOW] {maintenant}")

    # Fermeture du jour
    if hasattr(JourFermeture, "est_ferme") and JourFermeture.est_ferme(maintenant.date()):
        logger.info("[FERME] Restaurant fermé aujourd'hui")
        return {'error': "Le restaurant est fermé aujourd'hui."}

    JOURS_MAP = {0: "LUN", 1: "MAR", 2: "MER", 3: "JEU", 4: "VEN", 5: "SAM", 6: "DIM"}
    jour_semaine = JOURS_MAP[maintenant.weekday()]

    # Heures d'ouverture (premiers slots)
    HEURE_OUVERTURE_MIDI = get_heure_debut_service(jour_semaine, "MIDI", time(11, 30))
    HEURE_CUTOFF_MIDI = time(14, 30)
    HEURE_OUVERTURE_SOIR = get_heure_debut_service(jour_semaine, "SOIR", time(18, 30))
    HEURE_FIN_SOIR = time(22, 30)

    def get_service(dt: datetime) -> str:
        return "MIDI" if dt.time() < time(16, 0) else "SOIR"

    service_courant = get_service(maintenant)
    services_ouverts = list(HoraireDisponible.objects
                            .filter(jour=jour_semaine)
                            .values_list('service', flat=True)
                            .distinct())
    logger.debug(f"[SERVICE] Actuel: {service_courant} | Ouverts aujourd'hui: {services_ouverts}")

    if not services_ouverts:
        logger.info("[FERME] Aucun service ouvert aujourd'hui")
        # Si on est tard, tenter demain
        if maintenant.time() >= time(22, 0):
            jour_suivant = maintenant + timedelta(days=1)
            jour_str = JOURS_MAP[jour_suivant.weekday()]
            services_demain = list(HoraireDisponible.objects
                                   .filter(jour=jour_str)
                                   .values_list('service', flat=True)
                                   .distinct())
            if "MIDI" in services_demain:
                h = get_heure_debut_service(jour_str, "MIDI", time(11, 30))
                nouvelle_heure = make_aware(datetime.combine(jour_suivant.date(), h))
                return estimer_heure_livraison(adresse_livraison, maintenant=nouvelle_heure)
            if "SOIR" in services_demain:
                h = get_heure_debut_service(jour_str, "SOIR", time(18, 30))
                nouvelle_heure = make_aware(datetime.combine(jour_suivant.date(), h))
                return estimer_heure_livraison(adresse_livraison, maintenant=nouvelle_heure)

        return {'error': "Aucun service ouvert aujourd'hui."}

    # Si le service courant n'est pas ouvert, bascule au soir si possible
    if service_courant not in services_ouverts:
        if "SOIR" in services_ouverts:
            service_courant = "SOIR"
            if maintenant.time() < HEURE_OUVERTURE_SOIR:
                maintenant = make_aware(datetime.combine(maintenant.date(), HEURE_OUVERTURE_SOIR))
                logger.debug(f"[PASSAGE] Vers SOIR à {maintenant}")
        else:
            return {'error': f"Le service du {service_courant.lower()} est fermé aujourd'hui."}

    # Temps livraison par ville
    try:
        VilleDesservie_obj = VilleDesservie.objects.get(ville=adresse_livraison.ville)
        temps_livraison = int(VilleDesservie_obj.temps_gisors or 20)
    except VilleDesservie.DoesNotExist:
        temps_livraison = 60
    logger.debug(f"[ROUTE] Temps livraison estimé: {temps_livraison} min")

    # Bornes du service
    if service_courant == "SOIR":
        heure_ouverture_service = HEURE_OUVERTURE_SOIR
        heure_fin_service = HEURE_FIN_SOIR
    else:
        heure_ouverture_service = HEURE_OUVERTURE_MIDI
        heure_fin_service = HEURE_CUTOFF_MIDI

    heure_ouverture = make_aware(datetime.combine(maintenant.date(), heure_ouverture_service))
    heure_fin = make_aware(datetime.combine(maintenant.date(), heure_fin_service))

    # Calcul heure mini possible (prépa + trajet)
    delai_total = TEMPS_PREPARATION_MINUTES + temps_livraison  # MODIFICATION : Temps de préparation augmenté
    debut_possible = max(heure_ouverture, maintenant + timedelta(minutes=delai_total))
    logger.debug(f"[MIN] Début possible: {debut_possible} (prépa {TEMPS_PREPARATION_MINUTES} + route {temps_livraison})")

    # CORRECTION : Logique améliorée de bascule MIDI→SOIR
    if service_courant == "MIDI" and "SOIR" in services_ouverts:
        # Cas 1: Commande après le cutoff MIDI → bascule directe vers SOIR
        if maintenant.time() >= HEURE_CUTOFF_MIDI:
            switch_heure = make_aware(datetime.combine(maintenant.date(), HEURE_OUVERTURE_SOIR))
            debut_possible = max(debut_possible, switch_heure)
            service_courant = "SOIR"
            logger.debug(f"[BASCULE CUTOFF] Midi -> Soir à {debut_possible}")
        # Cas 2: L'heure estimée dépasse le cutoff MIDI → bascule aussi
        elif debut_possible.time() > HEURE_CUTOFF_MIDI:
            switch_heure = make_aware(datetime.combine(maintenant.date(), HEURE_OUVERTURE_SOIR))
            debut_possible = max(debut_possible, switch_heure)
            service_courant = "SOIR"
            logger.debug(f"[BASCULE ESTIM] Midi -> Soir (estim dépasse cutoff) à {debut_possible}")

    # Estimation selon dispo livreur
    livreurs_libres = apps.get_model('swigo', 'Livreur').objects.filter(au_travaille=True, is_booked=False)
    if livreurs_libres.exists():
        est = maintenant + timedelta(minutes=delai_total)
        prochaine_heure = max(est, debut_possible)
        logger.debug(f"[LIVREUR OK] Prochaine estimation brute: {prochaine_heure}")
    else:
        TourneeModel = apps.get_model('swigo', 'Tournee')
        tournees = TourneeModel.objects.filter(
            is_done=False, is_closed=True, is_sent_livreur=True,
            livreur__au_travaille=True, heure_retour_estime__isnull=False
        )
        estimations_possibles = []
        for t in tournees:
            retour = make_aware(datetime.combine(t.date_tournee, t.heure_retour_estime))
            autre = TourneeModel.objects.filter(
                livreur=t.livreur, is_done=False, is_closed=False,
                date_tournee=t.date_tournee, nom__gt=t.nom
            ).exists()
            if not autre:
                est = retour + timedelta(minutes=delai_total)
                estimations_possibles.append(max(est, debut_possible))

        if estimations_possibles:
            prochaine_heure = min(estimations_possibles)
            logger.debug(f"[TOURNEE] Estim via retour: {prochaine_heure}")
        else:
            prochaine_heure = max(maintenant + timedelta(minutes=40 + delai_total), debut_possible)
            logger.debug(f"[DEF AUTRE] Estimation par défaut: {prochaine_heure}")

    # CORRECTION : Vérification intelligente des horaires avec bascule
    if service_courant == "SOIR":
        heure_fin_effective = HEURE_FIN_SOIR
    else:
        heure_fin_effective = HEURE_CUTOFF_MIDI

    # Vérifier si l'heure estimée dépasse les horaires du service actuel
    if prochaine_heure.time() > heure_fin_effective:
        logger.debug(f"[HORS HORAIRE {service_courant}] {prochaine_heure.time()} après {heure_fin_effective}")
        
        # CORRECTION : Si on dépasse le cutoff MIDI, essayer de basculer vers SOIR
        if service_courant == "MIDI" and "SOIR" in services_ouverts:
            switch_heure = make_aware(datetime.combine(maintenant.date(), HEURE_OUVERTURE_SOIR))
            prochaine_heure = max(prochaine_heure, switch_heure)
            service_courant = "SOIR"
            logger.debug(f"[BASCULE HORAIRE] MIDI->SOIR à {prochaine_heure}")
        else:
            # Sinon, reporter au jour suivant
            logger.debug("[REPORT] Bascule au jour suivant")
            next_date = prochaine_heure.date()
            for i in range(1, 8):  # Chercher sur 7 jours
                d = next_date + timedelta(days=i)
                j = JOURS_MAP[d.weekday()]
                dispo = HoraireDisponible.objects.filter(jour=j).values_list('service', flat=True).distinct()
                if "MIDI" in dispo:
                    h = get_heure_debut_service(j, "MIDI", time(11, 30))
                    prochaine_heure = make_aware(datetime.combine(d, h))
                    break
                if "SOIR" in dispo:
                    h = get_heure_debut_service(j, "SOIR", time(18, 30))
                    prochaine_heure = make_aware(datetime.combine(d, h))
                    break
            logger.debug(f"[NEXT OPEN] {prochaine_heure}")

    # Arrondi & recherche créneau dispo
    heure_estimee_brute = chercher_prochain_creneau_disponible(prochaine_heure, mode='livraison')
    heure_estimee = arrondir_au_quart_heure(heure_estimee_brute)

    # Ajustement léger possible (jamais avant debut_possible)
    candidate = heure_estimee - timedelta(minutes=15)
    if (heure_estimee.minute == 15
        and (heure_estimee - prochaine_heure).seconds < 20 * 60
        and candidate >= debut_possible):
        logger.debug(f"[AJUST] {heure_estimee} -> {candidate}")
        heure_estimee = candidate

    # Si l'heure estimée est aujourd'hui mais passée, chercher dès demain
    if heure_estimee.date() == maintenant.date() and heure_estimee < maintenant:
        logger.debug(f"[DEPASSE] {heure_estimee} -> recherche lendemain")
        prochaine_heure = None
        for i in range(1, 7):
            d = maintenant.date() + timedelta(days=i)
            j = JOURS_MAP[d.weekday()]
            services_dispos = HoraireDisponible.objects.filter(jour=j).values_list('service', flat=True).distinct()
            if "MIDI" in services_dispos:
                h = get_heure_debut_service(j, "MIDI", time(11, 30))
                prochaine_heure = make_aware(datetime.combine(d, h))
                break
            if "SOIR" in services_dispos:
                h = get_heure_debut_service(j, "SOIR", time(18, 30))
                prochaine_heure = make_aware(datetime.combine(d, h))
                break
        if not prochaine_heure:
            return {'error': "Aucun créneau de livraison disponible cette semaine."}
        heure_estimee = chercher_prochain_creneau_disponible(prochaine_heure, mode="livraison")

    # Vérifications finales de cohérence
    JOURS_MAP = {0: "LUN", 1: "MAR", 2: "MER", 3: "JEU", 4: "VEN", 5: "SAM", 6: "DIM"}
    jour_final = JOURS_MAP[heure_estimee.weekday()]
    service_final = get_service(heure_estimee)

    if not HoraireDisponible.objects.filter(jour=jour_final, service=service_final).exists():
        return {'error': f"Le service du {service_final.lower()} est fermé pour ce créneau."}

    if service_final == "MIDI" and heure_estimee.time() > HEURE_CUTOFF_MIDI:
        return {'error': "Il est trop tard pour une livraison ce midi."}
    if service_final == "SOIR" and heure_estimee.time() > time(22, 30):
        return {'error': "Il est trop tard pour une livraison ce soir."}

    return heure_estimee

# =========================
# Estimation Retrait (à emporter)
# =========================
def estimer_heure_retrait():
    """
    Estime la prochaine heure de retrait (à emporter), alignée sur les créneaux de 15 minutes.
    """
    now_local = timezone.localtime()

    # Horaires fixes (adapte selon ton modèle HoraireDisponible si besoin)
    HEURE_OUVERTURE = time(11, 0)
    HEURE_CUTOFF = time(14, 30)
    HEURE_DEBUT_SOIR_LOCAL = time(18, 0)
    HEURE_FIN_SOIR = time(22, 30)

    # Début prépa = maintenant ou début du prochain service
    if now_local.time() < HEURE_CUTOFF:
        debut_service = make_aware(datetime.combine(now_local.date(), HEURE_OUVERTURE))
    else:
        debut_service = make_aware(datetime.combine(now_local.date(), HEURE_DEBUT_SOIR_LOCAL))

    debut_prepa = max(now_local, debut_service)
    fin_prepa = debut_prepa + timedelta(minutes=TEMPS_PREPARATION_MINUTES)  # MODIFICATION : Utilise le nouveau temps de préparation

    # Arrondi au quart d'heure supérieur
    minute_arrondie = ((fin_prepa.minute // 15) + 1) * 15
    if minute_arrondie >= 60:
        fin_prepa += timedelta(hours=1)
        minute_arrondie = 0

    fin_prepa = fin_prepa.replace(minute=minute_arrondie, second=0, microsecond=0)

    # Limite fin de service
    if fin_prepa.time() > HEURE_FIN_SOIR:
        raise Exception("Il est trop tard pour commander à emporter aujourd'hui.")

    # Cherche le créneau dispo en mode 'emporter'
    return chercher_prochain_creneau_disponible(fin_prepa, mode='emporter')

# =========================
# Vérifs & paiements
# =========================
def verifier_ou_corriger_creneau_livraison(commande):
    """
    Vérifie si le créneau de livraison spécifié est encore valide.
    Si non, recalcule automatiquement un nouveau créneau. Ne fait rien si verrouillé.
    """
    maintenant = timezone.localtime()

    if getattr(commande, "horaire_verrouille", False):
        logger.debug(f"[LOCK] Horaire verrouillé pour commande {commande.id}, aucune modif")
        return commande.heure_livraison_specifiee or commande.heure_livraison_asap

    if not commande.date_livraison_specifiee or not commande.heure_livraison_specifiee:
        logger.debug("[CRENEAU] Incomplet (date/heure manquantes), estimation ASAP")
        heure_estimee = estimer_heure_livraison(commande.adresse_livraison)
        
        # CORRECTION : Mettre à jour TOUS les champs de date/heure
        commande.heure_livraison_asap = heure_estimee
        commande.date_livraison_specifiee = heure_estimee.date()  # ← AJOUT
        commande.heure_livraison_specifiee = heure_estimee.time()  # ← AJOUT
        commande.horaire_verrouille = True
        
        commande.save(update_fields=['heure_livraison_asap', 'date_livraison_specifiee', 'heure_livraison_specifiee', 'horaire_verrouille'])
        return heure_estimee

    heure_choisie = make_aware(
        datetime.combine(commande.date_livraison_specifiee, commande.heure_livraison_specifiee),
        timezone.get_current_timezone()
    )
    logger.debug(f"[CHECK] Creneau client: {heure_choisie} | Now: {maintenant}")

    recalcul = False
    if heure_choisie < maintenant:
        logger.debug("[CHECK] Créneau passé")
        recalcul = True
    elif not creneau_est_disponible(heure_choisie.date(), heure_choisie.time(), mode="livraison"):
        logger.debug("[CHECK] Créneau saturé")
        recalcul = True

    if not recalcul:
        logger.debug("[OK] Créneau valide, verrouillage")
        commande.horaire_verrouille = True
        commande.save(update_fields=['horaire_verrouille'])
        return heure_choisie

    # Recalcul automatique
    nouvelle_heure = estimer_heure_livraison(commande.adresse_livraison, maintenant=maintenant)
    logger.debug(f"[RECALC] Nouveau créneau: {nouvelle_heure}")
    
    # CORRECTION : Mettre à jour TOUS les champs
    commande.heure_livraison_asap = nouvelle_heure
    commande.date_livraison_specifiee = nouvelle_heure.date()  # ← AJOUT
    commande.heure_livraison_specifiee = nouvelle_heure.time()  # ← AJOUT
    commande.horaire_verrouille = True
    
    commande.save(update_fields=['heure_livraison_asap', 'date_livraison_specifiee', 'heure_livraison_specifiee', 'horaire_verrouille'])
    return nouvelle_heure


def obtenir_paiements_possibles(commande):
    """
    Renvoie la liste des moyens de paiement disponibles pour la commande.
    Désactive tout sauf CB si nouveau client (pas d'historique payé).
    """
    Commande = apps.get_model('swigo', 'Commande')
    client = commande.client

    is_nouveau = not (Commande.objects
                      .filter(client=client, is_paid=True)
                      .exclude(id=commande.id)
                      .exists())

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

    if is_nouveau:
        for p in paiements:
            if p['id'] != 'stripe':
                p['disabled'] = True

    return paiements


def verifier_ou_corriger_creneau_retrait(commande):
    """
    Vérifie si le créneau de retrait choisi est toujours valide.
    Si non, en propose un autre automatiquement. Ne modifie rien si verrouillé.
    """
    maintenant = timezone.localtime()
    heure_choisie = commande.heure_pick_up_specifie

    if getattr(commande, "horaire_verrouille", False):
        logger.debug(f"[LOCK] Horaire verrouillé pour commande {commande.id}, aucune modification")
        return heure_choisie

    logger.debug(f"[CHECK RETRAIT] Créneau demandé: {heure_choisie}")

    if not heure_choisie:
        logger.debug("[CHECK RETRAIT] Créneau non précisé -> estimation")
        heure_estimee = estimer_heure_retrait()
        commande.heure_pick_up_specifie = heure_estimee
        # Pour les commandes à emporter, aussi sauvegarder la date/heure
        commande.date_livraison_specifiee = heure_estimee.date()  # ← AJOUT (optionnel)
        commande.heure_livraison_specifiee = heure_estimee.time()  # ← AJOUT (optionnel)
        commande.horaire_verrouille = True
        commande.save(update_fields=['heure_pick_up_specifie', 'date_livraison_specifiee', 'heure_livraison_specifiee', 'horaile_verrouille'])
        return heure_estimee

    recalcul = False
    if heure_choisie < maintenant:
        logger.debug("[CHECK RETRAIT] Créneau passé")
        recalcul = True
    elif not creneau_est_disponible(heure_choisie.date(), heure_choisie.time(), mode="retrait"):
        logger.debug("[CHECK RETRAIT] Créneau indisponible")
        recalcul = True

    if not recalcul:
        logger.debug("[OK RETRAIT] Créneau valide, verrouillage")
        commande.horaire_verrouille = True
        commande.save(update_fields=['horaire_verrouille'])
        return heure_choisie

    nouvelle_heure = estimer_heure_retrait()
    logger.debug(f"[RECALC RETRAIT] Nouveau créneau: {nouvelle_heure}")
    commande.heure_pick_up_specifie = nouvelle_heure
    # Pour les commandes à emporter, aussi sauvegarder la date/heure
    commande.date_livraison_specifiee = nouvelle_heure.date()  # ← AJOUT (optionnel)
    commande.heure_livraison_specifiee = nouvelle_heure.time()  # ← AJOUT (optionnel)
    commande.horaire_verrouille = True
    commande.save(update_fields=['heure_pick_up_specifie', 'date_livraison_specifiee', 'heure_livraison_specifiee', 'horaire_verrouille'])
    return nouvelle_heure


def get_temps_livraison_minutes(adresse_livraison):
    """
    Temps de livraison selon la ville desservie ; fallback 60 min si non trouvée.
    """
    VilleDesservie = apps.get_model('swigo', 'VilleDesservie')
    try:
        ville = VilleDesservie.objects.get(ville=adresse_livraison.ville)
        return int(ville.temps_gisors or 20)
    except VilleDesservie.DoesNotExist:
        return 60

# =========================
# Conversions stock & prix (g/ml/u)
# =========================
# Conversion vers les unités de STOCK (entiers)
#  - unite_stock 'g'  : stocké en grammes
#  - unite_stock 'l'  : stocké en millilitres
#  - unite_stock 'u'  : stocké en unités
CONV_TO_STOCK = {
    # vers 'g'
    ('g', 'g'): Decimal('1'),
    ('kg', 'g'): Decimal('1000'),
    ('mg', 'g'): Decimal('0.001'),

    # vers 'l' (stock en ml)
    ('ml', 'l'): Decimal('1'),
    ('cl', 'l'): Decimal('10'),
    ('l',  'l'): Decimal('1000'),

    # vers 'u'
    ('u', 'u'): Decimal('1'),
}

def to_stock_units(qty, from_unit, unite_stock) -> int:
    """
    Convertit qty (g, kg, ml, cl, l, u) vers l'unité de STOCK de l'ingrédient (entier).
    """
    q = Decimal(str(qty))
    key = (from_unit, unite_stock)
    if key not in CONV_TO_STOCK:
        raise ValueError(f"Conversion non supportée: {from_unit} -> {unite_stock}")
    val = (q * CONV_TO_STOCK[key]).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(val)

def price_per_stock_unit(total_price_eur, qty, from_unit, unite_stock) -> Decimal:
    """
    Calcule le prix unitaire d'achat cohérent avec l'unité de STOCK (€/g, €/ml, €/u).
    Exemple :
      - 2 kg farine à 3,00 € → 3000 g → 3/3000 = 0.0010 €/g
      - 1 l lait à 1,10 €   → 1000 ml → 0.0011 €/ml
      - 30 œufs à 5,40 €    → 30 u    → 0.18 €/u
    """
    total = Decimal(str(total_price_eur))
    stock_qty = Decimal(to_stock_units(qty, from_unit, unite_stock))
    if stock_qty <= 0:
        raise ValueError("Quantité convertie nulle ou négative.")
    return (total / stock_qty).quantize(Decimal('0.0001'))

def format_qty(qty, unit_stock):
    """
    Formate les quantités pour affichage humain.
    - g -> g ou kg
    - l (stock en ml) -> ml ou l
    - u -> unités
    """
    if unit_stock == "g":
        if qty >= 1000:
            return f"{qty/1000:.2f} kg"
        return f"{qty:.0f} g"
    elif unit_stock == "l":
        if qty >= 1000:
            return f"{qty/1000:.2f} l"
        return f"{qty:.0f} ml"
    elif unit_stock == "u":
        return f"{qty:.0f} u"
    return f"{qty} {unit_stock}"

def afficher_recette_detail(recette):
    """
    Affiche le détail d'une recette : ingrédients, quantités, coût par ingrédient,
    total et prix de revient unitaire.
    """
    from swigo.models import RecetteIngredient

    print(f"📋 Recette : {recette.nom} ({recette.portions} portions)")
    total_ht = Decimal("0")
    lignes = []

    for ri in RecetteIngredient.objects.filter(recette=recette).select_related("ingredient"):
        ing = ri.ingredient
        q = ri.quantite
        u = ri.unite

        # conversion vers unité de stock
        try:
            q_stock = Decimal(to_stock_units(q, u, ing.unite_stock))
        except Exception as e:
            q_stock = Decimal("0")
            print(f"⚠️ Conversion impossible {q}{u} -> {ing.unite_stock} pour {ing.nom} ({e})")

        cout_ht = q_stock * (ing.prix_unitaire_achat or 0)
        total_ht += cout_ht

        lignes.append((ing.nom, q, u, q_stock, ing.unite_stock, ing.prix_unitaire_achat, cout_ht))

    # affichage
    for nom, q, u, qs, us, pu, cout in lignes:
        print(f"- {nom:<20} {q} {u} (~{format_qty(qs, us)}) @ {pu} €/ {us} = {cout:.4f} € HT")

    print("—" * 50)
    print(f"TOTAL HT recette : {total_ht:.4f} €")
    print(f"PRU HT unitaire  : {(total_ht/recette.portions).quantize(Decimal('0.001'))} €")
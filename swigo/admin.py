# admin.py
from django.contrib import admin
from django.apps import apps
from decimal import Decimal

from .models import (
    # Clients & Adresses
    Categorie, Client, ClientBlacklist, AdresseLivraison, VilleDesservie,
    # Plages horaires / fermetures
    HoraireDisponible, JourFermeture,
    # Stock & ingrédients
    Ingredient, ProduitTransforme, ProduitVenteDirecte, MouvementStock,
    # Produits / Cartes
    Plat, Option, Cuisson, PouletOption,
    # Courses & fournisseurs
    ListeDeCourses, ArticleListeDeCourses, Fournisseur,
    # Panier / Commande / Promo
    Panier, ArticlePanier, Commande, CodePromo,
    # Livraison & logistique
    Livreur, Tournee, TourneeCommande,
    # Facturation
    Facture, LigneFacture,
    # Salade personnalisée
    SaladePersonnalisee,
    # Menus
    Menu, ComposantMenuFixe, ChoixMenu, ChoixMenuArticle,
    # Couscous
    CouscousPersonnalise, FormuleCouscous, ViandeCouscous, ChoixViandeCouscous,
    OptionXL, AccompagnementCouscous,
    # Sides génériques
    Accompagnement,
)

# =========================
# Inlines
# =========================

class TourneeCommandeInline(admin.TabularInline):
    model = TourneeCommande
    extra = 0
    ordering = ['ordre']


# =========================
# Actions
# =========================

@admin.action(description="Blacklister les clients sélectionnés")
def blacklister_clients(modeladmin, request, queryset):
    for client in queryset:
        ClientBlacklist.objects.get_or_create(
            email=client.email,
            numero_telephone=client.numero_telephone,
            defaults={'raison': "Ajout manuel via l’admin"},
        )
    modeladmin.message_user(request, f"{queryset.count()} client(s) blacklisté(s).")


# =========================
# Admins – Référentiel
# =========================

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ("nom", "icone", "ordre")
    list_editable = ("icone", "ordre")
    search_fields = ("nom",)
    ordering = ("ordre",)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "numero_telephone", "email", "date_creation")
    search_fields = ("nom", "prenom", "numero_telephone", "email")
    ordering = ("-date_creation",)
    actions = [blacklister_clients]


@admin.register(ClientBlacklist)
class ClientBlacklistAdmin(admin.ModelAdmin):
    list_display = ("email", "numero_telephone", "raison", "date_blocage")
    list_filter = ("date_blocage",)
    search_fields = ("email", "numero_telephone")
    readonly_fields = ("date_blocage",)


@admin.register(AdresseLivraison)
class AdresseLivraisonAdmin(admin.ModelAdmin):
    list_display = ("client", "adresse", "code_postal", "ville", "zone", "localisation", "delai_livraison_estime")
    list_filter = ("zone", "localisation")
    search_fields = ("adresse", "code_postal", "ville")


@admin.register(VilleDesservie)
class VilleDesservieAdmin(admin.ModelAdmin):
    list_display = ("ville", "code_postal", "nombre_habitants", "distance_gisors", "temps_gisors", "zone", "panier_minimal", "localisation")
    list_filter = ("zone", "localisation")
    search_fields = ("ville", "code_postal")


@admin.register(JourFermeture)
class JourFermetureAdmin(admin.ModelAdmin):
    list_display = ("date_debut", "date_fin", "description")
    list_filter = ("date_debut", "date_fin")
    search_fields = ("description",)


@admin.register(HoraireDisponible)
class HoraireDisponibleAdmin(admin.ModelAdmin):
    list_display = ("jour", "get_jour_complet", "service", "heure_debut", "heure_fin", "intervalle", "capacite_max", "nombre_commandes")
    list_editable = ("intervalle", "capacite_max", "nombre_commandes")
    list_filter = ("jour", "service")
    search_fields = ("jour", "service")
    ordering = ("jour", "service")

    @admin.display(description="Jour complet")
    def get_jour_complet(self, obj):
        return obj.get_jour_display()


# =========================
# Admins – Stock & ingrédients
# =========================

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("nom", "quantite_stock", "unite_stock", "prix_unitaire_achat", "groupe", "vendable_directement")
    list_filter = ("groupe", "vendable_directement")
    search_fields = ("nom",)


@admin.register(ProduitVenteDirecte)
class ProduitVenteDirecteAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "prix_unitaire_vente_ttc", "taux_tva_vente")
    search_fields = ("ingredient__nom",)


@admin.register(ProduitTransforme)
class ProduitTransformeAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "quantite_disponible", "unite")
    list_filter = ("categorie",)
    search_fields = ("nom",)


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "date", "quantity", "price_per_unit")
    list_filter = ("ingredient", "date")
    search_fields = ("ingredient__nom",)


# =========================
# Admins – Carte / Produits
# =========================

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "prix_unitaire_ttc", "taux_tva", "type_plat", "type_burger", "disponible")
    list_editable = ("type_plat", "disponible")  # 🆕 Permet l'édition directe dans la liste
    list_filter = ("categorie", "type_plat", "type_burger", "disponible")
    search_fields = ("nom", "description_courte")
    
    # 🆕 Définir explicitement les champs du formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('nom', 'categorie', 'type_plat', 'type_burger', 'disponible')
        }),
        ('Descriptions', {
            'fields': ('description_courte', 'description_longue')
        }),
        ('Prix', {
            'fields': ('prix_unitaire_ttc', 'taux_tva')
        }),
        ('Photos', {
            'fields': ('photo',)
        }),
        ('Configuration avancée', {
            'fields': ('recette', 'produit_transforme', 'est_compose'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("nom_option", "plat", "prix_unitaire_ttc", "taux_tva", "categorie", "ordre")
    list_filter = ("categorie", "taux_tva", "plat")
    search_fields = ("nom_option", "plat__nom")


@admin.register(Cuisson)
class CuissonAdmin(admin.ModelAdmin):
    list_display = ("plat", "option", "temps_cuisson_affiche")
    search_fields = ("plat__nom", "option__nom_option")

    @admin.display(description="Temps de cuisson")
    def temps_cuisson_affiche(self, obj):
        # Exemple : si ton modèle a 'temps' ou 'duree' (à adapter)
        if hasattr(obj, "temps"):
            return f"{obj.temps} min"
        elif hasattr(obj, "duree"):
            return f"{obj.duree} min"
        else:
            return "-"



@admin.register(PouletOption)
class PouletOptionAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "prix_supplement", "ordre", "disponible")
    list_filter = ("categorie", "disponible")
    search_fields = ("nom",)


@admin.register(Accompagnement)
class AccompagnementAdmin(admin.ModelAdmin):
    list_display = ("nom", "prix_supplement", "ordre", "disponible")
    list_filter = ("disponible",)
    search_fields = ("nom",)


# =========================
# Admins – Courses & Fournisseurs
# =========================

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(ListeDeCourses)
class ListeDeCoursesAdmin(admin.ModelAdmin):
    list_display = ("fournisseur", "date")
    list_filter = ("fournisseur", "date")
    search_fields = ("fournisseur__nom",)


@admin.register(ArticleListeDeCourses)
class ArticleListeDeCoursesAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "liste", "quantite", "unite", "est_achete", "prix_unitaire_achat")
    list_filter = ("liste", "est_achete")
    search_fields = ("ingredient__nom", "liste__fournisseur__nom")


# =========================
# Admins – Panier / Commande / Code Promo
# =========================

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ("id", "commande_id", "frais_livraison_effectif", "frais_gestion", "sous_total", "prix_total", "is_locked", "date_modification")
    readonly_fields = ("frais_livraison_effectif", "date_modification",)
    search_fields = ("session_key", "commande__id")

    def frais_livraison_effectif(self, obj):
        return obj.frais_livraison if not (obj.commande and obj.commande.is_commande_a_emporter) else Decimal("0.00")
    frais_livraison_effectif.short_description = "Frais livraison effectif"

    def commande_id(self, obj):
        return obj.commande.id if obj.commande else "-"
    commande_id.short_description = "Commande ID"


@admin.register(ArticlePanier)
class ArticlePanierAdmin(admin.ModelAdmin):
    list_display = ("commande_id", "plat", "quantite", "prix_total")
    search_fields = ("panier__session_key", "plat__nom")

    def commande_id(self, obj):
        if obj.panier and obj.panier.commande:
            return obj.panier.commande.id
        return "-"
    commande_id.short_description = "Commande ID"
    commande_id.admin_order_field = "panier__commande__id"


@admin.register(CodePromo)
class CodePromoAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "reduction_type", "reduction_amount", "date_debut", "date_fin")
    list_filter = ("reduction_type",)
    search_fields = ("code", "description")


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "client", "adresse_livraison", "is_commande_a_emporter",
        "commande_is_valid", "is_paid", "resume_paiement",
        "is_in_the_kitchen", "is_cooked", "is_ready_to_ship", "is_shipped",
        "is_delivered", "heure_paiement", "heure_in_the_kitchen", "heure_cooked",
        "heure_ready_to_ship", "heure_shipped", "heure_delivered", "heure_pick_up_specifie",
    )
    list_filter = (
        "is_commande_a_emporter", "is_paid", "commande_is_valid", "is_in_the_kitchen",
        "is_cooked", "is_ready_to_ship", "is_shipped", "is_delivered",
    )
    search_fields = ("id", "client__nom", "adresse_livraison__adresse")
    readonly_fields = ("heure_paiement", "heure_in_the_kitchen", "heure_cooked", "heure_ready_to_ship", "heure_shipped", "heure_delivered")
    actions = ["mark_as_paid"]

    @admin.action(description="Marquer les commandes comme payées")
    def mark_as_paid(self, request, queryset):
        updated_count = 0
        for commande in queryset:
            if not commande.is_paid:
                # suppose une méthode set_paiement existe côté modèle
                commande.set_paiement(moyen="admin")
                updated_count += 1
        self.message_user(request, f"{updated_count} commande(s) marquée(s) comme payée(s).")

    @admin.display(description="Paiement")
    def resume_paiement(self, obj):
        if obj.montant_especes or obj.montant_ticket or obj.montant_stripe:
            return f"Mixte: {obj.montant_especes or 0}€ espèces, {obj.montant_ticket or 0}€ ticket, {obj.montant_stripe or 0}€ CB"
        return obj.get_moyen_paiement_display() or "Non renseigné"


# =========================
# Admins – Livraison & logistique
# =========================

@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ("nom", "telephone", "au_travaille", "is_booked", "latitude", "longitude")
    list_filter = ("au_travaille", "is_booked")
    search_fields = ("nom", "telephone")
    list_editable = ("au_travaille", "is_booked", "latitude", "longitude")


@admin.register(Tournee)
class TourneeAdmin(admin.ModelAdmin):
    list_display = ("nom", "date_tournee", "livreur", "heure_depart", "heure_retour_estime", "heure_retour_reel", "is_closed", "is_done")
    list_filter = ("date_tournee", "is_closed", "is_done", "livreur")
    search_fields = ("nom", "livreur__nom")
    inlines = [TourneeCommandeInline]
    ordering = ("date_tournee", "nom")


@admin.register(TourneeCommande)
class TourneeCommandeAdmin(admin.ModelAdmin):
    list_display = ("tournee", "commande", "ordre", "heure_passage")
    search_fields = ("tournee__nom", "commande__id")
    ordering = ("tournee", "ordre")


# =========================
# Admins – Facturation
# =========================

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ("numero", "commande", "client", "date_emission", "montant_ht", "montant_tva", "montant_ttc", "deja_reglee", "societe")
    list_filter = ("date_emission", "deja_reglee")
    search_fields = ("numero", "commande__id", "client__nom")


@admin.register(LigneFacture)
class LigneFactureAdmin(admin.ModelAdmin):
    list_display = ("facture", "description", "quantite", "prix_unitaire_ht", "taux_tva", "montant_ttc")
    list_filter = ("taux_tva",)
    search_fields = ("facture__numero", "description")


# =========================
# Admins – Salade personnalisée
# =========================

@admin.register(SaladePersonnalisee)
class SaladePersonnaliseeAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "prix_total")
    search_fields = ("client__nom",)


# =========================
# Admins – Menus
# =========================

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("nom", "prix_ttc", "taux_tva", "disponible")
    list_filter = ("disponible",)
    search_fields = ("nom",)


@admin.register(ComposantMenuFixe)
class ComposantMenuFixeAdmin(admin.ModelAdmin):
    list_display = ("menu", "role", "plat", "salade", "couscous")
    list_filter = ("role", "salade", "couscous", "menu")
    search_fields = ("menu__nom", "plat__nom")


@admin.register(ChoixMenu)
class ChoixMenuAdmin(admin.ModelAdmin):
    list_display = ("menu", "role", "autorise_salade_personnalisee", "autorise_couscous_personnalise")
    list_filter = ("role", "autorise_salade_personnalisee", "autorise_couscous_personnalise")
    search_fields = ("menu__nom",)


@admin.register(ChoixMenuArticle)
class ChoixMenuArticleAdmin(admin.ModelAdmin):
    list_display = ("article_panier", "role", "plat_choisi", "salade", "couscous", "info_text")
    list_filter = ("role",)
    search_fields = ("article_panier__id", "plat_choisi__nom")


# =========================
# Admins – Couscous
# =========================

@admin.register(FormuleCouscous)
class FormuleCouscousAdmin(admin.ModelAdmin):
    list_display = ("nom", "nombre_viandes_incluses", "prix_base_ttc")
    search_fields = ("nom",)


@admin.register(ViandeCouscous)
class ViandeCouscousAdmin(admin.ModelAdmin):
    list_display = ("nom", "portion", "supplement_inclus")
    search_fields = ("nom",)


@admin.register(OptionXL)
class OptionXLAdmin(admin.ModelAdmin):
    list_display = ("nom", "supplement")
    search_fields = ("nom",)


@admin.register(AccompagnementCouscous)
class AccompagnementCouscousAdmin(admin.ModelAdmin):
    list_display = ("code", "nom")
    search_fields = ("code", "nom")


@admin.register(ChoixViandeCouscous)
class ChoixViandeCouscousAdmin(admin.ModelAdmin):
    list_display = ("couscous", "viande", "est_incluse")
    list_filter = ("est_incluse",)
    search_fields = ("couscous__id", "viande__nom")


@admin.register(CouscousPersonnalise)
class CouscousPersonnaliseAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "formule", "option_xl", "prix_total")
    list_filter = ("option_xl", "formule")
    search_fields = ("client__nom", "formule__nom")


# =========================
# Auto-register pour les modèles non couverts ci-dessus
# =========================

# Enregistre automatiquement tout modèle de l’app qui n’a pas déjà un ModelAdmin dédié
app_config = apps.get_app_config(__name__.split(".")[0])  # récupère la config de l'app courante
for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

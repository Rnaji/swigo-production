from django.urls import path ,include
from swigo import swigo_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


app_name='swigo'
urlpatterns = [
    
    path('',swigo_views.adresse_livraison,name="index"),
    
    path('index/',swigo_views.index,name="index"),
    path('index-2/',swigo_views.index_2,name="index-2"),
    path('index-3/',swigo_views.index_3,name="index-3"),

    path('about-us/',swigo_views.about_us,name="about-us"),
    path('faq/',swigo_views.faq,name="faq"),
    path('team/',swigo_views.team,name="team"),
    path('team-detail/',swigo_views.team_detail,name="team-detail"),
    path('testimonial/',swigo_views.testimonial,name="testimonial"),
    path('services/',swigo_views.services,name="services"),
    path('service-detail/',swigo_views.service_detail,name="service-detail"),

    path('our-menu-1/',swigo_views.our_menu_1,name="our-menu-1"),
    path('our-menu-2/',swigo_views.our_menu_2,name="our-menu-2"),
    path('our-menu-3/',swigo_views.our_menu_3,name="our-menu-3"),
    path('our-menu-4/',swigo_views.our_menu_4,name="our-menu-4"),
    path('our-menu-5/',swigo_views.our_menu_5,name="our-menu-5"),

    path('shop-style-1/',swigo_views.shop_style_1,name="shop-style-1"),
    path('shop-style-2/',swigo_views.shop_style_2,name="shop-style-2"),
    path('shop-cart/',swigo_views.shop_cart,name="shop-cart"),
    path('shop-wishlist/',swigo_views.shop_wishlist,name="shop-wishlist"),
    path('shop-checkout/',swigo_views.shop_checkout,name="shop-checkout"),
    path('product-detail/',swigo_views.product_detail,name="product-detail"),

    path('blog-grid-2/',swigo_views.blog_grid_2,name="blog-grid-2"),
    path('blog-grid-3/',swigo_views.blog_grid_3,name="blog-grid-3"),
    path('blog-grid-left-sidebar/',swigo_views.blog_grid_left_sidebar,name="blog-grid-left-sidebar"),
    path('blog-grid-right-sidebar/',swigo_views.blog_grid_right_sidebar,name="blog-grid-right-sidebar"),

    path('blog-list/',swigo_views.blog_list,name="blog-list"),
    path('blog-list-left-sidebar/',swigo_views.blog_list_left_sidebar,name="blog-list-left-sidebar"),
    path('blog-list-right-sidebar/',swigo_views.blog_list_right_sidebar,name="blog-list-right-sidebar"),
    path('blog-both-sidebar/',swigo_views.blog_both_sidebar,name="blog-both-sidebar"),

    path('blog-standard/',swigo_views.blog_standard,name="blog-standard"),
    path('blog-open-gutenberg/',swigo_views.blog_open_gutenberg,name="blog-open-gutenberg"),
    path('blog-detail-left-sidebar/',swigo_views.blog_detail_left_sidebar,name="blog-detail-left-sidebar"),
    path('blog-detail-right-sidebar/',swigo_views.blog_detail_right_sidebar,name="blog-detail-right-sidebar"),

    path('blog-grid-3-masonary/',swigo_views.blog_grid_3_masonary,name="blog-grid-3-masonary"),
    path('blog-grid-4-masonary/',swigo_views.blog_grid_4_masonary,name="blog-grid-4-masonary"),
    path('blog-wide-list-sidebar/',swigo_views.blog_wide_list_sidebar,name="blog-wide-list-sidebar"),
    path('blog-wide-grid-sidebar/',swigo_views.blog_wide_grid_sidebar,name="blog-wide-grid-sidebar"),

    path('contact-us/',swigo_views.contact_us,name="contact-us"),
    path('coming-soon/',swigo_views.coming_soon,name="coming-soon"),
    path('under-maintenance/',swigo_views.under_maintenance,name="under-maintenance"),
    path('error-404/',swigo_views.error_404,name="error-404"),

    path('adresse_livraison/',swigo_views.adresse_livraison, name='adresse_livraison'),
    path('programmer-livraison/',swigo_views.programmer_livraison, name='programmer_livraison'),
    path('renseigner_commande/',swigo_views.renseigner_commande, name='renseigner_commande'),
    path('categories/', swigo_views.get_categories, name='get_categories'),
    path('plats_par_categorie_ajax/<str:categorie_nom>/', swigo_views.plats_par_categorie_ajax, name='plats_par_categorie_ajax'),
    path('options_par_plat_ajax/<int:plat_id>/', swigo_views.options_par_plat_ajax, name='options_par_plat_ajax'),
    path('ajouter_au_panier/', swigo_views.ajouter_au_panier, name='ajouter_au_panier'),
    path('remove_item_from_cart/', swigo_views.remove_item_from_cart, name='remove_item_from_cart'),
    path('get_cart_items/', swigo_views.get_cart_items, name='get_cart_items'),  # URL pour récupérer les articles du panier
    path('update_quantity/', swigo_views.update_quantity, name='update_quantity'),
    path('panier/', swigo_views.afficher_panier, name='afficher_panier'),
    path('appliquer_code_promo/', swigo_views.appliquer_code_promo, name='appliquer_code_promo'),
    path('valider_commande/', swigo_views.valider_commande, name='valider_commande'),
    path('get_adresse_livraison/', swigo_views.get_adresse_livraison, name='get_adresse_livraison'),
    path('success/', swigo_views.paiement_succes, name='stripe_success'),
    path('cancel/', swigo_views.paiement_annule, name='paiement_annule'),
    path('webhooks/stripe/', swigo_views.stripe_webhook, name='stripe_webhook'),
    path('accepter_livraison_asap/', swigo_views.accepter_livraison_asap, name='accepter_livraison_asap'),
    path('paiement-succes/', swigo_views.paiement_succes, name='paiement_succes'),

    path('assets-index/', swigo_views.assets_index, name='assets_index'),
    path('assets-logistique/', swigo_views.map_commandes_payees, name='assets_logistique'),  # Afficher la carte
    path('api/commandes-payees/', swigo_views.api_commandes_payees, name='api_commandes_payees'),  # API pour AJAX
    path('assets-logistique-attente/', swigo_views.map_commandes_en_attente_paiement, name='assets_logistique_attente'),  # Vue pour afficher la carte des commandes en attente de paiement
    path('api/commandes-attente-paiement/', swigo_views.api_commandes_en_attente_paiement, name='api_commandes_attente_paiement'),  # API pour les commandes en attente de paiement
    path('api/livreurs-positions/', swigo_views.api_livreurs_positions, name='api_livreurs_positions'),  # API pour suivre les livreurs
    path('api/update-livreur-position/', swigo_views.update_livreur_position, name='update_livreur_position'),
    path('api/tournees-existantes/', swigo_views.api_tournees_existantes, name='api_tournees_existantes'),
    path('attribuer-commande-a-tournee/', swigo_views.attribuer_commande_a_tournee, name='attribuer_commande_a_tournee'),
    path('creer-nouvelle-tournee/', swigo_views.creer_nouvelle_tournee, name='creer_nouvelle_tournee'),
    path('api/tournees/', swigo_views.api_affichage_tournees, name='api_affichage_tournees'),
    path('sauvegarder-ordre-commandes/', swigo_views.sauvegarder_ordre_commandes, name='sauvegarder_ordre_commandes'),
    path('api/tournee/<str:nom_tournee>/adresses/', swigo_views.api_adresses_tournee, name='api_adresses_tournee'),
    path('api/commandes/<int:commande_id>/', swigo_views.api_commande_details, name='api_commande_details'),
    path('api/panier/<int:commande_id>/', swigo_views.api_detail_panier, name='api_detail_panier'),
    path('cloturer-tournee/<str:tournee_id>/', swigo_views.cloturer_tournee, name='cloturer_tournee'),
    path('assets-cuisine/', swigo_views.cuisine_view, name='assets_cuisine'),
    path('ajax/get_commandes_cuisine/', swigo_views.get_commandes_cuisine, name='get_commandes_cuisine'),
    path('assets-bar/', swigo_views.bar_view, name='assets_bar'),
    path('commande/<int:commande_id>/cuisson_en_cours/', swigo_views.activer_cuisson, name="activer_cuisson"),
    path('tournee/<str:tournee_id>/set_cooked/', swigo_views.set_cooked, name='set_cooked'),
    path('get-commandes-bar/', swigo_views.get_commandes_bar, name='get_commandes_bar'),
    path('tournee/<int:tournee_id>/set_ok_bar/', swigo_views.set_ok_bar, name='set_ok_bar'),
    path('tournee/<int:tournee_id>/attribuer-livreur/<int:livreur_id>/', swigo_views.attribuer_livreur_a_tournee, name='attribuer_livreur_a_tournee'),
    path('livreur/tournee/<str:tournee_nom>/', swigo_views.vue_livreur, name='vue_livreur'),
    path('api/tournee/<str:tournee_nom>/envoyer/', swigo_views.envoyer_tournee, name='envoyer_tournee'),
    path('api/demarrer-tournee/', swigo_views.demarrer_tournee, name='demarrer_tournee'),
    path('api/tournee/<str:nomTournee>/update-heure-retour-estime/', swigo_views.update_heure_retour_estime, name='update_heure_retour_estime'),
    path('api/tournee/update-heures-passage/', swigo_views.update_heures_passage, name='update_heures_passage'),
    path('api/commande/<int:commande_id>/set-delivered/', swigo_views.set_delivered, name='set_delivered'),
    path('api/tournee/<int:tournee_nom>/set-shipped/', swigo_views.set_tournee_shipped, name='set_tournee_shipped'),
    path('api/tournee/<int:tournee_nom>/mark-as-done/', swigo_views.mark_tournee_as_done, name='mark_tournee_as_done'),
    path('api/update-heure-retour-reel/<str:nomTournee>/', swigo_views.update_heure_retour_reel, name='update_heure_retour_reel'),
    path('tournees-livreurs/', swigo_views.vue_livreurs_tournees, name='tournees_livreurs'),
    path('api/marquer-retour/<str:tournee_nom>/', swigo_views.mark_tournee_as_done, name='mark_tournee_as_done'),
    path('tournees-livreurs/<str:tournee_nom>/', swigo_views.tournee_detail, name='tournee_detail'),
    path('valider-livreur/<str:tournee_nom>/', swigo_views.valider_livreur, name='valider_livreur'),
    path('ajax/get_livreurs_disponibles/', swigo_views.get_livreurs_disponibles, name='get_livreurs_disponibles'),
    path('get_livreurs_disponibles_bar/', swigo_views.get_livreurs_disponibles_bar, name='get_livreurs_disponibles_bar'),
    path('api/marquer-emportee/', swigo_views.marquer_emportee, name='marquer_emportee'),
    path('api/commandes-a-payer/', swigo_views.api_commandes_a_payer, name='api_commandes_a_payer'),
    path('api/enregistrer-paiement/', swigo_views.enregistrer_paiement, name='enregistrer_paiement'),
    path('caisse/commandes-a-payer/', swigo_views.commandes_a_payer_view, name='commandes_a_payer'),
    path('caisse/commandes-payees/', swigo_views.commandes_payees_view, name='commandes_payees'),
    path('commandes-du-jour/', swigo_views.commandes_du_jour, name='commandes_du_jour'),
    path('get_panier_minimum/', swigo_views.get_panier_minimum, name='get_panier_minimum'),

    path('api/commandes-payees/', swigo_views.api_commandes_payees, name="api_commandes_payees"),

    path('api/commandes_a_livrer/', swigo_views.api_commandes_a_livrer, name='api_commandes_a_livrer'),


    path(
        'gestionnaire-stock/', 
        swigo_views.assets_gestionnaire_stock, 
        name='assets_gestionnaire_stock'
    ),
    path(
        'liste_de_courses/<int:fournisseur_id>/', 
        swigo_views.afficher_liste_de_courses, 
        name='liste_de_courses'
    ),
    path(
        'toggle-article-achete/<int:article_id>/', 
        swigo_views.toggle_article_achete, 
        name='toggle_article_achete'
    ),
    path(
        'supprimer-article/<int:article_id>/', 
        swigo_views.supprimer_article_liste_de_courses, 
        name='supprimer_article_liste_de_courses'
    ),
    path(
        'ajouter-a-la-liste-de-courses/<int:ingredient_id>/<int:fournisseur_id>/', 
        swigo_views.ajouter_a_la_liste_de_courses, 
        name='ajouter_a_la_liste_de_courses'
    ),
    path(
        'save-article-order/', 
        swigo_views.save_article_order, 
        name='save_article_order'
    ),
    path(
        'ajouter-stock/<int:ingredient_id>/', 
        swigo_views.ajouter_stock, 
        name='ajouter_stock'
    ),


    path('archiver_liste_de_courses/<int:liste_id>/', swigo_views.archiver_liste_de_courses, name='archiver_liste_de_courses'),

    path('liste/supprimer/<int:liste_id>/', swigo_views.supprimer_liste_de_courses, name='supprimer_liste_de_courses'),


    path('toggle_article_achete/<int:article_id>/', swigo_views.toggle_article_achete, name='toggle_article_achete'),




    path('get_salade_options/', swigo_views.get_salade_options, name='get_salade_options'),

    path('ajouter_salade_personnalisee/', swigo_views.ajouter_salade_personnalisee, name='ajouter_salade_personnalisee'),
    
    path('couscous/personaliser/', swigo_views.personnaliser_couscous, name='personnaliser_couscous'),
    
    path('couscous/ajouter-au-panier/<int:couscous_id>/', swigo_views.ajouter_au_panier_couscous, name='ajouter_au_panier_couscous'),

    path('get_couscous_options/', swigo_views.get_couscous_options, name='get_couscous_options'),

    path('api/commandes-a-emporter/', swigo_views.api_commandes_a_emporter, name='api_commandes_a_emporter'),

    path("ajouter_couscous_personnalise/", swigo_views.ajouter_couscous_personnalise, name="ajouter_couscous_personnalise"),


    path('commandes/<int:commande_id>/changer_mode/', swigo_views.changer_mode_livraison, name='changer_mode_livraison'),

    path('programmer-pick-up/', swigo_views.programmer_pick_up, name='programmer_pick_up'),
    
    path('retrait-sur-place/', swigo_views.choisir_retrait_sur_place, name='choisir_retrait_sur_place'),

    path('confirmer_commande/', swigo_views.confirmer_commande, name='confirmer_commande'),

    path('confirmation_commande/<int:commande_id>/', swigo_views.confirmation_commande, name='confirmation_commande'),

    path('api/commandes-a-valider/', swigo_views.api_commandes_a_valider, name='api_commandes_a_valider'),

    path('api/valider-commande/<int:commande_id>/', swigo_views.api_valider_commande, name='valider_commande'),
    
    path('generer-facture/<int:commande_id>/', swigo_views.generer_facture_view, name='generer_facture'),

    path("factures/<int:facture_id>/", swigo_views.facture_detail, name="facture_detail"),
    path('mentions-rgpd/', swigo_views.mentions_rgpd, name='mentions_rgpd'),

    path("plats_par_categorie_ajax/menu/", swigo_views.menus_par_categorie_ajax, name="menus_par_categorie_ajax"),
    path("ajouter_menu_personnalise/", swigo_views.ajouter_menu_personnalise, name="ajouter_menu_personnalise"),
    path('api/choix_menu/<int:menu_id>/', swigo_views.api_choix_menu, name='api_choix_menu'),
    path('menus_par_categorie_ajax/', swigo_views.menus_par_categorie_ajax, name='menus_par_categorie_ajax'),
    path("api/historique_commandes_client/<int:client_id>/", swigo_views.historique_commandes_client, name="api_historique_commandes_client"),


# Production
    path("production/ingredients-base/", swigo_views.assets_gestionnaire_stock, name="assets_gestionnaire_stock"),
    path("production/produits-transformes/", swigo_views.assets_produits_transformes, name="assets_produits_transformes"),
    path("production/recettes/", TemplateView.as_view(template_name="production/recettes.html"), name="assets_recettes"),
    path("production/ordres/", TemplateView.as_view(template_name="production/ordres.html"), name="assets_ordres_production"),
    path("production/suivi/", TemplateView.as_view(template_name="production/suivi.html"), name="assets_suivi_production"),


    path("api/produit-transforme/<int:produit_id>/out-of-stock/", swigo_views.produit_out_of_stock, name="produit_out_of_stock"),
# Production – recettes
    path("production/produit/<int:produit_id>/fiche-technique/", 
        swigo_views.fiche_technique, name="fiche_technique"),
    path("production/produit/<int:produit_id>/recette/", 
        swigo_views.recette_detail, name="recette_detail"),
    path("production/produit/<int:produit_id>/ordre-fabrication/", 
        swigo_views.ordre_fabrication, name="ordre_fabrication"),

    path('accompagnements_burger_ajax/', swigo_views.accompagnements_burger_ajax, name='accompagnements_burger_ajax'),

    path('burgers_par_type_ajax/<str:burger_type>/', swigo_views.burgers_par_type_ajax, name='burgers_par_type_ajax'),
    path('crousty_options_ajax/<int:plat_id>/', swigo_views.get_crousty_options_ajax, name='crousty_options_ajax'),


    path('ajouter_crousty_personnalise/', swigo_views.ajouter_crousty_personnalise, name='ajouter_crousty_personnalise'),

    path('poulet_options_ajax/<int:plat_id>/', swigo_views.get_poulet_options_ajax, name='poulet_options_ajax'),
    path('ajouter_poulet_personnalise/', swigo_views.ajouter_poulet_personnalise, name='ajouter_poulet_personnalise'),

    path('api/plats-par-categorie/', swigo_views.get_plats_par_categorie, name='plats_par_categorie'),
    path('api/plat/<int:plat_id>/', swigo_views.get_plat_detail, name='plat_detail'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
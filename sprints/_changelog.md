# Changelog inter-sprints

> Trace toute modification rétroactive (quand un sprint modifie un fichier/modèle créé par un sprint précédent).

| Date | Sprint source | Fichier/Modèle modifié (sprint d'origine) | Changement | Raison |
|------|--------------|-------------------------------------------|------------|--------|
| 2026-06-26 | sprint-02 | `core/models.py` (sprint 01) | Ajout modèle `City` (nom, tri par nom) | Les boutiques et produits nécessitent une localisation par ville |
| 2026-06-26 | sprint-02 | `accounts/models.py` (sprint 01) | Ajout FK `ville` (City) sur `Boutique` | Localisation obligatoire de la boutique |
| 2026-06-26 | sprint-03 | `catalog/views.py` (sprint 02) | Ajout `CategoryAttributesByIdView` (attributs par ID catégorie) | Chargement dynamique des champs EAV dans le formulaire SSR de dépôt |
| 2026-06-26 | sprint-03 | `catalog/urls.py` (sprint 02) | Ajout route `categories/<int:pk>/attributes-by-id/` | Endpoint nécessaire pour le JS du formulaire de dépôt |
| 2026-06-26 | sprint-03 | `accounts/models.py` (sprint 01) | Ajout méthodes `get_full_name()` et `get_short_name()` sur `User` | Nécessaires pour afficher le nom du vendeur dans les serializers produit |
| 2026-06-26 | sprint-04 | `catalog/views.py` (sprint 02) | Ajout `FilterableAttributesView` | Endpoint pour retourner les attributs filtrables d'une catégorie |
| 2026-06-26 | sprint-04 | `catalog/urls.py` (sprint 02) | Ajout route `categories/<slug>/filterable-attributes/` | Endpoint filterable-attributes nécessaire pour le frontend |
| 2026-06-26 | sprint-04 | `catalog/serializers.py` (sprint 02) | Ajout `FilterableAttributeSerializer` | Serializer dédié aux attributs filtrables (sans champs `required`/`filterable`) |
| 2026-06-26 | sprint-04 | `products/views.py` (sprint 03) | Refonte API `get()` avec filtres django-filter, EAV, search, boost ordering ; refonte SSR `ProductListView` avec filtres et contexte enrichi | Listing enrichi sprint 04 |
| 2026-06-26 | sprint-04 | `products/templates/products/product_list.html` (sprint 03) | Refonte complète : sidebar filtres, tags actifs, pagination avec query params, badge boosté | Page SSR listing enrichie |

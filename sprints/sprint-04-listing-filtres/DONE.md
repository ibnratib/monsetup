# Sprint 04 — Listing & Filtres — DONE

## Résumé

Enrichissement du listing des annonces avec filtres dynamiques EAV, tri, recherche textuelle, filtrage par ville/catégorie/prix, et amélioration de la page SSR listing avec barre de filtres visuelle.

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `products/filters.py` | `ProductFilter` — filtres django-filter (category, ville, prix, seller_type, is_boosted, status) |

## Fichiers modifiés

| Fichier | Changement |
|---------|-----------|
| `products/views.py` | Ajout filtres API (django-filter + EAV dynamique + search + boost ordering), refonte SSR `ProductListView` avec filtres et contexte enrichi |
| `catalog/views.py` | Ajout `FilterableAttributesView` — retourne les attributs filtrables d'une catégorie |
| `catalog/urls.py` | Ajout route `categories/<slug>/filterable-attributes/` |
| `catalog/serializers.py` | Ajout `FilterableAttributeSerializer` |
| `products/templates/products/product_list.html` | Refonte complète : sidebar filtres, tags actifs, pagination avec query params préservés, badge boosté, JS catégorie racine → sous-catégorie |

## Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/products/?category=&ville=&price_min=&price_max=&search=&ordering=&attr_<id>=` | Listing enrichi avec tous les filtres |
| GET | `/api/v1/catalog/categories/<slug>/filterable-attributes/` | Attributs filtrables d'une catégorie (nouveau) |

## Filtres supportés

### Filtres standards (django-filter)
- `category` — slug de la sous-catégorie
- `category_root` — slug de la catégorie racine
- `ville` — ID de la ville
- `status` — statut de l'annonce (défaut : DISPONIBLE)
- `price_min` / `price_max` — fourchette de prix
- `seller_type` — type de vendeur (particulier/boutique)
- `is_boosted` — annonces boostées

### Recherche textuelle
- `search` — recherche icontains sur `title` + `description_complementaire`

### Filtres EAV dynamiques
- `attr_<id>=<value>` — filtre par attribut EAV (INT, DECIMAL, BOOLEAN, CHOICE, MULTI_CHOICE, TEXT_SHORT)
- Seuls les attributs `filterable=True` sont pris en compte

### Tri
- `ordering` — `created_at`, `-created_at`, `price`, `-price`
- Annonces boostées (is_boosted=True + boost_expires_at > now) toujours en premier

## Page SSR `/annonces/`
- Barre latérale de filtres (responsive)
- Dropdown catégorie racine → sous-catégorie (JS dynamique)
- Dropdown ville, champs prix min/max, recherche texte
- Filtres EAV dynamiques si sous-catégorie sélectionnée
- Tri (plus récent, prix croissant, prix décroissant)
- Tags de filtres actifs cliquables pour retirer
- Pagination avec query params préservés
- Badge "Boosté" sur les annonces boostées

## Definition of Done

- [x] `GET /api/v1/products/?category=gaming&price_min=1000` filtre correctement
- [x] `GET /api/v1/products/?search=macbook` retourne les annonces avec "macbook" dans le titre ou description
- [x] `GET /api/v1/products/?attr_5=16` filtre par attribut EAV
- [x] `GET /api/v1/products/?ordering=-price` trie par prix décroissant
- [x] Annonces boostées en premier dans le listing
- [x] `GET /api/v1/catalog/categories/<slug>/filterable-attributes/` retourne les attributs filtrables
- [x] Page SSR `/annonces/` affiche la barre de filtres fonctionnelle
- [x] Les filtres sont préservés dans la pagination
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

# Sprint 04 — Listing & Filtres

## Objectif

Enrichir le listing des annonces avec des filtres dynamiques EAV, tri, recherche textuelle, filtrage par ville/catégorie/prix, et améliorer la page SSR listing avec les filtres visuels.

## Pré-requis

- Sprint 03 complété (`Product`, `ProductImage`, `ProductAttributeValue`, listing basique, pages SSR)
- Le listing actuel (`GET /api/v1/products/` et `/annonces/`) ne supporte que le tri par date et la pagination

## Livrables

### Aucune nouvelle app — modifications sur `products`

### Filtres API

Ajouter `ProductFilter` dans `products/filters.py` avec `django-filter` :

| Filtre | Champ | Type | Exemple |
|--------|-------|------|---------|
| `category` | `category__slug` | exact | `?category=gaming` |
| `category_root` | `category__parent__slug` | exact | `?category_root=pc-portables` |
| `ville` | `ville__id` | exact | `?ville=1` |
| `status` | `status` | exact | `?status=DISPONIBLE` (par défaut dans listing public) |
| `price_min` | `price` | gte | `?price_min=500` |
| `price_max` | `price` | lte | `?price_max=5000` |
| `seller_type` | `seller__user_type` | exact | `?seller_type=boutique` |
| `is_boosted` | `is_boosted` | exact | `?is_boosted=true` |
| `search` | `title`, `description_complementaire` | icontains (SearchFilter) | `?search=macbook` |

### Filtres EAV dynamiques

En plus des filtres ci-dessus, supporter le filtrage par attributs EAV sur les attributs où `filterable=True` :

```
GET /api/v1/products/?attr_<attribute_id>=<value>
```

Exemples :
- `?attr_5=16` → RAM = 16 (INT)
- `?attr_7=42` → GPU = choix avec id 42 (CHOICE)
- `?attr_9=true` → SSD inclus = true (BOOLEAN)

Implémentation :
- Surcharger `get_queryset()` dans la vue de listing
- Pour chaque paramètre `attr_<id>` dans `request.query_params` :
  1. Vérifier que l'AttributeDefinition existe et est `filterable=True`
  2. Filtrer les `Product` ayant un `ProductAttributeValue` correspondant
  3. Utiliser le bon champ (`value_int`, `value_choice_id`, etc.) selon le type

### Tri

| Paramètre | Champs | Exemple |
|-----------|--------|---------|
| `ordering` | `created_at`, `-created_at`, `price`, `-price` | `?ordering=-price` |

Défaut : `-created_at` (plus récent en premier).

Les annonces boostées (`is_boosted=True` et `boost_expires_at` > now) apparaissent **en premier**, avant le tri normal.

### Endpoints API modifiés

| Méthode | URL | Changement |
|---------|-----|-----------|
| GET | `/api/v1/products/` | Ajout filtres, tri, recherche, EAV dynamique |
| GET | `/api/v1/catalog/categories/<slug>/filterable-attributes/` | **Nouveau** — retourne les AttributeDefinition filtrables (avec choices) pour une catégorie (utile pour le frontend pour construire le formulaire de filtres) |

### Serializers

| Nom | Usage |
|-----|-------|
| `FilterableAttributeSerializer` | Expose les attributs filtrables d'une catégorie avec leurs choices (pour construire le formulaire de filtres côté frontend) |

### Pages SSR modifiées

#### `/annonces/` — Page listing enrichie

Ajouter au template `product_list.html` :
- **Barre latérale de filtres** (ou section en haut sur mobile) :
  - Dropdown catégorie racine → sous-catégorie
  - Dropdown ville
  - Champs prix min / prix max
  - Champ de recherche texte (titre)
  - Filtres EAV dynamiques : quand une sous-catégorie est sélectionnée, afficher les attributs filtrables de cette catégorie (chargés via un appel API ou passés dans le contexte)
- **Tri** : dropdown "Plus récent", "Prix croissant", "Prix décroissant"
- Les filtres appliqués s'affichent comme des "tags" cliquables pour les retirer
- La pagination reste fonctionnelle avec les filtres actifs (query params préservés)

#### Vue SSR `ProductListView` modifiée

```python
# Accepter les query params de filtre dans la vue SSR
# Réutiliser la même logique de filtrage que l'API
# Passer les catégories, villes et filtres actifs dans le contexte du template
```

### Fichiers à créer / modifier

```
products/
├── filters.py              (CRÉER — ProductFilter)
├── views.py                (MODIFIER — ajouter filtres dans API + SSR)
├── urls.py                 (MODIFIER si nouvel endpoint)
├── templates/products/
│   └── product_list.html   (MODIFIER — ajouter sidebar filtres)
catalog/
├── views.py                (MODIFIER — ajouter FilterableAttributesView)
├── urls.py                 (MODIFIER — ajouter endpoint filterable-attributes)
├── serializers.py          (MODIFIER — ajouter FilterableAttributeSerializer si différent)
```

## Validations métier

- Le listing public ne montre que les annonces `status=DISPONIBLE` par défaut (sauf si un filtre `status` explicite est passé par un admin).
- Les filtres EAV ne s'appliquent que sur les attributs `filterable=True` — ignorer silencieusement les autres.
- `price_min` et `price_max` doivent être des nombres positifs — ignorer si invalides.
- La recherche textuelle est case-insensitive et porte sur `title` + `description_complementaire`.
- Les annonces boostées apparaissent en premier dans le listing (avant le tri utilisateur).

## Contrat de sortie (Definition of Done)

- [ ] `GET /api/v1/products/?category=gaming&price_min=1000` filtre correctement
- [ ] `GET /api/v1/products/?search=macbook` retourne les annonces avec "macbook" dans le titre ou description
- [ ] `GET /api/v1/products/?attr_5=16` filtre par attribut EAV
- [ ] `GET /api/v1/products/?ordering=-price` trie par prix décroissant
- [ ] Annonces boostées en premier dans le listing
- [ ] `GET /api/v1/catalog/categories/<slug>/filterable-attributes/` retourne les attributs filtrables
- [ ] Page SSR `/annonces/` affiche la barre de filtres fonctionnelle
- [ ] Les filtres sont préservés dans la pagination
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

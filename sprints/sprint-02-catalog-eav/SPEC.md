# Sprint 02 — Catalogue EAV + Localisation

## Objectif

Mettre en place le système EAV hiérarchique (catégories, attributs, choix) et le modèle `City` pour la localisation. Ajouter la FK `ville` sur `Boutique` (modification rétroactive sprint 01).

## Pré-requis

- Sprint 01 complété (User, Particulier, Boutique, core, DRF configuré)
- Lire `_changelog.md` pour les modifications rétroactives à appliquer

## Modifications rétroactives (sprint 01)

> Ces changements touchent des fichiers du sprint 01. Les appliquer EN PREMIER.

| Fichier | Changement |
|---------|-----------|
| `core/models.py` | Ajouter le modèle `City` |
| `core/admin.py` | Enregistrer `City` dans l'admin |
| `accounts/models.py` | Ajouter FK `ville` (City, obligatoire) sur `Boutique` |
| `accounts/serializers.py` | Ajouter `ville` dans `BoutiqueSerializer` et `RegisterBoutiqueSerializer` |

## Livrables

### Apps à créer

| App | Rôle |
|-----|------|
| `catalog` | Catégories, AttributeDefinition, AttributeChoice |

### Modèles

#### `core` app (ajout)

| Modèle | Champs | Notes |
|--------|--------|-------|
| `City` | `name` (unique, max 100), `ordering: ['name']` | Triée par nom. Administrable via Django Admin. Pas hardcodée. |

#### `accounts` app (modification)

| Modèle | Changement |
|--------|-----------|
| `Boutique` | Ajouter `ville = ForeignKey(City, on_delete=PROTECT, related_name='boutiques')` — obligatoire |

#### `catalog` app (nouveau)

| Modèle | Champs | Notes |
|--------|--------|-------|
| `Category` | `name`, `slug` (unique), `parent` (FK self, nullable), `icon` (optionnel), `order` (PositiveIntegerField, pour le tri) | 2 niveaux max : racine (parent=null) → sous-catégorie |
| `AttributeDefinition` | `category` (FK Category), `name`, `label_fr` (label affiché), `attribute_type` (CHOICE: `INT`, `DECIMAL`, `CHOICE`, `MULTI_CHOICE`, `BOOLEAN`, `TEXT_SHORT`), `required` (bool), `filterable` (bool), `min_value` (nullable), `max_value` (nullable), `order` (tri d'affichage), `unit` (optionnel, ex: "Go", "GHz") | Attaché à une catégorie (racine ou sous-catégorie) |
| `AttributeChoice` | `attribute` (FK AttributeDefinition), `value`, `order` | Valeurs autorisées pour CHOICE/MULTI_CHOICE. Triées par `order`. |

### Méthode métier critique

```python
# Sur le modèle Category
def get_inherited_attributes(self):
    """
    Retourne tous les AttributeDefinition applicables à cette catégorie :
    - Si c'est une sous-catégorie : attributs de la catégorie racine (parent) + attributs propres
    - Si c'est une catégorie racine : uniquement ses attributs propres
    - Pas de doublons, triés par `order`
    """
```

### Endpoints API

| Méthode | URL | Permission | Response |
|---------|-----|------------|----------|
| GET | `/api/v1/catalog/categories/` | AllowAny | Liste des catégories racines avec sous-catégories imbriquées |
| GET | `/api/v1/catalog/categories/<slug>/` | AllowAny | Détail d'une catégorie + ses attributs hérités |
| GET | `/api/v1/catalog/categories/<slug>/attributes/` | AllowAny | Liste des AttributeDefinition (avec héritage) + leurs choices |
| GET | `/api/v1/cities/` | AllowAny | Liste des villes (triées par nom) |

### Serializers

| Nom | Modèle | Champs |
|-----|--------|--------|
| `CitySerializer` | City | `id`, `name` |
| `CategoryListSerializer` | Category | `id`, `name`, `slug`, `icon`, `children` (sous-catégories) |
| `CategoryDetailSerializer` | Category | `id`, `name`, `slug`, `icon`, `parent`, `attributes` (via get_inherited_attributes) |
| `AttributeDefinitionSerializer` | AttributeDefinition | `id`, `name`, `label_fr`, `attribute_type`, `required`, `filterable`, `min_value`, `max_value`, `unit`, `choices` |
| `AttributeChoiceSerializer` | AttributeChoice | `id`, `value` |

### Admin Django

- `City` : list_display = (name,), search
- `Category` : list_display = (name, parent, order), list_filter = (parent,), prepopulated slug
- `AttributeDefinition` : list_display = (name, category, attribute_type, required, filterable), list_filter = (category, attribute_type)
- `AttributeChoice` : list_display = (attribute, value, order), list_filter = (attribute,)
- Inline `AttributeChoice` dans `AttributeDefinition` admin
- Inline `AttributeDefinition` dans `Category` admin

### Settings à modifier

```python
INSTALLED_APPS += [
    'catalog',
]
```

### URLs à ajouter

```python
# monsetup/urls.py
path('api/v1/catalog/', include('catalog.urls')),
path('api/v1/cities/', CityListView.as_view(), name='city-list'),  # ou dans core/urls.py
```

### Fichiers à créer

```
catalog/
├── __init__.py
├── models.py            (Category, AttributeDefinition, AttributeChoice)
├── serializers.py
├── views.py
├── urls.py
├── admin.py
└── migrations/
```

## Validations métier

- Une catégorie ne peut avoir qu'**un seul niveau de parent** (pas de catégorie → sous-catégorie → sous-sous-catégorie). Valider dans `Category.clean()`.
- `AttributeChoice` ne peut exister que pour les types `CHOICE` / `MULTI_CHOICE`.
- `min_value` / `max_value` ne sont pertinents que pour les types `INT` / `DECIMAL`.
- `get_inherited_attributes()` ne doit **jamais** retourner de doublons (même si un attribut du même nom existe au deux niveaux).
- Le slug de Category est unique et auto-généré depuis `name`.
- `City.name` est unique (pas de doublons de villes).

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] `GET /api/v1/catalog/categories/` retourne les catégories avec sous-catégories imbriquées
- [ ] `GET /api/v1/catalog/categories/<slug>/attributes/` retourne les attributs hérités correctement
- [ ] `GET /api/v1/cities/` retourne les villes triées par nom
- [ ] `Boutique` a maintenant un champ `ville` (FK City)
- [ ] Admin Django : City, Category, AttributeDefinition, AttributeChoice administrables
- [ ] Inline choices dans l'admin AttributeDefinition
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

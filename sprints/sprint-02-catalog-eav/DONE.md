# Sprint 02 — DONE

## Résumé

Mise en place du système EAV hiérarchique (catégories, attributs, choix) et du modèle `City` pour la localisation. Ajout de la FK `ville` sur `Boutique` (modification rétroactive sprint 01).

## Modifications rétroactives appliquées

| Fichier | Changement |
|---------|-----------|
| `core/models.py` | Ajout modèle `City` (name unique, ordering par nom) |
| `core/admin.py` | Enregistrement `City` dans l'admin (list_display, search) |
| `accounts/models.py` | Ajout FK `ville` (City, PROTECT) sur `Boutique` |
| `accounts/serializers.py` | Ajout `ville` dans `BoutiqueSerializer` et `RegisterBoutiqueSerializer` |

## App créée

| App | Fichiers |
|-----|----------|
| `catalog` | `__init__.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `migrations/` |

## Modèles créés / modifiés

| Modèle | App | Action |
|--------|-----|--------|
| `City` | core | Créé — `name` (unique, max 100), ordering `['name']` |
| `Boutique` | accounts | Modifié — ajout FK `ville` (City, obligatoire) |
| `Category` | catalog | Créé — `name`, `slug`, `parent` (FK self), `icon`, `order` |
| `AttributeDefinition` | catalog | Créé — `category` (FK), `name`, `label_fr`, `attribute_type`, `required`, `filterable`, `min_value`, `max_value`, `order`, `unit` |
| `AttributeChoice` | catalog | Créé — `attribute` (FK), `value`, `order` |

## Endpoints API ajoutés

| Méthode | URL | Permission |
|---------|-----|------------|
| GET | `/api/v1/catalog/categories/` | AllowAny |
| GET | `/api/v1/catalog/categories/<slug>/` | AllowAny |
| GET | `/api/v1/catalog/categories/<slug>/attributes/` | AllowAny |
| GET | `/api/v1/cities/` | AllowAny |

## Validations métier implémentées

- `Category.clean()` : empêche plus d'un niveau de parent (max 2 niveaux)
- `AttributeDefinition.clean()` : `min_value`/`max_value` uniquement pour INT/DECIMAL
- `AttributeChoice.clean()` : choix uniquement pour CHOICE/MULTI_CHOICE
- `Category.get_inherited_attributes()` : héritage parent → enfant sans doublons, trié par `order`
- `City.name` unique
- `Category.slug` auto-généré et unique

## Admin Django

- `City` : list_display, search_fields
- `Category` : list_display, list_filter, prepopulated slug, inline `AttributeDefinition`
- `AttributeDefinition` : list_display, list_filter, inline `AttributeChoice`
- `AttributeChoice` : list_display, list_filter

## Migrations

| App | Migration |
|-----|-----------|
| core | `0001_initial` (City) |
| accounts | `0002_boutique_ville` |
| catalog | `0001_initial` (Category, AttributeDefinition, AttributeChoice) |

## Contrat de sortie

- [x] `python manage.py migrate` fonctionne sans erreur
- [x] `GET /api/v1/catalog/categories/` retourne les catégories avec sous-catégories imbriquées
- [x] `GET /api/v1/catalog/categories/<slug>/attributes/` retourne les attributs hérités correctement
- [x] `GET /api/v1/cities/` retourne les villes triées par nom
- [x] `Boutique` a maintenant un champ `ville` (FK City)
- [x] Admin Django : City, Category, AttributeDefinition, AttributeChoice administrables
- [x] Inline choices dans l'admin AttributeDefinition
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

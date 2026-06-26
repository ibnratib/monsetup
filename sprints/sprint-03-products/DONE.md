# Sprint 03 — Produits (annonces) + Images — DONE

## Résumé

App `products` créée avec les modèles Product, ProductImage et ProductAttributeValue. CRUD API complet, compression d'images automatique via Pillow, validation EAV dynamique, et pages SSR avec Tailwind CSS (CDN).

## Livrables réalisés

### App créée

- `products` — Product, ProductImage, ProductAttributeValue, CRUD annonces, pages SSR

### Modèles

- `Product` — annonce avec seller, category (sous-catégorie), title, price, ville, status, boost, compteurs
- `ProductImage` — images avec compression auto si > MAX_IMAGE_SIZE_MB (2 MB), max 8 par annonce
- `ProductAttributeValue` — valeurs EAV polymorphes (int, decimal, boolean, text, choice, multi_choice), unique (product, attribute)

### Endpoints API

| Méthode | URL | Permission |
|---------|-----|------------|
| POST | `/api/v1/products/` | IsAuthenticated |
| GET | `/api/v1/products/` | AllowAny |
| GET | `/api/v1/products/<id>/` | AllowAny |
| PATCH | `/api/v1/products/<id>/` | IsProductOwner |
| DELETE | `/api/v1/products/<id>/` | IsProductOwner |
| GET | `/api/v1/catalog/categories/<id>/attributes-by-id/` | AllowAny |

### Pages SSR

| URL | Template | Description |
|-----|----------|-------------|
| `/annonces/` | `product_list.html` | Listing paginé des annonces disponibles |
| `/annonces/<id>/` | `product_detail.html` | Détail annonce avec carrousel images, attributs EAV, bouton WhatsApp |
| `/annonces/deposer/` | `product_create.html` | Formulaire de dépôt avec champs EAV dynamiques |

### Serializers

- `ProductImageSerializer` — lecture images
- `ProductListSerializer` — listing avec thumbnail, seller_type, seller_name
- `ProductDetailSerializer` — détail complet avec images, attributs, vendeur, whatsapp_url
- `DynamicProductCreateSerializer` — création/édition avec validation EAV dynamique
- `AttributeValueReadSerializer` — lecture des valeurs d'attributs avec label_fr et display_value
- `SellerPublicSerializer` — infos publiques du vendeur

### Permissions

- `IsProductOwner` — `request.user == obj.seller` (lecture autorisée pour tous)

### Admin

- `ProductAdmin` — list_display, list_filter, search_fields, inlines (ProductImage, ProductAttributeValue)

### Templates

- `base.html` — template de base avec Tailwind CSS (CDN), header, footer, responsive
- 3 templates produits (list, detail, create)

## Validations métier implémentées

- [x] `category` doit être une sous-catégorie (parent non null)
- [x] Nombre d'images ≤ MAX_IMAGES_PER_PRODUCT (8)
- [x] `description_complementaire` ≤ MAX_DESCRIPTION_LENGTH (300 caractères)
- [x] `price` > 0
- [x] Limite d'annonces actives pour Particuliers (max_active_ads)
- [x] Pas de limite pour les Boutiques
- [x] Validation EAV complète (types, min/max, choices valides, required)
- [x] `is_boosted` / `boost_expires_at` en lecture seule pour le vendeur
- [x] Compression d'images automatique (> 2 MB → JPEG 85%, max 1920px)

## Contrat de sortie

- [x] `python manage.py migrate` fonctionne sans erreur
- [x] `POST /api/v1/products/` crée une annonce avec images et attributs EAV validés
- [x] `GET /api/v1/products/` retourne la liste paginée
- [x] `GET /api/v1/products/<id>/` retourne le détail complet (images, attributs, vendeur, WhatsApp URL)
- [x] Compression d'images fonctionnelle (> MAX_IMAGE_SIZE_MB → compressée)
- [x] Limite d'annonces actives appliquée pour les Particuliers
- [x] Validation EAV complète (types, min/max, choices, required)
- [x] `is_boosted` / `boost_expires_at` en lecture seule pour le vendeur
- [x] Pages SSR : `/annonces/`, `/annonces/<id>/`, `/annonces/deposer/` fonctionnelles
- [x] Template `base.html` avec Tailwind CSS (CDN)
- [x] Admin Django : Product avec inlines images et attributs
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

## Fichiers créés/modifiés

### Créés
- `products/__init__.py`
- `products/models.py`
- `products/serializers.py`
- `products/views.py`
- `products/urls.py`
- `products/permissions.py`
- `products/admin.py`
- `products/utils.py`
- `products/migrations/0001_initial.py`
- `products/templates/products/product_list.html`
- `products/templates/products/product_detail.html`
- `products/templates/products/product_create.html`
- `templates/base.html`

### Modifiés
- `monsetup/settings.py` — ajout `products` dans INSTALLED_APPS, DIRS templates
- `monsetup/urls.py` — ajout API products + SSR annonces + MEDIA serving en debug
- `catalog/views.py` — ajout `CategoryAttributesByIdView`
- `catalog/urls.py` — ajout route `categories/<id>/attributes-by-id/`

# Sprint 03 — Produits (annonces) + Images

## Objectif

Créer le système d'annonces : modèle `Product`, upload d'images avec compression automatique, valeurs d'attributs EAV (`ProductAttributeValue`), serializer dynamique, et les endpoints CRUD pour gérer les annonces.

## Pré-requis

- Sprint 01 complété (User, Particulier, Boutique)
- Sprint 02 complété (City, Category, AttributeDefinition, AttributeChoice, `get_inherited_attributes()`)

## Livrables

### App à créer

| App | Rôle |
|-----|------|
| `products` | Product, ProductImage, ProductAttributeValue, CRUD annonces |

### Modèles

#### `products` app

| Modèle | Champs | Notes |
|--------|--------|-------|
| `Product` | `seller` (FK User), `category` (FK Category — sous-catégorie uniquement), `title` (max 150), `description_complementaire` (max `MAX_DESCRIPTION_LENGTH`, optionnel), `price` (DecimalField max_digits=10, decimal_places=2, en DH), `ville` (FK City, obligatoire), `adresse` (TextField, optionnel), `status` (CHOICE: `DISPONIBLE` / `VENDU` / `ARCHIVE`, default `DISPONIBLE`), `is_boosted` (bool, default False), `boost_expires_at` (DateTimeField, nullable), `views_count` (PositiveIntegerField, default 0), `whatsapp_clicks_count` (PositiveIntegerField, default 0) | Hérite de `TimeStampedModel`. Le champ `category` doit pointer vers une **sous-catégorie** (pas une racine). |
| `ProductImage` | `product` (FK Product, related_name='images'), `image` (ImageField upload_to='products/'), `order` (PositiveIntegerField, default 0) | Max `MAX_IMAGES_PER_PRODUCT` images par produit. La première (order=0) est le thumbnail. Compression auto si > `MAX_IMAGE_SIZE_MB`. |
| `ProductAttributeValue` | `product` (FK Product, related_name='attribute_values'), `attribute` (FK AttributeDefinition), `value_int` (nullable), `value_decimal` (nullable), `value_boolean` (nullable), `value_text` (nullable), `value_choice` (FK AttributeChoice, nullable), `value_multi_choice` (M2M AttributeChoice, blank) | Unique ensemble (product, attribute). Un seul champ `value_*` rempli selon le type de l'attribut. |

### Compression d'images

```python
# Dans ProductImage.save() ou un signal post_save
# Si l'image dépasse MAX_IMAGE_SIZE_MB :
# 1. Ouvrir avec Pillow
# 2. Redimensionner (max 1920px côté le plus long)
# 3. Sauvegarder en JPEG qualité 85%
# Utiliser Pillow (déjà dans requirements.txt)
```

### Serializers

| Nom | Usage | Champs |
|-----|-------|--------|
| `ProductImageSerializer` | Read | `id`, `image` (URL complète), `order` |
| `ProductListSerializer` | Listing | `id`, `title`, `price`, `status`, `ville` (nom), `category` (nom+slug), `thumbnail` (URL première image), `seller_type` (particulier/boutique), `seller_name`, `is_boosted`, `created_at` |
| `ProductDetailSerializer` | Détail | Tous les champs + `images` (nested), `attribute_values` (nested, avec label_fr et valeur formatée), `seller` (infos publiques), `whatsapp_url` |
| `DynamicProductCreateSerializer` | Création/édition | `title`, `description_complementaire`, `price`, `category`, `ville`, `adresse`, `images` (upload multiple), `attributes` (dict dynamique validé contre `get_inherited_attributes()`) |

### DynamicProductCreateSerializer — Logique critique

```python
class DynamicProductCreateSerializer(serializers.Serializer):
    """
    Serializer générique pour créer/modifier une annonce.
    Les attributs EAV sont validés dynamiquement selon la catégorie choisie.
    
    Le champ `attributes` est un dict : { attribute_id: value }
    Exemple : { "12": 16, "13": "choice_id_45", "14": true }
    
    Validation :
    1. Vérifier que la catégorie est une sous-catégorie (pas une racine)
    2. Récupérer get_inherited_attributes() de la catégorie
    3. Pour chaque attribut required=True, vérifier qu'il est présent dans le dict
    4. Pour chaque valeur soumise :
       - INT : vérifier int, min_value/max_value
       - DECIMAL : vérifier decimal, min_value/max_value
       - BOOLEAN : vérifier bool
       - TEXT_SHORT : vérifier string, max 255 chars
       - CHOICE : vérifier que value_choice est un AttributeChoice existant pour cet attribut
       - MULTI_CHOICE : vérifier que toutes les valeurs sont des AttributeChoice existants
    5. Rejeter tout attribut_id qui n'appartient pas à la catégorie
    """
```

### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| POST | `/api/v1/products/` | IsAuthenticated | Créer une annonce (multipart/form-data pour images) |
| GET | `/api/v1/products/` | AllowAny | Lister les annonces (voir sprint 04 pour filtres avancés, ici tri par date + pagination basique) |
| GET | `/api/v1/products/<id>/` | AllowAny | Détail d'une annonce (incrémente `views_count`) |
| PATCH | `/api/v1/products/<id>/` | IsOwner | Modifier son annonce |
| DELETE | `/api/v1/products/<id>/` | IsOwner | Supprimer son annonce |

### Permissions custom

| Nom | Logique |
|-----|---------|
| `IsProductOwner` | `request.user == obj.seller` — le vendeur ne peut modifier/supprimer que ses propres annonces |

### Validations métier

- `category` doit être une **sous-catégorie** (parent non null). Interdire la publication sur une catégorie racine.
- Le nombre d'images ne peut pas dépasser `MAX_IMAGES_PER_PRODUCT` (settings).
- `description_complementaire` : max `MAX_DESCRIPTION_LENGTH` caractères.
- `price` : doit être > 0.
- `status` : seul le vendeur peut changer le statut de ses propres annonces.
- **Limite d'annonces actives** pour les Particuliers : si `Particulier.max_active_ads` est atteint (annonces avec status=DISPONIBLE), rejeter la création avec erreur en français.
- Pas de limite d'annonces pour les Boutiques.
- Les valeurs EAV sont validées côté serveur contre les `AttributeDefinition` (types, min/max, choices valides).
- Un attribut `required=True` non rempli → erreur de validation.
- Un attribut CHOICE/MULTI_CHOICE avec une valeur qui n'existe pas dans `AttributeChoice` → rejet.
- `is_boosted` et `boost_expires_at` : en lecture seule pour le vendeur (seul l'admin peut modifier).

### Admin Django

- `Product` : list_display = (title, seller, category, ville, status, price, is_boosted, created_at), list_filter = (status, category, ville, is_boosted), search = (title, seller__email)
- `ProductImage` : inline dans Product admin
- `ProductAttributeValue` : inline dans Product admin (read-only ou minimal)

### Settings à modifier

```python
INSTALLED_APPS += [
    'products',
]
```

### URLs à ajouter

```python
# monsetup/urls.py
path('api/v1/products/', include('products.urls')),
```

### Fichiers à créer

```
products/
├── __init__.py
├── models.py            (Product, ProductImage, ProductAttributeValue)
├── serializers.py       (DynamicProductCreateSerializer, ProductListSerializer, etc.)
├── views.py
├── urls.py
├── permissions.py       (IsProductOwner)
├── admin.py
├── utils.py             (compress_image)
└── migrations/
```

### Templates Django (pages SSR)

> Ce sprint introduit les premières pages web visibles.

| Template | URL | Description |
|----------|-----|-------------|
| `products/product_list.html` | `/annonces/` | Page listing des annonces avec pagination. Affiche thumbnail, titre, prix, ville, statut. Tri par date (plus récent). |
| `products/product_detail.html` | `/annonces/<id>/` | Fiche détaillée d'une annonce : images (carrousel basique), attributs EAV formatés, prix, ville, bouton WhatsApp, infos vendeur. |
| `products/product_create.html` | `/annonces/deposer/` | Formulaire de dépôt d'annonce. Sélection catégorie → chargement dynamique des champs EAV. Upload images. |
| `base.html` | — | Template de base : header (logo, navigation), footer. Responsive. |

#### Vues SSR

| Vue | URL | Description |
|-----|-----|-------------|
| `ProductListView` | `/annonces/` | Rendu SSR de la liste (consomme le même queryset que l'API) |
| `ProductDetailView` | `/annonces/<id>/` | Rendu SSR du détail (incrémente views_count) |
| `ProductCreateView` | `/annonces/deposer/` | Formulaire de création (requiert auth) |

#### Notes CSS

- Utiliser **Tailwind CSS** (CDN pour le MVP, build plus tard).
- Le `base.html` inclut le CDN Tailwind et une structure responsive basique.
- Pas besoin d'un design parfait — fonctionnel et propre.

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] `POST /api/v1/products/` crée une annonce avec images et attributs EAV validés
- [ ] `GET /api/v1/products/` retourne la liste paginée
- [ ] `GET /api/v1/products/<id>/` retourne le détail complet (images, attributs, vendeur, WhatsApp URL)
- [ ] Compression d'images fonctionnelle (> MAX_IMAGE_SIZE_MB → compressée)
- [ ] Limite d'annonces actives appliquée pour les Particuliers
- [ ] Validation EAV complète (types, min/max, choices, required)
- [ ] `is_boosted` / `boost_expires_at` en lecture seule pour le vendeur
- [ ] Pages SSR : `/annonces/`, `/annonces/<id>/`, `/annonces/deposer/` fonctionnelles
- [ ] Template `base.html` avec Tailwind CSS (CDN)
- [ ] Admin Django : Product avec inlines images et attributs
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

# Registre du projet — État vivant

> Ce fichier est mis à jour après chaque sprint. L'IA doit le lire en premier avant d'implémenter.

## Apps Django créées

| App | Rôle | Sprint |
|-----|------|--------|
| `core` | Utilitaires partagés, base models (TimeStampedModel), City, HomePageView, template filters (format_price, time_since_fr) | 01, 02, 08, 09 |
| `accounts` | Custom User, Particulier, Boutique, authentification JWT + SSR (inscription/connexion/déconnexion), page boutique | 01, 02, 06, 08 |
| `catalog` | Catégories, AttributeDefinition, AttributeChoice | 02, 04 |
| `products` | Product, ProductImage, ProductAttributeValue, Favorite, Report, ProductView, ProductWhatsAppClick, CRUD annonces, pages SSR, filtres & listing, boost admin actions, expire_boosts command | 03, 04, 06, 08 |
| `dashboard` | Dashboard vendeur : mes annonces, stats, changement statut, notifications, rappel 30j, favoris | 05, 06 |
| `reviews` | Avis vendeurs : Review, ReviewReply, ReviewTag, signalement d'avis | 07 |

## Modèles existants

| Modèle | App | Champs principaux | Notes |
|--------|-----|-------------------|-------|
| `TimeStampedModel` | core | `created_at`, `updated_at` | Abstract |
| `City` | core | `name` (unique, max 100) | Triée par nom. Sprint 02 |
| `User` | accounts | `email` (login), `phone_whatsapp`, `first_name`, `last_name`, `user_type`, `is_active`, `is_staff`, `date_joined` | Custom User (email-based) |
| `Particulier` | accounts | `user` (OneToOne), `max_active_ads` | Profil C2C |
| `Boutique` | accounts | `user` (OneToOne), `nom_boutique`, `slug`, `description`, `adresse`, `ville` (FK City), `statut_verification`, `logo` | Profil B2C. `ville` ajouté sprint 02 |
| `Category` | catalog | `name`, `slug` (unique), `parent` (FK self, nullable), `icon`, `order` | 2 niveaux max. Sprint 02 |
| `AttributeDefinition` | catalog | `category` (FK Category), `name`, `label_fr`, `attribute_type`, `required`, `filterable`, `min_value`, `max_value`, `order`, `unit` | Types: INT, DECIMAL, CHOICE, MULTI_CHOICE, BOOLEAN, TEXT_SHORT. Sprint 02 |
| `AttributeChoice` | catalog | `attribute` (FK AttributeDefinition), `value`, `order` | Pour CHOICE/MULTI_CHOICE uniquement. Sprint 02 |
| `Product` | products | `seller` (FK User), `category` (FK Category), `title`, `description_complementaire`, `price`, `ville` (FK City), `adresse`, `status`, `is_boosted`, `boost_expires_at`, `views_count`, `whatsapp_clicks_count` | Hérite de TimeStampedModel. Catégorie = sous-catégorie uniquement. Sprint 03 |
| `ProductImage` | products | `product` (FK Product), `image` (ImageField), `order` | Max 8 images. Compression auto > 2 MB. Sprint 03 |
| `ProductAttributeValue` | products | `product` (FK Product), `attribute` (FK AttributeDefinition), `value_int`, `value_decimal`, `value_boolean`, `value_text`, `value_choice` (FK), `value_multi_choice` (M2M) | Unique (product, attribute). Sprint 03 |
| `Notification` | dashboard | `user` (FK User), `type` (CHOICE: RAPPEL_DISPONIBILITE, SIGNALEMENT_RECU, ANNONCE_EXPIREE), `message` (TextField), `product` (FK Product, nullable), `is_read` (bool, default False) | Hérite de TimeStampedModel. Sprint 05 |
| `Favorite` | products | `user` (FK User), `product` (FK Product) | Hérite de TimeStampedModel. Unique (user, product). Sprint 06 |
| `Report` | products | `reporter` (FK User), `product` (FK Product), `reason` (CHOICE), `comment` (TextField, max 500), `status` (CHOICE: EN_ATTENTE/TRAITEE/REJETEE) | Hérite de TimeStampedModel. Unique (reporter, product). Sprint 06 |
| `ProductView` | products | `product` (FK Product), `session_key` (CharField), `ip_address` (GenericIPAddressField), `created_at` (auto) | Déduplication par session. Sprint 06 |
| `ProductWhatsAppClick` | products | `product` (FK Product), `user` (FK User, nullable), `created_at` (auto) | Tracking clics WhatsApp. Sprint 06 |
| `ReviewTag` | reviews | `label` (CharField, unique, max 50) | Tags prédéfinis administrables. Sprint 07 |
| `Review` | reviews | `reviewer` (FK User), `seller` (FK User, related_name='received_reviews'), `rating` (1-5), `comment` (TextField, max 500, optionnel), `tags` (M2M ReviewTag) | Hérite de TimeStampedModel. Unique (reviewer, seller). Sprint 07 |
| `ReviewReply` | reviews | `review` (OneToOne Review), `text` (TextField, max 300) | Hérite de TimeStampedModel. Sprint 07 |
| `ReviewReport` | reviews | `reporter` (FK User), `review` (FK Review), `reason` (CHOICE), `comment` (TextField, max 500), `status` (CHOICE: EN_ATTENTE/TRAITEE/REJETEE) | Hérite de TimeStampedModel. Unique (reporter, review). Sprint 07 |

## Endpoints API actifs

| Méthode | URL | Permission | Sprint |
|---------|-----|------------|--------|
| POST | `/api/v1/auth/register/particulier/` | AllowAny | 01 |
| POST | `/api/v1/auth/register/boutique/` | AllowAny | 01 |
| POST | `/api/v1/auth/token/` | AllowAny | 01 |
| POST | `/api/v1/auth/token/refresh/` | AllowAny | 01 |
| GET | `/api/v1/auth/me/` | IsAuthenticated | 01 |
| PATCH | `/api/v1/auth/me/` | IsAuthenticated | 01 |
| GET | `/api/v1/catalog/categories/` | AllowAny | 02 |
| GET | `/api/v1/catalog/categories/<slug>/` | AllowAny | 02 |
| GET | `/api/v1/catalog/categories/<slug>/attributes/` | AllowAny | 02 |
| GET | `/api/v1/catalog/categories/<slug>/filterable-attributes/` | AllowAny | 04 |
| GET | `/api/v1/cities/` | AllowAny | 02 |
| POST | `/api/v1/products/` | IsAuthenticated | 03 |
| GET | `/api/v1/products/` | AllowAny | 03, 04 |
| GET | `/api/v1/products/<id>/` | AllowAny | 03 |
| PATCH | `/api/v1/products/<id>/` | IsProductOwner | 03 |
| DELETE | `/api/v1/products/<id>/` | IsProductOwner | 03 |
| GET | `/api/v1/catalog/categories/<id>/attributes-by-id/` | AllowAny | 03 |
| GET | `/api/v1/favorites/` | IsAuthenticated | 06 |
| POST | `/api/v1/favorites/` | IsAuthenticated | 06 |
| DELETE | `/api/v1/favorites/<id>/` | IsAuthenticated + IsOwner | 06 |
| POST | `/api/v1/products/<id>/report/` | IsAuthenticated | 06 |
| POST | `/api/v1/products/<id>/track-whatsapp/` | AllowAny | 06 |
| GET | `/api/v1/dashboard/my-products/` | IsAuthenticated | 05 |
| PATCH | `/api/v1/dashboard/my-products/<id>/status/` | IsAuthenticated + IsOwner | 05 |
| GET | `/api/v1/dashboard/stats/` | IsAuthenticated | 05 |
| GET | `/api/v1/dashboard/notifications/` | IsAuthenticated | 05 |
| PATCH | `/api/v1/dashboard/notifications/<id>/read/` | IsAuthenticated + IsNotificationOwner | 05 |
| POST | `/api/v1/dashboard/notifications/mark-all-read/` | IsAuthenticated | 05 |
| GET | `/api/v1/sellers/<id>/reviews/` | AllowAny | 07 |
| POST | `/api/v1/sellers/<id>/reviews/` | IsAuthenticated | 07 |
| POST | `/api/v1/reviews/<id>/reply/` | IsAuthenticated + IsSeller | 07 |
| POST | `/api/v1/reviews/<id>/report/` | IsAuthenticated | 07 |
| GET | `/api/v1/review-tags/` | AllowAny | 07 |

## Fichiers de configuration

| Fichier | Rôle |
|---------|------|
| `monsetup/settings.py` | Configuration Django principale |
| `monsetup/urls.py` | URLs racine |
| `manage.py` | CLI Django |
| `requirements.txt` | Dépendances Python |

## Dépendances installées (requirements.txt)

```
django>=5.0,<6.1
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-filter>=23.0
django-cors-headers>=4.0
Pillow>=10.0
drf-spectacular>=0.27
```

## Migrations appliquées

| App | Migration | Sprint |
|-----|-----------|--------|
| accounts | `0001_initial` | 01 |
| accounts | `0002_boutique_ville` | 02 |
| core | `0001_initial` | 02 |
| catalog | `0001_initial` | 02 |
| products | `0001_initial` | 03 |
| dashboard | `0001_initial` | 05 |
| products | `0002_productwhatsappclick_favorite_productview_report` | 06 |
| reviews | `0001_initial` | 07 |

## Fixtures disponibles

_Pas de fixtures. Validation manuelle via API (Swagger / curl)._

## Arborescence du projet

```
monsetup/
├── manage.py
├── requirements.txt
├── monsetup/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── permissions.py
│   ├── admin.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── setup_filters.py
│   └── migrations/
├── accounts/
│   ├── __init__.py
│   ├── models.py
│   ├── managers.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── urls_ssr.py
│   ├── admin.py
│   ├── templates/accounts/
│   │   ├── register_choice.html
│   │   ├── register_particulier.html
│   │   ├── register_boutique.html
│   │   ├── login.html
│   │   └── boutique_page.html
│   └── migrations/
├── catalog/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
├── products/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── filters.py
│   ├── admin.py
│   ├── utils.py
│   ├── management/commands/expire_boosts.py
│   ├── templates/products/
│   │   ├── product_list.html
│   │   ├── product_detail.html
│   │   └── product_create.html
│   └── migrations/
├── dashboard/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls_api.py
│   ├── urls_ssr.py
│   ├── permissions.py
│   ├── admin.py
│   ├── management/commands/check_ad_reminders.py
│   ├── templates/dashboard/
│   │   ├── dashboard_home.html
│   │   ├── my_products.html
│   │   ├── notifications.html
│   │   └── favorites.html
│   └── migrations/
├── reviews/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls_api.py
│   ├── urls_ssr.py
│   ├── permissions.py
│   ├── admin.py
│   ├── templates/reviews/
│   │   ├── seller_profile.html
│   │   └── seller_reviews.html
│   └── migrations/
├── templates/
│   ├── base.html
│   └── pages/
│       └── home.html
```

## Pages SSR

| URL | Template | Description | Sprint |
|-----|----------|-------------|--------|
| `/annonces/` | `products/product_list.html` | Listing annonces avec filtres, tri, recherche, EAV dynamique | 03, 04 |
| `/annonces/<id>/` | `products/product_detail.html` | Détail annonce | 03 |
| `/annonces/deposer/` | `products/product_create.html` | Formulaire dépôt (auth requise) | 03 |
| `/dashboard/` | `dashboard/dashboard_home.html` | Vue d'ensemble : stats + dernières annonces + notifications non lues | 05 |
| `/dashboard/mes-annonces/` | `dashboard/my_products.html` | Liste annonces du vendeur avec changement de statut | 05 |
| `/dashboard/notifications/` | `dashboard/notifications.html` | Liste notifications avec marquer comme lu | 05 |
| `/inscription/` | `accounts/register_choice.html` | Page de choix du type de compte | 06 |
| `/inscription/particulier/` | `accounts/register_particulier.html` | Formulaire inscription particulier | 06 |
| `/inscription/boutique/` | `accounts/register_boutique.html` | Formulaire inscription boutique | 06 |
| `/connexion/` | `accounts/login.html` | Formulaire de connexion (session-based) | 06 |
| `/deconnexion/` | — | Déconnexion + redirect | 06 |
| `/dashboard/favoris/` | `dashboard/favorites.html` | Liste des favoris dans le dashboard | 06 |
| `/vendeur/<id>/` | `reviews/seller_profile.html` | Profil vendeur avec avis | 07 |
| `/vendeur/<id>/avis/` | `reviews/seller_reviews.html` | Tous les avis d'un vendeur | 07 |
| `/` | `pages/home.html` | Page d'accueil : hero, catégories, annonces boostées, dernières annonces | 08 |
| `/boutique/<slug>/` | `accounts/boutique_page.html` | Page vitrine publique d'une boutique | 08 |

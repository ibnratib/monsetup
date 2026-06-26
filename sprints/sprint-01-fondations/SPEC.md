# Sprint 01 — Fondations

## Objectif

Mettre en place la base du projet : Custom User model, profils Particulier/Boutique, configuration DRF + JWT, structure des apps, et requirements.txt.

## Pré-requis

- Aucun (premier sprint)
- Environnement virtuel Python déjà créé (`env/`)
- Projet Django déjà initialisé (`monsetup/`)

## Livrables

### Apps à créer

| App | Rôle |
|-----|------|
| `accounts` | Custom User, Particulier, Boutique, authentification JWT |
| `core` | Utilitaires partagés, base models (TimeStampedModel), permissions communes |

### Modèles

#### `core` app

| Modèle | Champs | Notes |
|--------|--------|-------|
| `TimeStampedModel` (abstract) | `created_at` (auto), `updated_at` (auto) | Modèle de base pour tous les autres modèles |

#### `accounts` app

| Modèle | Champs | Notes |
|--------|--------|-------|
| `User` | `email` (unique, login field), `phone_whatsapp`, `first_name`, `last_name`, `user_type` (CHOICE: `particulier` / `boutique`), `is_active`, `is_staff`, `date_joined` | Custom User avec email comme identifiant (pas de username) |
| `Particulier` | `user` (OneToOne → User), `max_active_ads` (default: `MAX_ACTIVE_ADS_PARTICULIER`) | Profil C2C |
| `Boutique` | `user` (OneToOne → User), `nom_boutique`, `slug` (unique, auto-generated), `description`, `adresse`, `statut_verification` (CHOICE: `EN_ATTENTE` / `VERIFIE` / `REJETE`), `logo` | Profil B2C |

### Endpoints API

| Méthode | URL | Permission | Request body | Response |
|---------|-----|------------|--------------|----------|
| POST | `/api/v1/auth/register/particulier/` | AllowAny | `{email, password, first_name, last_name, phone_whatsapp}` | `{data: {user, tokens}}` |
| POST | `/api/v1/auth/register/boutique/` | AllowAny | `{email, password, nom_boutique, phone_whatsapp, adresse}` | `{data: {user, tokens}}` |
| POST | `/api/v1/auth/token/` | AllowAny | `{email, password}` | `{access, refresh}` |
| POST | `/api/v1/auth/token/refresh/` | AllowAny | `{refresh}` | `{access}` |
| GET | `/api/v1/auth/me/` | IsAuthenticated | — | `{data: {user + profil}}` |
| PATCH | `/api/v1/auth/me/` | IsAuthenticated | champs modifiables | `{data: {user + profil}}` |

### Serializers

| Nom | Modèle | Champs | Validations |
|-----|--------|--------|-------------|
| `RegisterParticulierSerializer` | User + Particulier | email, password, first_name, last_name, phone_whatsapp | Email unique, password min 8 chars |
| `RegisterBoutiqueSerializer` | User + Boutique | email, password, nom_boutique, phone_whatsapp, adresse | Email unique, nom_boutique requis |
| `UserSerializer` | User | id, email, first_name, last_name, phone_whatsapp, user_type, date_joined | Read-only pour email et user_type |
| `ParticulierSerializer` | Particulier | user (nested), max_active_ads | — |
| `BoutiqueSerializer` | Boutique | user (nested), nom_boutique, slug, description, adresse, statut_verification, logo | slug read-only |
| `ProfileSerializer` | User + profil | Sérialise le user + son profil (Particulier ou Boutique) dynamiquement | — |

### Permissions custom

| Nom | Logique |
|-----|---------|
| `IsOwner` | `request.user == obj.user` — pour protéger l'accès au profil |

### Settings à configurer

```python
# settings.py additions

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders',
    'accounts',
    'core',
]

MIDDLEWARE += [
    'corsheaders.middleware.CorsMiddleware',
]

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOW_ALL_ORIGINS = True  # dev only

# Constantes métier
MAX_IMAGES_PER_PRODUCT = 8
MAX_IMAGE_SIZE_MB = 2
MAX_ACTIVE_ADS_PARTICULIER = 10
MAX_DESCRIPTION_LENGTH = 300
AD_REMINDER_DAYS = 30
MAX_REVIEW_LENGTH = 500
MAX_REPLY_LENGTH = 300
```

### requirements.txt

```
django>=5.0,<6.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-filter>=23.0
django-cors-headers>=4.0
Pillow>=10.0
drf-spectacular>=0.27
```

### Fichiers à créer

```
monsetup/
├── requirements.txt
├── monsetup/
│   ├── settings.py          (modifier)
│   ├── urls.py              (modifier — inclure api/v1/auth/)
├── core/
│   ├── __init__.py
│   ├── models.py            (TimeStampedModel)
│   ├── permissions.py       (IsOwner)
│   ├── admin.py
│   └── migrations/
├── accounts/
│   ├── __init__.py
│   ├── models.py            (User, Particulier, Boutique)
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py             (enregistrer User, Particulier, Boutique)
│   ├── managers.py          (CustomUserManager)
│   └── migrations/
```

## Validations métier

- Email doit être unique (erreur explicite en français si doublon).
- Password minimum 8 caractères.
- `phone_whatsapp` : format marocain (06/07 + 8 chiffres) — validation regex.
- `slug` de Boutique : auto-généré à partir de `nom_boutique` (slugify), garanti unique.
- `statut_verification` d'une Boutique : `EN_ATTENTE` par défaut à la création (seul l'admin peut changer).
- Un User ne peut être qu'un seul type (Particulier OU Boutique, jamais les deux).

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] Les endpoints d'inscription et de login retournent des tokens JWT valides
- [ ] `GET /api/v1/auth/me/` retourne le profil complet (user + particulier/boutique)
- [ ] Admin Django accessible avec les modèles User, Particulier, Boutique
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

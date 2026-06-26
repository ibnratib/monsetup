# Sprint 06 — Auth SSR + Interactions (Favoris, Signalements, Tracking)

## Objectif

Créer les pages d'inscription/connexion/déconnexion web, le système de favoris, les signalements d'annonces, et le tracking des vues et clics WhatsApp.

## Pré-requis

- Sprint 03 complété (Product, endpoints CRUD)
- Sprint 05 complété (Dashboard, Notification)
- Lire `sprints/_design-system.md` pour le style des templates

## Livrables

### Partie 1 — Auth SSR (pages web)

#### Pages à créer

| Template | URL | Description |
|----------|-----|-------------|
| `accounts/register_choice.html` | `/inscription/` | Page de choix : "Particulier" ou "Boutique" (2 cartes cliquables) |
| `accounts/register_particulier.html` | `/inscription/particulier/` | Formulaire inscription particulier (email, mot de passe, prénom, nom, WhatsApp) |
| `accounts/register_boutique.html` | `/inscription/boutique/` | Formulaire inscription boutique (email, mot de passe, nom boutique, WhatsApp, ville, adresse) |
| `accounts/login.html` | `/connexion/` | Formulaire de connexion (email + mot de passe) |

#### Vues SSR à créer dans `accounts/views.py`

| Vue | URL | Description |
|-----|-----|-------------|
| `RegisterChoiceView` | `/inscription/` | Affiche le choix du type de compte |
| `RegisterParticulierView` (SSR) | `/inscription/particulier/` | Formulaire + création via serializer existant |
| `RegisterBoutiqueView` (SSR) | `/inscription/boutique/` | Formulaire + création via serializer existant, dropdown ville (FK City) |
| `LoginView` (SSR) | `/connexion/` | Authentification Django session (pas JWT pour le web SSR) |
| `LogoutView` | `/deconnexion/` | Déconnexion + redirect vers accueil |

#### Authentification web (session-based)

Pour les pages SSR, utiliser l'**authentification par session Django** (pas JWT) :
- `django.contrib.auth.login()` / `logout()` pour les pages web
- JWT reste pour l'API REST (mobile, intégrations)
- Les deux coexistent : `SessionAuthentication` ajouté dans DRF pour que les pages SSR qui appellent l'API interne fonctionnent

```python
# settings.py — ajouter SessionAuthentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # AJOUTER
    ],
    ...
}
```

#### Mise à jour du header (`base.html`)

Le header doit afficher dynamiquement :
- **Non connecté** : `[Connexion]` + `[S'inscrire]`
- **Connecté** : `[Déposer]` + `[Dashboard]` + nom d'utilisateur + `[Déconnexion]`
- **Connecté + notifications non lues** : badge numérique sur "Dashboard"

#### URLs à ajouter

```python
# monsetup/urls.py
path('inscription/', include('accounts.urls_ssr')),
path('connexion/', LoginView.as_view(), name='login'),
path('deconnexion/', LogoutView.as_view(), name='logout'),
```

#### Fichiers à créer / modifier

```
accounts/
├── urls_ssr.py          (CRÉER — routes SSR inscription)
├── views.py             (MODIFIER — ajouter vues SSR)
├── templates/
│   └── accounts/
│       ├── register_choice.html
│       ├── register_particulier.html
│       ├── register_boutique.html
│       └── login.html
templates/
└── base.html            (MODIFIER — header dynamique)
```

### Partie 2 — Favoris (wishlist)

#### Modèle

| Modèle | App | Champs | Notes |
|--------|-----|--------|-------|
| `Favorite` | `products` | `user` (FK User), `product` (FK Product) | Hérite de `TimeStampedModel`. Unique ensemble (user, product). |

#### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| GET | `/api/v1/favorites/` | IsAuthenticated | Liste des favoris de l'utilisateur connecté |
| POST | `/api/v1/favorites/` | IsAuthenticated | Ajouter un produit aux favoris (`{ "product": <id> }`) |
| DELETE | `/api/v1/favorites/<id>/` | IsAuthenticated + IsOwner | Retirer un favori |

#### Serializers

| Nom | Champs |
|-----|--------|
| `FavoriteSerializer` | `id`, `product` (nested : id, title, price, thumbnail, status, ville), `created_at` |
| `FavoriteCreateSerializer` | `product` (PK) — validation : produit existe, pas déjà en favori |

#### Pages SSR

| Template | URL | Description |
|----------|-----|-------------|
| `dashboard/favorites.html` | `/dashboard/favoris/` | Liste des favoris dans le dashboard (avec bouton retirer) |

- Bouton "Ajouter aux favoris" (cœur) sur chaque carte produit dans le listing et la fiche détail
- Cœur plein si déjà en favori, vide sinon
- Toggle via POST/DELETE fetch API (JS simple) ou formulaire POST classique

#### Ajout dans la sidebar dashboard

Ajouter un lien "Mes favoris" dans la sidebar du dashboard (après "Mes annonces" et "Notifications").

### Partie 3 — Signalements

#### Modèle

| Modèle | App | Champs | Notes |
|--------|-----|--------|-------|
| `Report` | `products` | `reporter` (FK User), `product` (FK Product), `reason` (CHOICE: `FRAUDULEUSE`, `PRIX_IRREALISTE`, `PRODUIT_INTERDIT`, `CONTENU_INAPPROPRIE`, `DOUBLON`), `comment` (TextField, optionnel, max 500), `status` (CHOICE: `EN_ATTENTE` / `TRAITEE` / `REJETEE`, default `EN_ATTENTE`) | Hérite de `TimeStampedModel`. Un user ne peut signaler le même produit qu'une seule fois. |

#### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| POST | `/api/v1/products/<id>/report/` | IsAuthenticated | Signaler une annonce |

#### Page SSR

- Bouton "Signaler" sur la fiche produit (modale ou page dédiée)
- Formulaire : dropdown raison + commentaire optionnel
- Confirmation : "Votre signalement a été envoyé."

#### Admin Django

- `Report` : list_display = (product, reporter, reason, status, created_at), list_filter = (reason, status), actions = (marquer comme traitée, rejeter)

### Partie 4 — Tracking (vues et clics WhatsApp)

#### Modèles

| Modèle | App | Champs | Notes |
|--------|-----|--------|-------|
| `ProductView` | `products` | `product` (FK Product), `session_key` (CharField), `ip_address` (GenericIPAddressField), `created_at` (auto) | Déduplication : 1 vue par session par produit (pas de double comptage si refresh) |
| `ProductWhatsAppClick` | `products` | `product` (FK Product), `user` (FK User, nullable), `created_at` (auto) | Chaque clic WhatsApp est tracké |

#### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| POST | `/api/v1/products/<id>/track-whatsapp/` | AllowAny | Tracker un clic WhatsApp (incrémente le compteur) |

#### Logique de tracking des vues

Modifier `ProductDetailView` (SSR) et `ProductDetailAPIView` (API) :
- Au lieu de simplement `F('views_count') + 1`, créer un `ProductView` avec déduplication par session
- Si un `ProductView` existe déjà pour ce produit + cette session → ne pas incrémenter
- Sinon → créer le `ProductView` + incrémenter `views_count`

#### Logique de tracking WhatsApp

- Sur la fiche produit, le bouton WhatsApp envoie d'abord un POST à `/api/v1/products/<id>/track-whatsapp/` via fetch, puis redirige vers `wa.me`
- L'endpoint incrémente `whatsapp_clicks_count` et crée un `ProductWhatsAppClick`

### Settings à modifier

```python
INSTALLED_APPS — pas de nouvelle app, tout va dans accounts et products
LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
```

## Validations métier

- Un utilisateur ne peut ajouter le même produit qu'une seule fois en favori (unique ensemble).
- Un utilisateur ne peut signaler le même produit qu'une seule fois.
- Un utilisateur ne peut pas signaler sa propre annonce.
- Le tracking de vues est dédupliqué par session (1 vue par session par produit).
- Les pages d'inscription créent le User + le profil (Particulier ou Boutique) dans une transaction atomique.
- Après inscription, l'utilisateur est automatiquement connecté et redirigé vers le dashboard.
- Après connexion, redirect vers `next` (si présent) ou vers le dashboard.
- Le header de `base.html` reflète correctement l'état de connexion.

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] Pages `/inscription/`, `/inscription/particulier/`, `/inscription/boutique/` fonctionnelles
- [ ] Page `/connexion/` fonctionnelle avec redirect
- [ ] Déconnexion via `/deconnexion/`
- [ ] Header `base.html` dynamique (connecté / non connecté)
- [ ] `POST /api/v1/favorites/` ajoute un favori
- [ ] `DELETE /api/v1/favorites/<id>/` retire un favori
- [ ] Page `/dashboard/favoris/` affiche les favoris
- [ ] Bouton cœur sur les cartes produit (listing + fiche)
- [ ] `POST /api/v1/products/<id>/report/` crée un signalement
- [ ] Bouton "Signaler" sur la fiche produit
- [ ] Tracking vues dédupliqué par session
- [ ] Tracking clics WhatsApp fonctionnel
- [ ] Templates conformes au design system (`_design-system.md`)
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

# Sprint 05 — Dashboard vendeur

## Objectif

Créer l'espace privé du vendeur (particulier ou boutique) : liste de ses annonces, statistiques (vues, clics WhatsApp), changement de statut, notifications de rappel (30 jours), et les pages SSR correspondantes.

## Pré-requis

- Sprint 03 complété (Product, ProductImage, endpoints CRUD)
- Sprint 04 complété (filtres, listing enrichi)
- Lire `sprints/_design-system.md` pour le style des templates

## Livrables

### App à créer

| App | Rôle |
|-----|------|
| `dashboard` | Dashboard vendeur : mes annonces, stats, changement statut, notifications |

### Modèles

#### `dashboard` app

| Modèle | Champs | Notes |
|--------|--------|-------|
| `Notification` | `user` (FK User), `type` (CHOICE: `RAPPEL_DISPONIBILITE`, `SIGNALEMENT_RECU`, `ANNONCE_EXPIREE`), `message` (TextField), `product` (FK Product, nullable), `is_read` (bool, default False), `created_at` (auto) | Hérite de `TimeStampedModel`. Notifications internes au dashboard. |

### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| GET | `/api/v1/dashboard/my-products/` | IsAuthenticated | Liste des annonces du vendeur connecté (toutes, avec filtrage par statut possible) |
| PATCH | `/api/v1/dashboard/my-products/<id>/status/` | IsAuthenticated + IsOwner | Changer le statut d'une annonce (DISPONIBLE / VENDU / ARCHIVE) |
| GET | `/api/v1/dashboard/stats/` | IsAuthenticated | Stats agrégées : total annonces, total vues, total clics WhatsApp, annonces par statut |
| GET | `/api/v1/dashboard/notifications/` | IsAuthenticated | Liste des notifications du vendeur (paginée) |
| PATCH | `/api/v1/dashboard/notifications/<id>/read/` | IsAuthenticated + IsOwner | Marquer une notification comme lue |
| POST | `/api/v1/dashboard/notifications/mark-all-read/` | IsAuthenticated | Marquer toutes les notifications comme lues |

### Serializers

| Nom | Usage | Champs |
|-----|-------|--------|
| `MyProductListSerializer` | Liste mes annonces | `id`, `title`, `price`, `status`, `ville` (nom), `category` (nom), `thumbnail`, `views_count`, `whatsapp_clicks_count`, `created_at` |
| `ProductStatusUpdateSerializer` | Changement statut | `status` (validation : uniquement DISPONIBLE/VENDU/ARCHIVE) |
| `DashboardStatsSerializer` | Stats agrégées | `total_products`, `total_views`, `total_whatsapp_clicks`, `products_disponible`, `products_vendu`, `products_archive` |
| `NotificationSerializer` | Liste notifications | `id`, `type`, `message`, `product` (id + title), `is_read`, `created_at` |

### Logique de rappel 30 jours

```python
# Management command : python manage.py check_ad_reminders
# À exécuter périodiquement (cron ou manuellement au MVP)
#
# Pour chaque Product avec status=DISPONIBLE et updated_at < (now - AD_REMINDER_DAYS) :
# 1. Vérifier qu'il n'existe pas déjà une notification RAPPEL_DISPONIBILITE non lue pour ce produit
# 2. Si non, créer une Notification :
#    - user = product.seller
#    - type = RAPPEL_DISPONIBILITE
#    - message = "Votre annonce « {title} » est en ligne depuis plus de 30 jours. Est-elle toujours disponible ?"
#    - product = product
```

### Management command

| Commande | Rôle |
|----------|------|
| `check_ad_reminders` | Crée les notifications de rappel pour les annonces > 30 jours sans changement |

### Permissions custom

| Nom | Logique |
|-----|---------|
| `IsNotificationOwner` | `request.user == obj.user` |

### Pages SSR

| Template | URL | Description |
|----------|-----|-------------|
| `dashboard/dashboard_home.html` | `/dashboard/` | Vue d'ensemble : stats + dernières annonces + notifications non lues |
| `dashboard/my_products.html` | `/dashboard/mes-annonces/` | Liste complète des annonces avec statut, vues, clics WA. Boutons changement statut. Filtrage par statut (tabs : Toutes / Disponibles / Vendues / Archivées) |
| `dashboard/notifications.html` | `/dashboard/notifications/` | Liste des notifications avec bouton "marquer comme lu" |

#### Layout dashboard

```
┌──────────────────────────────────────────────────────────┐
│  HEADER (Setup.ma)                    [Dashboard] [+]    │
├────────────┬─────────────────────────────────────────────┤
│ SIDEBAR    │  CONTENU PRINCIPAL                          │
│            │                                             │
│ Vue        │  ┌─────────────────────────────────────┐   │
│ d'ensemble │  │  Stats (4 cartes)                   │   │
│            │  │  Vues | Clics WA | Actives | Total  │   │
│ Mes        │  └─────────────────────────────────────┘   │
│ annonces   │                                             │
│            │  ┌─────────────────────────────────────┐   │
│ Notifs (3) │  │  Dernières annonces (tableau)       │   │
│            │  └─────────────────────────────────────┘   │
├────────────┴─────────────────────────────────────────────┤
│  FOOTER                                                   │
└──────────────────────────────────────────────────────────┘
```

- **Desktop** : sidebar gauche (w-56) + contenu principal
- **Mobile** : sidebar cachée, navigation via tabs ou menu hamburger
- **Stats** : 4 cartes en grille (`grid grid-cols-2 lg:grid-cols-4 gap-4`)
- **Tableau annonces** : responsive (scroll horizontal sur mobile ou cards empilées)

#### Carte stat

```html
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
  <p class="text-sm text-gray-500">Total vues</p>
  <p class="mt-1 text-2xl font-bold text-gray-900">1 234</p>
</div>
```

#### Ligne tableau annonce (dashboard)

Chaque annonce affiche :
- Thumbnail (petite)
- Titre (lien vers fiche)
- Prix
- Statut (badge coloré)
- Vues / Clics WA
- Date de publication
- Boutons d'action : Modifier | Changer statut (dropdown : Disponible/Vendu/Archivé) | Supprimer

Le changement de statut se fait via un formulaire POST simple (pas besoin de JS complexe au MVP) ou via fetch API avec rafraîchissement.

### Settings à modifier

```python
INSTALLED_APPS += [
    'dashboard',
]
```

### URLs à ajouter

```python
# monsetup/urls.py
path('api/v1/dashboard/', include('dashboard.urls_api')),
path('dashboard/', include('dashboard.urls_ssr')),
```

### Fichiers à créer

```
dashboard/
├── __init__.py
├── models.py              (Notification)
├── serializers.py
├── views.py               (API + SSR views)
├── urls_api.py            (endpoints REST)
├── urls_ssr.py            (pages dashboard)
├── permissions.py         (IsNotificationOwner)
├── admin.py               (Notification admin)
├── management/
│   └── commands/
│       └── check_ad_reminders.py
├── templates/
│   └── dashboard/
│       ├── dashboard_home.html
│       ├── my_products.html
│       └── notifications.html
└── migrations/
```

## Validations métier

- Un vendeur ne voit que **ses propres** annonces et notifications (isolation stricte `seller=request.user` / `user=request.user`).
- Le statut ne peut être changé qu'en `DISPONIBLE`, `VENDU` ou `ARCHIVE` (pas de valeur custom).
- Les notifications de rappel ne sont créées qu'une seule fois par annonce tant que la précédente n'est pas lue.
- Le compteur de notifications non lues est affiché dans le header (badge numérique).
- Les stats ne comptent que les annonces du vendeur connecté.

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] `GET /api/v1/dashboard/my-products/` retourne uniquement les annonces du vendeur connecté
- [ ] `PATCH /api/v1/dashboard/my-products/<id>/status/` change le statut correctement
- [ ] `GET /api/v1/dashboard/stats/` retourne les stats agrégées
- [ ] `GET /api/v1/dashboard/notifications/` retourne les notifications
- [ ] `python manage.py check_ad_reminders` crée les notifications de rappel 30j
- [ ] Page SSR `/dashboard/` affiche stats + dernières annonces + notifications
- [ ] Page SSR `/dashboard/mes-annonces/` affiche la liste avec changement de statut
- [ ] Templates conformes au design system (`_design-system.md`)
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

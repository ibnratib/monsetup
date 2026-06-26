# Sprint 05 — Dashboard vendeur — DONE

## Résumé

Dashboard vendeur complet avec API REST et pages SSR : liste de ses annonces, statistiques agrégées, changement de statut, notifications internes et commande de rappel 30 jours.

## Livrables

### App créée

- `dashboard` — Dashboard vendeur (mes annonces, stats, changement statut, notifications)

### Modèle créé

| Modèle | App | Champs |
|--------|-----|--------|
| `Notification` | dashboard | `user` (FK User), `type` (RAPPEL_DISPONIBILITE / SIGNALEMENT_RECU / ANNONCE_EXPIREE), `message`, `product` (FK Product, nullable), `is_read` (bool) |

### Endpoints API

| Méthode | URL | Permission |
|---------|-----|------------|
| GET | `/api/v1/dashboard/my-products/` | IsAuthenticated |
| PATCH | `/api/v1/dashboard/my-products/<id>/status/` | IsAuthenticated + IsOwner |
| GET | `/api/v1/dashboard/stats/` | IsAuthenticated |
| GET | `/api/v1/dashboard/notifications/` | IsAuthenticated |
| PATCH | `/api/v1/dashboard/notifications/<id>/read/` | IsAuthenticated + IsNotificationOwner |
| POST | `/api/v1/dashboard/notifications/mark-all-read/` | IsAuthenticated |

### Pages SSR

| URL | Template |
|-----|----------|
| `/dashboard/` | `dashboard/dashboard_home.html` |
| `/dashboard/mes-annonces/` | `dashboard/my_products.html` |
| `/dashboard/notifications/` | `dashboard/notifications.html` |

### Management command

| Commande | Rôle |
|----------|------|
| `check_ad_reminders` | Crée les notifications de rappel pour les annonces > 30 jours sans changement |

### Fichiers créés / modifiés

**Créés :**
- `dashboard/__init__.py`
- `dashboard/models.py`
- `dashboard/serializers.py`
- `dashboard/views.py`
- `dashboard/urls_api.py`
- `dashboard/urls_ssr.py`
- `dashboard/permissions.py`
- `dashboard/admin.py`
- `dashboard/migrations/0001_initial.py`
- `dashboard/management/__init__.py`
- `dashboard/management/commands/__init__.py`
- `dashboard/management/commands/check_ad_reminders.py`
- `dashboard/templates/dashboard/dashboard_home.html`
- `dashboard/templates/dashboard/my_products.html`
- `dashboard/templates/dashboard/notifications.html`

**Modifiés :**
- `monsetup/settings.py` — ajout `dashboard` dans INSTALLED_APPS
- `monsetup/urls.py` — ajout routes `/api/v1/dashboard/` et `/dashboard/`
- `templates/base.html` — ajout lien Dashboard dans le header

### Migration

| App | Migration | Sprint |
|-----|-----------|--------|
| dashboard | `0001_initial` | 05 |

## Contrat de sortie (Definition of Done)

- [x] `python manage.py migrate` fonctionne sans erreur
- [x] `GET /api/v1/dashboard/my-products/` retourne uniquement les annonces du vendeur connecté
- [x] `PATCH /api/v1/dashboard/my-products/<id>/status/` change le statut correctement
- [x] `GET /api/v1/dashboard/stats/` retourne les stats agrégées
- [x] `GET /api/v1/dashboard/notifications/` retourne les notifications
- [x] `python manage.py check_ad_reminders` crée les notifications de rappel 30j
- [x] Page SSR `/dashboard/` affiche stats + dernières annonces + notifications
- [x] Page SSR `/dashboard/mes-annonces/` affiche la liste avec changement de statut
- [x] Templates conformes au design system (`_design-system.md`)
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

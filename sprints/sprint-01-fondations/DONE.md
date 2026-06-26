# Sprint 01 — Fondations ✅

## Date de complétion

2026-06-26

## Livrables réalisés

### Apps créées
- [x] `core` — TimeStampedModel (abstract), permission IsOwner
- [x] `accounts` — Custom User (email-based), Particulier, Boutique, auth JWT

### Modèles
- [x] `TimeStampedModel` (abstract) — `created_at`, `updated_at`
- [x] `User` — email comme identifiant, `phone_whatsapp`, `user_type`
- [x] `Particulier` — OneToOne → User, `max_active_ads`
- [x] `Boutique` — OneToOne → User, `nom_boutique`, `slug` (auto-unique), `statut_verification`

### Endpoints API
- [x] `POST /api/v1/auth/register/particulier/` — Inscription particulier + tokens JWT
- [x] `POST /api/v1/auth/register/boutique/` — Inscription boutique + tokens JWT
- [x] `POST /api/v1/auth/token/` — Login (email + password → tokens)
- [x] `POST /api/v1/auth/token/refresh/` — Refresh token
- [x] `GET /api/v1/auth/me/` — Profil complet (user + particulier/boutique)
- [x] `PATCH /api/v1/auth/me/` — Mise à jour profil

### Configuration
- [x] `requirements.txt` créé avec toutes les dépendances
- [x] `settings.py` configuré (DRF, JWT, CORS, django-filter, drf-spectacular)
- [x] `AUTH_USER_MODEL = 'accounts.User'`
- [x] Constantes métier définies dans settings

### Admin Django
- [x] User, Particulier, Boutique enregistrés dans l'admin

## Validations métier implémentées

- [x] Email unique (erreur en français)
- [x] Password minimum 8 caractères
- [x] `phone_whatsapp` : validation regex format marocain (06/07 + 8 chiffres)
- [x] `slug` Boutique : auto-généré depuis `nom_boutique`, unicité garantie
- [x] `statut_verification` : `EN_ATTENTE` par défaut

## Definition of Done

- [x] `python manage.py migrate` fonctionne sans erreur
- [x] Les endpoints d'inscription et de login retournent des tokens JWT valides
- [x] `GET /api/v1/auth/me/` retourne le profil complet (user + particulier/boutique)
- [x] Admin Django accessible avec les modèles User, Particulier, Boutique
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

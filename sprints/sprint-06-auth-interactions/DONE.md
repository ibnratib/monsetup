# Sprint 06 — DONE

## Résumé

Sprint 06 implémenté : Auth SSR (inscription/connexion/déconnexion web), système de favoris, signalements d'annonces, et tracking dédupliqué des vues et clics WhatsApp.

## Livrables réalisés

### Partie 1 — Auth SSR
- [x] Page `/inscription/` — choix du type de compte (Particulier / Boutique)
- [x] Page `/inscription/particulier/` — formulaire inscription particulier
- [x] Page `/inscription/boutique/` — formulaire inscription boutique avec dropdown ville
- [x] Page `/connexion/` — formulaire de connexion (session-based)
- [x] Déconnexion via `/deconnexion/` avec redirect
- [x] Authentification web par session Django (pas JWT)
- [x] `SessionAuthentication` ajouté dans DRF
- [x] Après inscription → auto-connexion + redirect dashboard
- [x] Après connexion → redirect `next` ou dashboard
- [x] Header `base.html` dynamique : connecté (Dashboard, Déposer, nom, Déconnexion) / non connecté (Connexion, S'inscrire)
- [x] `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` configurés
- [x] `login_url = '/admin/login/'` remplacé dans toutes les vues dashboard/products

### Partie 2 — Favoris
- [x] Modèle `Favorite` (user + product, unique ensemble)
- [x] `GET /api/v1/favorites/` — liste des favoris
- [x] `POST /api/v1/favorites/` — ajouter un favori
- [x] `DELETE /api/v1/favorites/<id>/` — retirer un favori
- [x] Page `/dashboard/favoris/` — liste des favoris dans le dashboard (avec bouton retirer)
- [x] Bouton cœur sur la fiche produit (toggle via fetch API)
- [x] Lien "Mes favoris" ajouté dans la sidebar de toutes les pages dashboard

### Partie 3 — Signalements
- [x] Modèle `Report` (reporter, product, reason, comment, status)
- [x] `POST /api/v1/products/<id>/report/` — signaler une annonce
- [x] Validation : pas de double signalement, pas de signalement de sa propre annonce
- [x] Bouton "Signaler" sur la fiche produit (modale)
- [x] Admin Django : `ReportAdmin` avec list_display, list_filter, actions (marquer traitée, rejeter)

### Partie 4 — Tracking
- [x] Modèle `ProductView` (déduplication par session_key)
- [x] Modèle `ProductWhatsAppClick`
- [x] Tracking vues dédupliqué dans `ProductDetailView` (SSR) et `ProductDetailAPIView` (API)
- [x] `POST /api/v1/products/<id>/track-whatsapp/` — tracking clics WhatsApp
- [x] Bouton WhatsApp envoie POST de tracking avant de rediriger vers wa.me

## Fichiers créés

| Fichier | Description |
|---------|-------------|
| `accounts/urls_ssr.py` | Routes SSR inscription |
| `accounts/templates/accounts/register_choice.html` | Page choix type de compte |
| `accounts/templates/accounts/register_particulier.html` | Formulaire inscription particulier |
| `accounts/templates/accounts/register_boutique.html` | Formulaire inscription boutique |
| `accounts/templates/accounts/login.html` | Formulaire connexion |
| `dashboard/templates/dashboard/favorites.html` | Liste des favoris |
| `products/migrations/0002_productwhatsappclick_favorite_productview_report.py` | Migration sprint 06 |

## Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `monsetup/settings.py` | Ajout `SessionAuthentication`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` |
| `monsetup/urls.py` | Routes inscription, connexion, déconnexion, favoris API |
| `accounts/views.py` | Ajout vues SSR (RegisterChoice, RegisterParticulier, RegisterBoutique, Login, Logout) |
| `products/models.py` | Ajout modèles Favorite, Report, ProductView, ProductWhatsAppClick |
| `products/serializers.py` | Ajout FavoriteSerializer, FavoriteCreateSerializer, ReportCreateSerializer |
| `products/views.py` | Ajout FavoriteListCreateAPIView, FavoriteDeleteAPIView, ProductReportAPIView, ProductTrackWhatsAppAPIView, tracking dédupliqué |
| `products/urls.py` | Nouveaux endpoints API (favorites, report, track-whatsapp) |
| `products/admin.py` | Ajout ReportAdmin avec actions |
| `products/templates/products/product_detail.html` | Bouton favoris, bouton signaler (modale), tracking WhatsApp JS |
| `dashboard/views.py` | Ajout FavoritesView, suppression login_url hardcodé |
| `dashboard/urls_ssr.py` | Route `/dashboard/favoris/` |
| `dashboard/templates/dashboard/dashboard_home.html` | Lien "Mes favoris" dans sidebar |
| `dashboard/templates/dashboard/my_products.html` | Lien "Mes favoris" dans sidebar |
| `dashboard/templates/dashboard/notifications.html` | Lien "Mes favoris" dans sidebar |
| `templates/base.html` | Header dynamique (connecté/non connecté) |

## Migration

```
products.0002_productwhatsappclick_favorite_productview_report
```

## Validation

- [x] `python manage.py migrate` — OK
- [x] `python manage.py check` — 0 issues
- [x] `_registry.md` mis à jour

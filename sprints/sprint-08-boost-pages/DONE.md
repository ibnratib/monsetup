# Sprint 08 — DONE

## Résumé

Boost admin-only, expiration automatique des boosts, consolidation du rappel 30j, page d'accueil et page boutique publique.

## Livrables réalisés

### Partie 1 — Boost (admin-only)

- **Actions admin** sur `ProductAdmin` :
  - "Booster pour 7 jours" → `is_boosted=True`, `boost_expires_at=now+7j`
  - "Booster pour 30 jours" → `is_boosted=True`, `boost_expires_at=now+30j`
  - "Retirer le boost" → `is_boosted=False`, `boost_expires_at=None`
- **Management command `expire_boosts`** (`products/management/commands/expire_boosts.py`) :
  - Désactive les boosts avec `boost_expires_at <= now`
  - Met `is_boosted=False` et `boost_expires_at=None`

### Partie 2 — Rappels d'expiration (consolidation)

- `check_ad_reminders` (sprint 05) vérifié et fonctionnel :
  - Crée des notifications `RAPPEL_DISPONIBILITE` pour les annonces `DISPONIBLE` avec `updated_at < now - AD_REMINDER_DAYS`
  - Pas de doublon si notification non lue existante

### Partie 3 — Page d'accueil

- **Vue** : `HomePageView` dans `core/views.py` (TemplateView)
- **Template** : `templates/pages/home.html`
- **URL** : `/` (name=`home`)
- **Contenu** :
  - Hero section avec barre de recherche → redirige vers `/annonces/?search=...`
  - Grille de catégories racines avec icônes
  - Annonces boostées (max 8, status=DISPONIBLE, boost non expiré)
  - Dernières annonces (max 8, status=DISPONIBLE)
  - Section "Pourquoi Setup.ma" (3 colonnes)
- Logo dans `base.html` pointe vers `/` (name=`home`)

### Partie 4 — Page boutique

- **Vue** : `BoutiquePageView` dans `accounts/views.py` (View)
- **Template** : `accounts/templates/accounts/boutique_page.html`
- **URL** : `/boutique/<slug>/` (name=`boutique-page`)
- **Contenu** :
  - En-tête : logo, nom, badge vérifié (si `VERIFIE`), ville, note moyenne, bouton WhatsApp, description
  - Grille des annonces DISPONIBLE de la boutique (paginé, 20/page)
  - 5 derniers avis avec lien vers la page complète des avis

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `products/management/__init__.py` | Package init |
| `products/management/commands/__init__.py` | Package init |
| `products/management/commands/expire_boosts.py` | Command expiration boosts |
| `core/views.py` | HomePageView |
| `templates/pages/home.html` | Template page d'accueil |
| `accounts/templates/accounts/boutique_page.html` | Template page boutique |

## Fichiers modifiés

| Fichier | Modification |
|---------|--------------|
| `products/admin.py` | Ajout actions boost (7j, 30j, retirer) |
| `accounts/views.py` | Ajout BoutiquePageView |
| `monsetup/urls.py` | Ajout routes `/` et `/boutique/<slug>/` |
| `templates/base.html` | Logo pointe vers `home` |

## Contrat de sortie

- [x] `python manage.py migrate` — pas de nouvelle migration nécessaire
- [x] Actions admin "Booster 7j / 30j / Retirer boost" fonctionnelles
- [x] `python manage.py expire_boosts` désactive les boosts expirés
- [x] `python manage.py check_ad_reminders` crée les notifications de rappel (vérifié)
- [x] Page d'accueil `/` : hero, catégories, annonces boostées, dernières annonces
- [x] Barre de recherche redirige vers `/annonces/?search=...`
- [x] Page boutique `/boutique/<slug>/` : infos, annonces, avis
- [x] Badge vérifié affiché si `statut_verification == 'VERIFIE'`
- [x] Templates conformes au design system
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

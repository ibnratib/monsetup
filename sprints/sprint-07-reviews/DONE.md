# Sprint 07 — Avis vendeurs — DONE

## Résumé

Système complet de notation et d'avis sur les vendeurs, avec étoiles (1-5), commentaire texte, tags prédéfinis, réponse du vendeur, signalement d'avis, et pages SSR.

## Livrables réalisés

### App créée

- `reviews` — ReviewTag, Review, ReviewReply, ReviewReport

### Modèles

| Modèle | Description |
|--------|-------------|
| `ReviewTag` | Tags prédéfinis administrables (label unique, max 50) |
| `Review` | Avis d'un utilisateur sur un vendeur : rating (1-5), comment (optionnel, max 500), tags (M2M). Unique (reviewer, seller). Hérite de TimeStampedModel. |
| `ReviewReply` | Réponse du vendeur à un avis (OneToOne Review, text max 300). Hérite de TimeStampedModel. |
| `ReviewReport` | Signalement d'avis : reason (FAUX_AVIS, DIFFAMATION, CONTENU_INAPPROPRIE, SPAM), comment, status (EN_ATTENTE/TRAITEE/REJETEE). Unique (reporter, review). Hérite de TimeStampedModel. |

### Endpoints API

| Méthode | URL | Permission |
|---------|-----|------------|
| GET | `/api/v1/sellers/<id>/reviews/` | AllowAny |
| POST | `/api/v1/sellers/<id>/reviews/` | IsAuthenticated |
| POST | `/api/v1/reviews/<id>/reply/` | IsAuthenticated + IsSeller |
| POST | `/api/v1/reviews/<id>/report/` | IsAuthenticated |
| GET | `/api/v1/review-tags/` | AllowAny |

### Pages SSR

| URL | Template | Description |
|-----|----------|-------------|
| `/vendeur/<id>/` | `reviews/seller_profile.html` | Profil vendeur : infos, note moyenne, top tags, annonces, formulaire avis, liste des 5 derniers avis |
| `/vendeur/<id>/avis/` | `reviews/seller_reviews.html` | Liste complète paginée des avis |

### Intégration fiche produit

- `product_detail.html` enrichi avec : note moyenne vendeur, nombre d'avis (lien vers profil), top tags, badge vérifié
- `ProductDetailView` mis à jour pour injecter les données review du vendeur

### Admin Django

- `ReviewTag` : list_display = (label,)
- `Review` : list_display = (reviewer, seller, rating, created_at), list_filter = (rating,), search, inline ReviewReply
- `ReviewReport` : list_display, list_filter, actions (marquer traitée, rejeter)

### Fichiers créés

```
reviews/
├── __init__.py
├── models.py
├── serializers.py
├── views.py
├── urls_api.py
├── urls_ssr.py
├── permissions.py
├── admin.py
├── templates/
│   └── reviews/
│       ├── seller_profile.html
│       └── seller_reviews.html
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

### Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `monsetup/settings.py` | Ajout `'reviews'` dans INSTALLED_APPS |
| `monsetup/urls.py` | Ajout routes API (`api/v1/`) et SSR (`vendeur/`) pour reviews |
| `products/views.py` | `ProductDetailView.get_context_data` enrichi avec données review vendeur |
| `products/templates/products/product_detail.html` | Section vendeur enrichie : note, avis, top tags, badge vérifié, lien profil |

### Migrations

| App | Migration |
|-----|-----------|
| reviews | `0001_initial` |

## Validations métier

- [x] Un utilisateur ne peut laisser qu'un seul avis par vendeur (unique constraint + update_or_create)
- [x] Pas d'avis sur soi-même (validation serializer)
- [x] Note entre 1 et 5 (validators + serializer)
- [x] Commentaire optionnel, max 500 caractères
- [x] Tags parmi ReviewTag existants (validation serializer)
- [x] Vendeur répond une seule fois (OneToOne + validation)
- [x] Réponse max 300 caractères
- [x] Un seul signalement par avis par utilisateur (unique constraint + validation)
- [x] Tags administrés via Django Admin

## Definition of Done

- [x] `python manage.py migrate` fonctionne sans erreur
- [x] `GET /api/v1/sellers/<id>/reviews/` retourne la liste paginée des avis
- [x] `POST /api/v1/sellers/<id>/reviews/` crée/modifie un avis avec rating + tags
- [x] `POST /api/v1/reviews/<id>/reply/` permet au vendeur de répondre
- [x] `POST /api/v1/reviews/<id>/report/` signale un avis
- [x] Page SSR `/vendeur/<id>/` affiche le profil vendeur avec avis
- [x] Étoiles interactives fonctionnelles dans le formulaire
- [x] Note moyenne + top tags affichés sur la fiche produit (product_detail.html)
- [x] Admin Django : ReviewTag, Review, ReviewReply, ReviewReport
- [x] Templates conformes au design system (`_design-system.md`)
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

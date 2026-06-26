# Sprint 07 — Avis vendeurs

## Objectif

Créer le système de notation et d'avis sur les vendeurs : étoiles (1-5), commentaire texte, tags prédéfinis, réponse du vendeur, signalement d'avis, et les pages SSR correspondantes.

## Pré-requis

- Sprint 01 complété (User, Particulier, Boutique)
- Sprint 06 complété (Auth SSR, signalements)
- Lire `sprints/_design-system.md` pour le style des templates

## Livrables

### App à créer

| App | Rôle |
|-----|------|
| `reviews` | Review, ReviewReply, ReviewTag, signalement d'avis |

### Modèles

#### `reviews` app

| Modèle | Champs | Notes |
|--------|--------|-------|
| `ReviewTag` | `label` (CharField, unique, max 50) | Tags prédéfinis administrables. Ex: "Produit conforme", "Vendeur réactif", "Bon prix", "Emballage soigné", "Ponctuel au RDV". |
| `Review` | `reviewer` (FK User), `seller` (FK User, related_name='received_reviews'), `rating` (PositiveSmallIntegerField, 1-5), `comment` (TextField, max `MAX_REVIEW_LENGTH`, optionnel), `tags` (M2M ReviewTag, blank), `created_at`, `updated_at` | Hérite de `TimeStampedModel`. Unique ensemble (reviewer, seller). Un utilisateur ne peut laisser qu'un seul avis par vendeur. |
| `ReviewReply` | `review` (OneToOne Review), `text` (TextField, max `MAX_REPLY_LENGTH`), `created_at` | Hérite de `TimeStampedModel`. Le vendeur ne peut répondre qu'une seule fois. |
| `ReviewReport` | `reporter` (FK User), `review` (FK Review), `reason` (CHOICE: `FAUX_AVIS`, `DIFFAMATION`, `CONTENU_INAPPROPRIE`, `SPAM`), `comment` (TextField, optionnel, max 500), `status` (CHOICE: `EN_ATTENTE` / `TRAITEE` / `REJETEE`, default `EN_ATTENTE`) | Hérite de `TimeStampedModel`. Unique ensemble (reporter, review). |

### Méthodes sur le modèle User (ou via annotation)

```python
# Propriétés calculées pour le profil vendeur :
# - average_rating : moyenne des notes reçues (arrondi 1 décimale)
# - reviews_count : nombre d'avis reçus
# - top_tags : les 3 tags les plus fréquents dans les avis reçus
```

### Endpoints API

| Méthode | URL | Permission | Description |
|---------|-----|------------|-------------|
| GET | `/api/v1/sellers/<id>/reviews/` | AllowAny | Liste des avis d'un vendeur (paginée, du plus récent au plus ancien) |
| POST | `/api/v1/sellers/<id>/reviews/` | IsAuthenticated | Créer ou modifier son avis sur un vendeur |
| POST | `/api/v1/reviews/<id>/reply/` | IsAuthenticated + IsSeller | Répondre à un avis (vendeur uniquement) |
| POST | `/api/v1/reviews/<id>/report/` | IsAuthenticated | Signaler un avis |
| GET | `/api/v1/review-tags/` | AllowAny | Liste des tags disponibles |

### Serializers

| Nom | Champs |
|-----|--------|
| `ReviewTagSerializer` | `id`, `label` |
| `ReviewReplySerializer` | `id`, `text`, `created_at` |
| `ReviewSerializer` | `id`, `reviewer` (id, first_name, user_type), `rating`, `comment`, `tags` (liste labels), `reply` (nested, nullable), `created_at` |
| `ReviewCreateSerializer` | `rating` (1-5), `comment` (optionnel, max 500), `tags` (liste d'ids) — validation : pas d'avis sur soi-même, rating entre 1 et 5 |
| `ReviewReplyCreateSerializer` | `text` (max 300) — validation : le vendeur concerné = request.user |
| `ReviewReportSerializer` | `reason`, `comment` (optionnel) — validation : pas de double signalement |
| `SellerReviewSummarySerializer` | `average_rating`, `reviews_count`, `top_tags` (3 plus fréquents) |

### Permissions custom

| Nom | Logique |
|-----|---------|
| `IsReviewedSeller` | `request.user == obj.seller` — le vendeur noté peut répondre à l'avis |

### Pages SSR

| Template | URL | Description |
|----------|-----|-------------|
| `reviews/seller_profile.html` | `/vendeur/<id>/` | Page profil vendeur : infos publiques, note moyenne, top tags, liste des avis avec réponses. Si connecté : formulaire pour laisser un avis. |
| `reviews/seller_reviews.html` | `/vendeur/<id>/avis/` | Liste complète des avis (paginée) si beaucoup d'avis |

#### Layout page profil vendeur

```
┌──────────────────────────────────────────────────────────┐
│  HEADER                                                   │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────┐  Nom du vendeur                         │
│  │   Avatar/   │  ⭐ 4.3/5 (12 avis)                    │
│  │   Logo      │  🏷️ Vendeur réactif · Bon prix · ...   │
│  └─────────────┘  📍 Tanger                              │
│                   [Badge Vérifié] (si boutique vérifiée)  │
├──────────────────────────────────────────────────────────┤
│  ANNONCES DU VENDEUR (grille 4 dernières)                │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                           │
│  └────┘ └────┘ └────┘ └────┘  [Voir toutes →]           │
├──────────────────────────────────────────────────────────┤
│  LAISSER UN AVIS (si connecté + pas son propre profil)   │
│  ⭐⭐⭐⭐⭐  [Tags à cocher]  [Commentaire]  [Envoyer]  │
├──────────────────────────────────────────────────────────┤
│  AVIS (5 derniers)                                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │ ⭐⭐⭐⭐⭐ Youssef · Il y a 3 jours                │  │
│  │ "Super vendeur, produit conforme !"                │  │
│  │ 🏷️ Produit conforme · Ponctuel                    │  │
│  │   └─ Réponse du vendeur : "Merci beaucoup !"      │  │
│  │   [Signaler]                                       │  │
│  └────────────────────────────────────────────────────┘  │
│  [Voir tous les avis →]                                  │
├──────────────────────────────────────────────────────────┤
│  FOOTER                                                   │
└──────────────────────────────────────────────────────────┘
```

#### Intégration dans la fiche produit

Sur `product_detail.html`, ajouter dans la section vendeur :
- Note moyenne + nombre d'avis (lien vers le profil vendeur)
- Top tags
- Badge vérifié (si boutique vérifiée)

#### Étoiles interactives (formulaire)

```html
<!-- 5 étoiles cliquables (JS simple) -->
<div class="flex gap-1" id="star-rating">
  <button data-value="1" class="text-gray-300 hover:text-amber-400 text-2xl">★</button>
  <button data-value="2" class="text-gray-300 hover:text-amber-400 text-2xl">★</button>
  ...
</div>
<input type="hidden" name="rating" id="rating-value" value="">
```

### Admin Django

- `ReviewTag` : list_display = (label,)
- `Review` : list_display = (reviewer, seller, rating, created_at), list_filter = (rating,), search = (reviewer__email, seller__email)
- `ReviewReply` : inline dans Review admin
- `ReviewReport` : list_display = (review, reporter, reason, status, created_at), list_filter = (reason, status), actions = (marquer traitée, rejeter)

### Settings à modifier

```python
INSTALLED_APPS += [
    'reviews',
]
```

### URLs à ajouter

```python
# monsetup/urls.py
path('api/v1/', include('reviews.urls_api')),
path('vendeur/', include('reviews.urls_ssr')),
```

### Fichiers à créer

```
reviews/
├── __init__.py
├── models.py              (ReviewTag, Review, ReviewReply, ReviewReport)
├── serializers.py
├── views.py               (API + SSR views)
├── urls_api.py
├── urls_ssr.py
├── permissions.py         (IsReviewedSeller)
├── admin.py
├── templates/
│   └── reviews/
│       ├── seller_profile.html
│       └── seller_reviews.html
└── migrations/
```

## Validations métier

- Un utilisateur ne peut laisser qu'**un seul avis par vendeur** (unique ensemble reviewer+seller). S'il soumet à nouveau, son avis est **modifié** (pas dupliqué).
- Un utilisateur **ne peut pas** laisser un avis sur lui-même.
- La note est un entier entre **1 et 5** (validation côté serveur).
- Le commentaire est **optionnel**, max `MAX_REVIEW_LENGTH` (500 caractères).
- Les tags sont sélectionnés parmi les `ReviewTag` existants en base (pas de texte libre).
- Le vendeur peut répondre **une seule fois** à chaque avis (OneToOne). Max `MAX_REPLY_LENGTH` (300 caractères).
- Un utilisateur ne peut signaler le même avis qu'**une seule fois**.
- Les `ReviewTag` sont administrés via le Django Admin (pas hardcodés).

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] `GET /api/v1/sellers/<id>/reviews/` retourne la liste paginée des avis
- [ ] `POST /api/v1/sellers/<id>/reviews/` crée/modifie un avis avec rating + tags
- [ ] `POST /api/v1/reviews/<id>/reply/` permet au vendeur de répondre
- [ ] `POST /api/v1/reviews/<id>/report/` signale un avis
- [ ] Page SSR `/vendeur/<id>/` affiche le profil vendeur avec avis
- [ ] Étoiles interactives fonctionnelles dans le formulaire
- [ ] Note moyenne + top tags affichés sur la fiche produit (product_detail.html)
- [ ] Admin Django : ReviewTag, Review, ReviewReply, ReviewReport
- [ ] Templates conformes au design system (`_design-system.md`)
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

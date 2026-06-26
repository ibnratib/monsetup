# Sprint 08 — Boost & Expiration + Page d'accueil + Page boutique

## Objectif

Finaliser le système de boost admin, la gestion automatique de l'expiration des boosts, les rappels d'annonces 30j (management command déjà créé au sprint 05 — vérifier/consolider), et créer les dernières pages SSR manquantes : page d'accueil et page boutique.

## Pré-requis

- Sprint 05 complété (Dashboard, Notification, management command `check_ad_reminders`)
- Sprint 06 complété (Tracking, Favoris)
- Sprint 07 complété (Reviews, profil vendeur)
- Lire `sprints/_design-system.md` pour le style des templates

## Livrables

### Partie 1 — Boost (admin-only au MVP)

#### Fonctionnalité

Le boost n'est **pas payable** par le vendeur au MVP. C'est l'admin qui active manuellement le boost depuis le Django Admin.

Champs déjà existants sur `Product` (sprint 03) :
- `is_boosted` (bool, default False)
- `boost_expires_at` (DateTimeField, nullable)

#### Management command

| Commande | Rôle |
|----------|------|
| `expire_boosts` | Désactive les boosts expirés : `Product.objects.filter(is_boosted=True, boost_expires_at__lte=now).update(is_boosted=False, boost_expires_at=None)` |

#### Admin amélioré

- Ajouter des **actions admin** sur `ProductAdmin` :
  - "Booster pour 7 jours" — met `is_boosted=True`, `boost_expires_at=now+7j`
  - "Booster pour 30 jours" — met `is_boosted=True`, `boost_expires_at=now+30j`
  - "Retirer le boost" — met `is_boosted=False`, `boost_expires_at=None`

### Partie 2 — Rappels d'expiration (consolidation)

Vérifier que `check_ad_reminders` (créé au sprint 05) fonctionne correctement :
- Crée une notification `RAPPEL_DISPONIBILITE` pour les annonces `DISPONIBLE` dont `updated_at < now - AD_REMINDER_DAYS`
- Ne crée pas de doublon si une notification non lue existe déjà

Si le management command n'existe pas ou est incomplet, le créer/compléter.

### Partie 3 — Page d'accueil

#### Template

| Template | URL | Description |
|----------|-----|-------------|
| `pages/home.html` | `/` | Page d'accueil du site |

#### Layout page d'accueil

```
┌──────────────────────────────────────────────────────────┐
│  HEADER                                                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  HERO SECTION                                            │
│  "Le marketplace tech de confiance"                      │
│  "Achetez et vendez du matériel tech en toute sécurité"  │
│  [Barre de recherche]              [Déposer une annonce] │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  CATÉGORIES (grille d'icônes)                            │
│  🖥️ PC Portables  🖥️ PC Bureau  🔧 Composants          │
│  🎮 Consoles      🎧 Périphériques  📱 Smartphones      │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  ANNONCES BOOSTÉES / MISES EN AVANT (carrousel ou grille)│
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                           │
│  │ ⚡ │ │ ⚡ │ │ ⚡ │ │ ⚡ │                           │
│  └────┘ └────┘ └────┘ └────┘                            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  DERNIÈRES ANNONCES                                      │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                           │
│  └────┘ └────┘ └────┘ └────┘                            │
│  [Voir toutes les annonces →]                            │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  POURQUOI SETUP.MA ? (3 colonnes)                        │
│  🔒 Catalogue vérifié  💬 WhatsApp direct  ⭐ Avis      │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  FOOTER                                                   │
└──────────────────────────────────────────────────────────┘
```

#### Contenu dynamique

- **Annonces boostées** : `Product.objects.filter(is_boosted=True, boost_expires_at__gt=now, status='DISPONIBLE')[:8]`
- **Dernières annonces** : `Product.objects.filter(status='DISPONIBLE').order_by('-created_at')[:8]`
- **Catégories racines** : `Category.objects.filter(parent__isnull=True).order_by('order')`
- **Barre de recherche** : formulaire GET vers `/annonces/?search=...`

### Partie 4 — Page boutique

#### Template

| Template | URL | Description |
|----------|-----|-------------|
| `accounts/boutique_page.html` | `/boutique/<slug>/` | Page vitrine publique d'une boutique |

#### Layout page boutique

```
┌──────────────────────────────────────────────────────────┐
│  HEADER                                                   │
├──────────────────────────────────────────────────────────┤
│  ┌─────────┐  Nom de la boutique                         │
│  │  Logo   │  📍 Ville · Adresse                         │
│  └─────────┘  ⭐ 4.5/5 (8 avis) · [Badge Vérifié]      │
│               📞 [Contacter via WhatsApp]                │
│               Description de la boutique                  │
├──────────────────────────────────────────────────────────┤
│  ANNONCES DE LA BOUTIQUE (grille, paginée)               │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                           │
│  └────┘ └────┘ └────┘ └────┘                            │
│  [Pagination]                                            │
├──────────────────────────────────────────────────────────┤
│  AVIS SUR LA BOUTIQUE (5 derniers)                       │
│  ⭐⭐⭐⭐⭐ "Très bon vendeur"                          │
│  [Voir tous les avis →] (lien vers /vendeur/<id>/)      │
├──────────────────────────────────────────────────────────┤
│  FOOTER                                                   │
└──────────────────────────────────────────────────────────┘
```

#### Vue SSR

| Vue | URL | Description |
|-----|-----|-------------|
| `BoutiquePageView` | `/boutique/<slug>/` | Affiche la boutique par slug. Context : boutique, produits paginés, reviews, stats (note moyenne, top tags) |

### URLs à ajouter

```python
# monsetup/urls.py
path('', HomePageView.as_view(), name='home'),
path('boutique/<slug:slug>/', BoutiquePageView.as_view(), name='boutique-page'),
```

### Fichiers à créer / modifier

```
pages/                         (CRÉER — ou mettre dans core)
├── views.py                   (HomePageView)
templates/
├── pages/
│   └── home.html              (CRÉER)
accounts/
├── views.py                   (MODIFIER — ajouter BoutiquePageView)
├── templates/
│   └── accounts/
│       └── boutique_page.html (CRÉER)
products/
├── admin.py                   (MODIFIER — ajouter actions boost)
dashboard/
├── management/
│   └── commands/
│       └── expire_boosts.py   (CRÉER)
```

### Settings

```python
INSTALLED_APPS — pas de nouvelle app si on met HomePageView dans core
```

## Validations métier

- Les annonces boostées avec `boost_expires_at` passé sont automatiquement désactivées par `expire_boosts`.
- La page d'accueil ne montre que les annonces `DISPONIBLE`.
- La page boutique ne montre que les annonces `DISPONIBLE` de cette boutique.
- La page boutique est accessible par slug (`/boutique/<slug>/`).
- Le badge "Vérifié" n'apparaît que si `statut_verification == 'VERIFIE'`.
- Seul l'admin peut booster/débooster une annonce (pas le vendeur).

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py migrate` fonctionne sans erreur
- [ ] Actions admin "Booster 7j / 30j / Retirer boost" fonctionnelles
- [ ] `python manage.py expire_boosts` désactive les boosts expirés
- [ ] `python manage.py check_ad_reminders` crée les notifications de rappel (vérifié/consolidé)
- [ ] Page d'accueil `/` : hero, catégories, annonces boostées, dernières annonces
- [ ] Barre de recherche sur la page d'accueil redirige vers `/annonces/?search=...`
- [ ] Page boutique `/boutique/<slug>/` : infos, annonces, avis
- [ ] Badge vérifié affiché correctement
- [ ] Templates conformes au design system (`_design-system.md`)
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

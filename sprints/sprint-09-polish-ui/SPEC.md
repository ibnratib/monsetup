# Sprint 09 — Polish UI/UX + Cohérence design system

## Objectif

Dernier sprint. Aligner **tous** les templates existants sur le design system (`_design-system.md`), corriger les incohérences visuelles, améliorer la navigation mobile, et s'assurer que l'ensemble de l'application est fluide et cohérent.

## Pré-requis

- Sprints 01-08 tous complétés
- Lire **obligatoirement** `sprints/_design-system.md` — c'est la référence absolue pour ce sprint

## Livrables

### 1. Audit et refactoring de TOUS les templates

Passer en revue **chaque template** et l'aligner sur le design system :

| Template | Fichier | Points à vérifier |
|----------|---------|-------------------|
| Base | `templates/base.html` | Header responsive (hamburger mobile), footer, couleurs blue-600, font system |
| Accueil | `templates/pages/home.html` | Hero, catégories, cartes produit, CTA, responsive |
| Listing | `products/templates/products/product_list.html` | Sidebar filtres (drawer mobile), grille 2/3/4 cols, cartes produit |
| Détail produit | `products/templates/products/product_detail.html` | Layout 2 cols desktop / 1 col mobile, carrousel, bouton WhatsApp vert, attributs |
| Dépôt annonce | `products/templates/products/product_create.html` | Formulaire centré, sections cartes blanches, inputs stylés |
| Dashboard home | `dashboard/templates/dashboard/dashboard_home.html` | Stats cards, sidebar, responsive |
| Mes annonces | `dashboard/templates/dashboard/my_products.html` | Tableau/cards responsive, badges statut |
| Notifications | `dashboard/templates/dashboard/notifications.html` | Liste propre, badges lu/non-lu |
| Favoris | `dashboard/templates/dashboard/favorites.html` | Grille de cartes, bouton retirer |
| Inscription choix | `accounts/templates/accounts/register_choice.html` | 2 cartes centrées |
| Inscription particulier | `accounts/templates/accounts/register_particulier.html` | Formulaire centré, inputs stylés |
| Inscription boutique | `accounts/templates/accounts/register_boutique.html` | Formulaire centré, dropdown ville |
| Connexion | `accounts/templates/accounts/login.html` | Formulaire centré, simple |
| Profil vendeur | `reviews/templates/reviews/seller_profile.html` | Layout profil, étoiles, tags, avis |
| Avis vendeur | `reviews/templates/reviews/seller_reviews.html` | Liste paginée |
| Page boutique | `accounts/templates/accounts/boutique_page.html` | Vitrine, badge vérifié, annonces, avis |

### 2. Navigation mobile (hamburger menu)

Le `base.html` doit avoir un menu hamburger fonctionnel sur mobile :

```html
<!-- Mobile menu button -->
<button id="mobile-menu-btn" class="lg:hidden p-2 text-gray-600 hover:text-blue-600">
  <svg class="w-6 h-6"><!-- hamburger icon --></svg>
</button>

<!-- Mobile menu drawer -->
<div id="mobile-menu" class="hidden lg:hidden fixed inset-0 z-50 bg-black/50">
  <div class="bg-white w-64 h-full p-6 shadow-xl">
    <button id="mobile-menu-close" class="absolute top-4 right-4">✕</button>
    <nav class="mt-8 flex flex-col gap-4">
      <a href="/">Accueil</a>
      <a href="/annonces/">Annonces</a>
      {% if user.is_authenticated %}
        <a href="/annonces/deposer/">Déposer</a>
        <a href="/dashboard/">Dashboard</a>
        <a href="/deconnexion/">Déconnexion</a>
      {% else %}
        <a href="/connexion/">Connexion</a>
        <a href="/inscription/">S'inscrire</a>
      {% endif %}
    </nav>
  </div>
</div>
```

### 3. Sidebar filtres en drawer sur mobile

Sur la page listing (`product_list.html`), les filtres doivent passer en drawer/modal sur mobile :
- **Desktop (lg+)** : sidebar visible à gauche
- **Mobile/tablette** : bouton "Filtrer" qui ouvre un drawer latéral ou modal

### 4. Formatage prix

S'assurer que **partout** le prix est affiché en format `X XXX DH` :
- Créer un template filter `{% load setup_filters %}` → `{{ product.price|format_price }}`
- Utiliser ce filtre dans tous les templates qui affichent un prix

```python
# core/templatetags/setup_filters.py
from django import template
import locale

register = template.Library()

@register.filter
def format_price(value):
    """Formate un prix en DH avec séparateur de milliers."""
    try:
        formatted = f"{int(value):,}".replace(",", " ")
        return f"{formatted} DH"
    except (ValueError, TypeError):
        return f"{value} DH"
```

### 5. Dates relatives

S'assurer que les dates sont affichées en format relatif :
- Créer un template filter `{{ product.created_at|time_since_fr }}`

```python
@register.filter
def time_since_fr(value):
    """Affiche le temps écoulé en français."""
    from django.utils import timezone
    now = timezone.now()
    diff = now - value
    
    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            return f"Il y a {minutes} min" if minutes > 0 else "À l'instant"
        return f"Il y a {hours}h"
    elif diff.days == 1:
        return "Hier"
    elif diff.days < 7:
        return f"Il y a {diff.days} jours"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"Il y a {weeks} sem."
    else:
        return value.strftime("%d %b %Y")
```

### 6. Images placeholder

Quand un produit n'a pas d'image, afficher un placeholder cohérent :

```html
<div class="aspect-[4/3] bg-gray-100 flex items-center justify-center">
  <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
</div>
```

### 7. Messages flash (succès/erreur)

Ajouter dans `base.html` l'affichage des messages Django :

```html
{% if messages %}
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
    {% for message in messages %}
      <div class="p-4 rounded-lg mb-2 text-sm
        {% if message.tags == 'success' %}bg-green-50 border border-green-200 text-green-800
        {% elif message.tags == 'error' %}bg-red-50 border border-red-200 text-red-800
        {% else %}bg-blue-50 border border-blue-200 text-blue-800{% endif %}">
        {{ message }}
      </div>
    {% endfor %}
  </div>
{% endif %}
```

### 8. Carrousel images (fiche produit)

Implémenter un carrousel simple en JS natif sur la fiche produit :
- Navigation gauche/droite
- Indicateurs de position (dots)
- Image cliquable (zoom ou lightbox basique)
- Responsive (pleine largeur sur mobile)

### Fichiers à créer / modifier

```
core/
├── templatetags/
│   ├── __init__.py
│   └── setup_filters.py      (CRÉER — format_price, time_since_fr)
templates/
├── base.html                  (MODIFIER — hamburger, messages flash)
├── pages/
│   └── home.html              (MODIFIER — aligner design system)
products/templates/products/
├── product_list.html          (MODIFIER — drawer filtres mobile)
├── product_detail.html        (MODIFIER — carrousel, formatage)
├── product_create.html        (MODIFIER — style formulaire)
dashboard/templates/dashboard/
├── *.html                     (MODIFIER — aligner design system)
accounts/templates/accounts/
├── *.html                     (MODIFIER — aligner design system)
reviews/templates/reviews/
├── *.html                     (MODIFIER — aligner design system)
```

## Validations

- Tous les templates utilisent les classes Tailwind du design system (blue-600, rounded-xl, etc.)
- Le header est responsive avec hamburger menu fonctionnel
- Les filtres sont en drawer sur mobile
- Les prix sont formatés `X XXX DH` partout
- Les dates sont en format relatif français partout
- Les images placeholder sont affichées quand pas d'image
- Les messages flash s'affichent correctement
- Le carrousel d'images fonctionne sur la fiche produit

## Contrat de sortie (Definition of Done)

- [ ] `python manage.py check` passe sans erreur
- [ ] Tous les templates alignés sur `_design-system.md`
- [ ] Menu hamburger fonctionnel sur mobile
- [ ] Filtres en drawer sur mobile
- [ ] Template filter `format_price` utilisé partout
- [ ] Template filter `time_since_fr` utilisé partout
- [ ] Placeholder images cohérent
- [ ] Messages flash dans base.html
- [ ] Carrousel images sur fiche produit
- [ ] Navigation cohérente sur toutes les pages
- [ ] `_registry.md` mis à jour
- [ ] `DONE.md` rédigé

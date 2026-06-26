# Sprint 09 — Polish UI/UX + Cohérence design system — DONE

## Résumé

Dernier sprint de polish. Tous les templates ont été alignés sur le design system (`_design-system.md`), la navigation mobile est fonctionnelle, et les filtres sont accessibles sur tous les formats d'écran.

## Livrables réalisés

### 1. Template filters (`core/templatetags/setup_filters.py`)

- **`format_price`** : Formate les prix en `X XXX DH` avec séparateur de milliers
- **`time_since_fr`** : Affiche les dates en format relatif français (À l'instant, Il y a 2h, Hier, Il y a 3 jours, Il y a 2 sem., 15 jan 2026)
- Utilisés dans **tous** les templates qui affichent un prix ou une date

### 2. Navigation mobile — Hamburger menu (`base.html`)

- Header rendu sticky (`sticky top-0 z-40`)
- Logo avec accent ⚡ (`⚡ Setup.ma`)
- Desktop : navigation inline classique (hidden on mobile)
- Mobile : bouton hamburger → drawer latéral avec overlay semi-transparent
- Le drawer inclut tous les liens : Accueil, Annonces, Déposer, Dashboard, Favoris, Notifications, Déconnexion
- JavaScript natif pour open/close avec blocage du scroll body

### 3. Messages flash (`base.html`)

- Support des messages Django (`django.contrib.messages`) affiché entre le header et le contenu
- Styles différenciés : success (vert), error (rouge), warning (ambre), info (bleu)
- Classes alignées sur le design system

### 4. Footer enrichi (`base.html`)

- Footer restructuré en 2 colonnes (Setup.ma, Compte) avec liens utiles
- Séparation visuelle (`border-t`) et copyright

### 5. Sidebar filtres en drawer sur mobile (`product_list.html`)

- **Desktop (lg+)** : sidebar filtres visible à gauche comme avant
- **Mobile/tablette** : bouton "Filtrer" en haut de page qui ouvre un drawer latéral
- Overlay semi-transparent + bouton fermer
- JavaScript natif pour toggle

### 6. Carrousel images amélioré (`product_detail.html`)

- Boutons précédent/suivant plus visibles (w-10 h-10, shadow-md)
- Indicateurs de position (dots) en bas du carrousel
- Mise à jour automatique des dots au scroll
- Clic sur une image ouvre un lightbox plein écran
- Lightbox avec fermeture par clic sur overlay ou bouton ✕

### 7. Image placeholders cohérents

- Remplacement de tous les émojis 📷 par un SVG cohérent (icône paysage/photo)
- SVG uniforme `w-12 h-12 text-gray-300` dans tous les templates
- Utilisé dans : home, product_list, product_detail, favorites, seller_profile, boutique_page

### 8. Formulaire dépôt — Ville en select (`product_create.html`)

- Champ ville transformé de `input[type=number]` en `<select>` avec liste des villes
- Vue `ProductCreateView` mise à jour pour passer les cities dans le contexte GET et POST

### 9. CSS utilitaire

- Ajout de `scrollbar-hide` CSS utility pour le carrousel
- Bloc `{% block extra_js %}` ajouté dans base.html pour les scripts spécifiques

### 10. Audit complet des templates

Tous les templates suivants ont été vérifiés et alignés sur le design system :

| Template | Modifications |
|----------|--------------|
| `base.html` | Hamburger menu, messages flash, footer enrichi, sticky header |
| `pages/home.html` | `format_price`, `time_since_fr`, SVG placeholders |
| `product_list.html` | Drawer filtres mobile, `format_price`, `time_since_fr`, SVG placeholder |
| `product_detail.html` | Carrousel avec dots + lightbox, `format_price`, `time_since_fr`, SVG placeholder |
| `product_create.html` | Ville en select dropdown |
| `dashboard_home.html` | `format_price`, `time_since_fr` |
| `my_products.html` | `format_price`, `time_since_fr` |
| `notifications.html` | `time_since_fr` |
| `favorites.html` | `format_price`, SVG placeholder |
| `register_choice.html` | Déjà conforme |
| `register_particulier.html` | Déjà conforme |
| `register_boutique.html` | Déjà conforme |
| `login.html` | Déjà conforme |
| `seller_profile.html` | `format_price`, `time_since_fr`, SVG placeholder |
| `seller_reviews.html` | `time_since_fr` |
| `boutique_page.html` | `format_price`, `time_since_fr`, SVG placeholder |

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `core/templatetags/__init__.py` | Package init |
| `core/templatetags/setup_filters.py` | Filtres `format_price` et `time_since_fr` |

## Fichiers modifiés

| Fichier | Nature |
|---------|--------|
| `templates/base.html` | Hamburger menu, messages flash, footer, sticky header |
| `templates/pages/home.html` | Filtres, placeholders |
| `products/templates/products/product_list.html` | Drawer filtres mobile |
| `products/templates/products/product_detail.html` | Carrousel + lightbox |
| `products/templates/products/product_create.html` | Ville select |
| `products/views.py` | Ajout cities au contexte ProductCreateView |
| `dashboard/templates/dashboard/*.html` | Filtres format_price/time_since_fr |
| `accounts/templates/accounts/boutique_page.html` | Filtres, placeholders |
| `reviews/templates/reviews/*.html` | Filtres, placeholders |

## Contrat de sortie

- [x] `python manage.py check` passe sans erreur
- [x] Tous les templates alignés sur `_design-system.md`
- [x] Menu hamburger fonctionnel sur mobile
- [x] Filtres en drawer sur mobile
- [x] Template filter `format_price` utilisé partout
- [x] Template filter `time_since_fr` utilisé partout
- [x] Placeholder images cohérent (SVG)
- [x] Messages flash dans base.html
- [x] Carrousel images avec dots + lightbox sur fiche produit
- [x] Navigation cohérente sur toutes les pages
- [x] `_registry.md` mis à jour
- [x] `DONE.md` rédigé

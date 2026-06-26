# Design System — Setup.ma

> Ce fichier définit les conventions visuelles du projet. L'IA DOIT le consulter avant tout travail sur les templates.

## Identité visuelle

- **Style** : Minimaliste / Clean — inspiré Leboncoin & Vinted mais avec une identité tech/gaming propre
- **Ton** : Professionnel mais accessible, fiable (marketplace de confiance)
- **Mode** : Light mode uniquement (MVP)
- **Framework CSS** : Tailwind CSS (CDN en dev, build en prod)

## Palette de couleurs

### Couleurs principales (Tailwind classes)

| Rôle | Couleur | Tailwind class | Hex |
|------|---------|---------------|-----|
| **Primaire** | Bleu électrique | `blue-600` | #2563eb |
| **Primaire hover** | Bleu foncé | `blue-700` | #1d4ed8 |
| **Primaire light** | Bleu clair (fond) | `blue-50` | #eff6ff |
| **Secondaire** | Gris foncé | `gray-800` | #1f2937 |
| **Texte principal** | Quasi noir | `gray-900` | #111827 |
| **Texte secondaire** | Gris moyen | `gray-500` | #6b7280 |
| **Fond page** | Gris très clair | `gray-50` | #f9fafb |
| **Fond carte** | Blanc | `white` | #ffffff |
| **Bordures** | Gris léger | `gray-200` | #e5e7eb |
| **Succès** | Vert | `green-600` | #16a34a |
| **Erreur** | Rouge | `red-600` | #dc2626 |
| **Warning** | Ambre | `amber-500` | #f59e0b |
| **Boost badge** | Ambre fond | `amber-100` + `amber-700` text | — |
| **Badge vérifié** | Bleu fond | `blue-100` + `blue-700` text | — |

### Utilisation stricte

- **Boutons primaires** : `bg-blue-600 hover:bg-blue-700 text-white`
- **Boutons secondaires** : `bg-white border border-gray-300 hover:bg-gray-50 text-gray-700`
- **Boutons danger** : `bg-red-600 hover:bg-red-700 text-white`
- **Liens** : `text-blue-600 hover:text-blue-700 hover:underline`
- **Fond page** : `bg-gray-50`
- **Cartes** : `bg-white rounded-xl shadow-sm border border-gray-200`

## Typographie

- **Font** : System font stack (pas de Google Fonts pour la perf)
  ```
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  ```
  Tailwind : pas besoin de config, utiliser la font par défaut de Tailwind (`font-sans`)

- **Tailles** :
  - Titre page : `text-2xl font-bold` (mobile) / `text-3xl font-bold` (desktop)
  - Titre section : `text-xl font-semibold`
  - Titre carte : `text-lg font-medium`
  - Corps : `text-sm` (14px) ou `text-base` (16px)
  - Labels/meta : `text-xs text-gray-500`
  - Prix : `text-xl font-bold text-gray-900`

## Composants récurrents

### Carte produit (listing)

```html
<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
  <!-- Image -->
  <div class="aspect-[4/3] bg-gray-100 overflow-hidden">
    <img class="w-full h-full object-cover" src="..." alt="...">
  </div>
  <!-- Contenu -->
  <div class="p-4">
    <h3 class="text-sm font-medium text-gray-900 line-clamp-2">Titre</h3>
    <p class="mt-1 text-lg font-bold text-gray-900">1 500 DH</p>
    <div class="mt-2 flex items-center gap-2 text-xs text-gray-500">
      <span>Tanger</span>
      <span>·</span>
      <span>Il y a 2h</span>
    </div>
  </div>
</div>
```

### Bouton primaire

```html
<button class="inline-flex items-center px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors">
  Déposer une annonce
</button>
```

### Bouton secondaire

```html
<button class="inline-flex items-center px-4 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg transition-colors">
  Filtrer
</button>
```

### Bouton WhatsApp (CTA principal sur fiche produit)

```html
<a href="..." class="inline-flex items-center justify-center w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white text-base font-medium rounded-xl transition-colors gap-2">
  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><!-- WhatsApp icon --></svg>
  Contacter via WhatsApp
</a>
```

### Badge statut

```html
<!-- Disponible -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Disponible</span>
<!-- Vendu -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Vendu</span>
<!-- Boosté -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">⚡ Boosté</span>
<!-- Vérifié -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">✓ Vérifié</span>
```

### Input / Select

```html
<input class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
<select class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
```

### Champ avec label

```html
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">Nom du champ</label>
  <input class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
</div>
```

### Message d'erreur (formulaire)

```html
<p class="mt-1 text-sm text-red-600">Ce champ est obligatoire.</p>
```

### Alerte succès / erreur

```html
<!-- Succès -->
<div class="p-4 rounded-lg bg-green-50 border border-green-200 text-green-800 text-sm">Message de succès.</div>
<!-- Erreur -->
<div class="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">Message d'erreur.</div>
```

## Layout

### Header (navigation)

```
┌─────────────────────────────────────────────────────────────┐
│  Logo Setup.ma          [Annonces]  [Déposer] [Connexion]   │
└─────────────────────────────────────────────────────────────┘
```

- **Desktop** : header fixe en haut, max-w-7xl centré
- **Mobile** : hamburger menu ou navigation simplifiée
- Logo : texte `Setup.ma` en `text-xl font-bold text-blue-600` + petit accent (ex: icône ⚡ ou 🖥️)
- Background : `bg-white shadow-sm`

### Page listing

```
┌──────────────────────────────────────────────────────────────┐
│  HEADER                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ FILTRES  │  GRILLE PRODUITS                                  │
│ (sidebar)│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │
│          │  │     │ │     │ │     │ │     │               │
│ Catégorie│  └─────┘ └─────┘ └─────┘ └─────┘               │
│ Ville    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐               │
│ Prix     │  │     │ │     │ │     │ │     │               │
│ ...      │  └─────┘ └─────┘ └─────┘ └─────┘               │
│          │                                                   │
│          │  [Pagination]                                     │
├──────────┴───────────────────────────────────────────────────┤
│  FOOTER                                                       │
└──────────────────────────────────────────────────────────────┘
```

- **Desktop** : sidebar filtres (w-64) à gauche + grille 4 colonnes
- **Tablette** : filtres collapsés en haut + grille 3 colonnes
- **Mobile** : filtres dans un drawer/modal + grille 2 colonnes

Grille : `grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4`

### Page fiche produit

```
┌──────────────────────────────────────────────────────────────┐
│  HEADER                                                       │
├──────────────────────┬───────────────────────────────────────┤
│  GALERIE IMAGES      │  INFOS PRODUIT                        │
│  (carrousel)         │  Titre                                │
│                      │  Prix (gros, bold)                    │
│                      │  Ville · Date                         │
│                      │  [Bouton WhatsApp]                    │
│                      │  Vendeur (type + nom)                 │
├──────────────────────┴───────────────────────────────────────┤
│  ATTRIBUTS TECHNIQUES (grille 2 cols)                        │
│  RAM: 16 Go  |  Stockage: 512 Go SSD                       │
│  GPU: RTX 4060  |  Processeur: i7-13700H                   │
├──────────────────────────────────────────────────────────────┤
│  DESCRIPTION COMPLÉMENTAIRE                                  │
├──────────────────────────────────────────────────────────────┤
│  FOOTER                                                       │
└──────────────────────────────────────────────────────────────┘
```

- **Desktop** : 2 colonnes (images à gauche 60%, infos à droite 40%)
- **Mobile** : 1 colonne empilée (images → prix/CTA → attributs → description)

### Formulaire dépôt

- 1 colonne centrée (max-w-2xl)
- Sections séparées visuellement (cartes blanches)
  1. Catégorie (dropdown)
  2. Infos de base (titre, prix, ville, adresse, description)
  3. Attributs techniques (champs dynamiques selon catégorie)
  4. Photos (upload drag & drop ou sélection)
  5. Bouton "Publier l'annonce"

## Responsive breakpoints

| Breakpoint | Tailwind | Usage |
|-----------|----------|-------|
| Mobile | `< sm` (< 640px) | 2 cols grille, menu hamburger, CTA full-width |
| Tablette | `sm` - `lg` (640-1024px) | 3 cols grille, filtres collapsés |
| Desktop | `lg+` (> 1024px) | 4 cols grille, sidebar filtres visible |

## Animations / Transitions

- **Hover cartes** : `hover:shadow-md transition-shadow duration-200`
- **Boutons** : `transition-colors duration-150`
- **Menus/modales** : `transition-all duration-200`
- Pas d'animation lourde — garder la performance.

## Icônes

- Utiliser **Heroicons** (SVG inline via Tailwind) : https://heroicons.com/
- Inclure via SVG inline dans les templates (pas de font icon)
- Taille standard : `w-5 h-5` pour les boutons, `w-4 h-4` pour les badges/meta

## Images produit

- **Ratio** : 4:3 (`aspect-[4/3]`)
- **Fit** : `object-cover` (jamais déformé)
- **Placeholder** : fond `bg-gray-100` avec icône photo en `text-gray-300` si pas d'image
- **Carrousel fiche** : images cliquables, navigation gauche/droite (simple JS)

## Formatage des données

- **Prix** : toujours affiché `X XXX DH` (espace comme séparateur de milliers, "DH" comme unité)
- **Dates** : format relatif ("Il y a 2h", "Il y a 3 jours", "12 juin 2026")
- **Téléphone** : jamais affiché en clair — uniquement via bouton WhatsApp

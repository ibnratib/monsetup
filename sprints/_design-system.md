# Design System — Setup.ma

> Ce fichier définit les conventions visuelles du projet. L'IA DOIT le consulter avant tout travail sur les templates.

## Identité visuelle

- **Style** : Tech-forward / Premium — identité forte de marketplace gaming/tech, immédiatement reconnaissable
- **Ton** : Moderne, fiable, communautaire (marketplace de confiance pour la tech)
- **Mode** : Light mode avec header/footer dark (slate-900)
- **Framework CSS** : Tailwind CSS (CDN en dev avec config custom, build en prod)
- **Font** : Inter (Google Fonts) — `font-sans` configuré via tailwind.config

## Palette de couleurs

### Couleurs principales (Tailwind classes)

| Rôle | Couleur | Tailwind class | Hex |
|------|---------|---------------|-----|
| **Primaire** | Indigo | `indigo-600` | #4f46e5 |
| **Primaire hover** | Indigo clair | `indigo-500` | #6366f1 |
| **Primaire light** | Indigo fond | `indigo-50` | #eef2ff |
| **Accent / Prix** | Emerald | `emerald-600` | #059669 |
| **Accent CTA** | Emerald vif | `emerald-500` | #10b981 |
| **Accent hover** | Emerald clair | `emerald-400` | #34d399 |
| **Dark (header/footer)** | Slate foncé | `slate-900` | #0f172a |
| **Texte principal** | Slate quasi noir | `slate-900` | #0f172a |
| **Texte secondaire** | Slate moyen | `slate-500` | #64748b |
| **Fond page** | Slate très clair | `slate-50` | #f8fafc |
| **Fond carte** | Blanc | `white` | #ffffff |
| **Bordures** | Slate léger | `slate-200` | #e2e8f0 |
| **Succès** | Emerald | `emerald-600` | #059669 |
| **Erreur** | Rouge | `red-600` | #dc2626 |
| **Warning** | Ambre | `amber-500` | #f59e0b |
| **Boost badge** | Ambre fond | `amber-400/90` + `amber-900` text | — |
| **Badge vérifié** | Indigo fond | `indigo-100` + `indigo-700` text | — |

### Utilisation stricte

- **Boutons primaires** : `bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl`
- **Boutons accent (CTA)** : `bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-semibold rounded-xl`
- **Boutons secondaires** : `bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl`
- **Boutons danger** : `bg-red-600 hover:bg-red-500 text-white rounded-xl`
- **Liens** : `text-indigo-600 hover:text-indigo-500`
- **Fond page** : `bg-slate-50`
- **Cartes** : `bg-white rounded-2xl shadow-sm` (pas de border explicite)
- **Prix** : `text-emerald-600 font-bold` (distinction clé vs concurrents)

## Éléments de signature

1. **Header dark** avec gradient-line (indigo → emerald) en haut
2. **Logo** : "Setup" blanc bold + ".ma" emerald-400 — `text-xl font-extrabold`
3. **Hero** : fond slate-900 avec radial-gradients indigo/emerald en opacité
4. **Cards** : `card-hover` class (translateY(-2px) + shadow augmenté au hover)
5. **Prix en emerald** : les prix ressortent immédiatement visuellement

## Typographie

- **Font** : Inter (Google Fonts) via Tailwind config
  ```
  fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'] }
  ```

- **Tailles** :
  - Titre page : `text-2xl font-extrabold` (mobile) / `text-3xl font-extrabold` (desktop)
  - Titre section : `text-xl font-bold`
  - Titre carte : `text-sm font-medium`
  - Corps : `text-sm` (14px) ou `text-base` (16px)
  - Labels/meta : `text-xs text-slate-500`
  - Prix : `text-lg font-bold text-emerald-600`

## Composants récurrents

### Carte produit (listing)

```html
<a class="bg-white rounded-2xl overflow-hidden card-hover block shadow-sm">
  <!-- Image -->
  <div class="aspect-[4/3] bg-slate-100 overflow-hidden">
    <img class="w-full h-full object-cover" src="..." alt="...">
  </div>
  <!-- Contenu -->
  <div class="p-4">
    <h3 class="text-sm font-medium text-slate-900 line-clamp-2">Titre</h3>
    <p class="mt-1 text-lg font-bold text-emerald-600">1 500 DH</p>
    <div class="mt-2 flex items-center gap-2 text-xs text-slate-500">
      <span>Tanger</span>
      <span>·</span>
      <span>Il y a 2h</span>
    </div>
  </div>
</a>
```

### Bouton primaire

```html
<button class="inline-flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-colors">
  Appliquer
</button>
```

### Bouton accent (CTA header/hero)

```html
<a class="inline-flex items-center px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-900 text-sm font-semibold rounded-lg transition-colors">
  + Déposer
</a>
```

### Bouton secondaire

```html
<button class="inline-flex items-center px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-sm font-medium rounded-xl transition-colors">
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
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Disponible</span>
<!-- Vendu -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Vendu</span>
<!-- Boosté -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-400/90 text-amber-900">⚡ Boosté</span>
<!-- Vérifié -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">✓ Vérifié</span>
```

### Input / Select

```html
<input class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
<select class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
```

### Champ avec label

```html
<div>
  <label class="block text-sm font-medium text-slate-700 mb-1">Nom du champ</label>
  <input class="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent" />
</div>
```

### Message d'erreur (formulaire)

```html
<p class="mt-1 text-sm text-red-600">Ce champ est obligatoire.</p>
```

### Alerte succès / erreur

```html
<!-- Succès -->
<div class="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium">Message de succès.</div>
<!-- Erreur -->
<div class="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm font-medium">Message d'erreur.</div>
```

## Layout

### Header (navigation)

```
┌─────────────────────────────────────────────────────────────┐
│ ═══ gradient-line (indigo → emerald) ═══                    │
│  Setup.ma               [Annonces] [+ Déposer] [S'inscrire] │
└─────────────────────────────────────────────────────────────┘
```

- **Desktop** : header fixe dark (bg-slate-900) en haut, max-w-7xl centré
- **Mobile** : hamburger menu drawer (dark)
- Logo : `<span class="text-white">Setup</span><span class="text-emerald-400">.ma</span>` — `text-xl font-extrabold`
- Background : `bg-slate-900` avec `gradient-line` en border-top (indigo → emerald)

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

- **Hover cartes** : `card-hover` class → `transform: translateY(-2px); box-shadow: 0 12px 24px -8px rgba(0,0,0,0.12);`
- **Boutons** : `transition-colors duration-150`
- **Menus/modales** : `transition-all duration-200`, backdrop `backdrop-blur-sm`
- **Header gradient-line** : `background: linear-gradient(90deg, #6366f1, #10b981);`

## CSS Custom (dans `<style>` du base.html)

```css
.gradient-line { background: linear-gradient(90deg, #6366f1, #10b981); }
.card-hover { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.card-hover:hover { transform: translateY(-2px); box-shadow: 0 12px 24px -8px rgba(0,0,0,0.12); }
```

## Tailwind Config (CDN)

```javascript
tailwind.config = {
    theme: {
        extend: {
            fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'] },
        }
    }
}
```
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

# Index des sprints — Setup.ma

## Graphe de dépendances

```
Sprint 01 (Fondations)
    ├── Sprint 02 (Catalogue EAV)
    │       └── Sprint 03 (Produits)
    │               ├── Sprint 04 (Listing & Filtres)
    │               ├── Sprint 05 (Dashboard vendeur)
    │               ├── Sprint 06 (Interactions : favoris, signalements, tracking)
    │               └── Sprint 08 (Boost & Expiration)
    └── Sprint 07 (Avis vendeurs)

Sprint 09 (Frontend SSR) ← dépend de tous les sprints précédents
```

## Tableau des sprints

| # | Sprint | Statut | Dépend de | Exports (ce que ce sprint produit) |
|---|--------|--------|-----------|-------------------------------------|
| 01 | Fondations | ✅ Terminé | — | `User`, `Particulier`, `Boutique`, config DRF, JWT, structure apps |
| 02 | Catalogue EAV + Localisation | ✅ Terminé | 01 | `City`, `Category`, `AttributeDefinition`, `AttributeChoice`, admin catalog, FK ville sur Boutique |
| 03 | Produits + Images + Pages SSR | ✅ Terminé | 01, 02 | `Product`, `ProductImage`, `ProductAttributeValue`, `DynamicProductCreateSerializer`, compression images, pages listing/détail/dépôt |
| 04 | Listing & Filtres | ✅ Terminé | 03 | Filtres django-filter, filtres EAV dynamiques, recherche texte, tri, boost en premier, page SSR filtres |
| 05 | Dashboard vendeur | ✅ Terminé | 03 | My-products, stats (vues, clics WA), changement statut, notifications |
| 06 | Auth SSR + Interactions | ✅ Terminé | 03, 05 | Pages inscription/connexion, favoris, signalements, tracking vues/WhatsApp |
| 07 | Avis vendeurs | ✅ Terminé | 01 | `Review`, `ReviewReply`, notes, tags, réponse vendeur, signalement avis |
| 08 | Boost & Pages finales | ✅ Terminé | 03, 05, 07 | Actions admin boost, expire_boosts, page d'accueil, page boutique |
| 09 | Polish UI/UX | ✅ Terminé | 01-08 | Refactoring design system, hamburger mobile, drawer filtres, format prix/dates, carrousel, messages flash |

## Statuts possibles

- ⬜ À faire
- 🔄 En cours
- ✅ Terminé

## Sprints parallélisables

Les sprints **04, 05, 06, 07** peuvent être implémentés dans n'importe quel ordre (dépendent de 03 ou 01, mais pas entre eux).

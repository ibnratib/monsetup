# Instructions générales — Projet Setup.ma

## Contexte du produit

Setup.ma est une marketplace d'annonces **de niche**, dédiée à la communauté tech : gamers, développeurs, designers, professionnels IT. Contrairement à un site généraliste comme Avito, Setup.ma se positionne comme un **"Safe Space" de confiance** grâce à un catalogue propre et standardisé.

**Catégories autorisées uniquement** : PC Portables (Gaming, MacBook/Apple, Ultrabook Pro), PC de Bureau, Composants (GPU, CPU, cartes mères, RAM, stockage, boîtiers/alim), Consoles & Jeux, Périphériques & Audio, Smartphones Premium (iPhone 11+, Samsung S/Fold, Google Pixel).

**Modèle économique** : Asset-Light. Coûts d'infrastructure proches de 0 DH (Azure Free Tier, SQLite en dev → PostgreSQL/Neon en prod). Lancement par marketing terrain (étudiants ENSA/FST, gaming centers, 5-10 boutiques partenaires à Tanger).

## Stack technique

- **Backend** : Django + Django REST Framework (architecture API-first, apps séparées : `accounts`, `catalog`, `products`, `dashboard`, `core`)
- **API** : REST API complète (JSON) — conçue pour être consommée par le frontend web ET une future application mobile
- **Base de données** : SQLite en dev → PostgreSQL (Neon, tier gratuit) en prod
- **Frontend web** : Application séparée consommant l'API REST (Templates Django + HTMX pour le MVP, migrable vers un SPA plus tard)
- **Style** : Tailwind CSS
- **Stockage images** : local en dev → Azure Blob Storage en prod
- **Auth** : Token-based (JWT via `djangorestframework-simplejwt`) — compatible web et mobile

### Principe API-First

Toute la logique métier est exposée via des endpoints REST. Le frontend web n'est qu'un **client** parmi d'autres. Cette architecture permet :
- La réutilisation du même backend pour une application mobile (React Native, Flutter, etc.)
- Une séparation claire entre logique métier (backend) et présentation (frontend)
- Des tests d'intégration via les endpoints API
- Une documentation auto-générée (drf-spectacular / Swagger)

### Conventions REST

- Versionner l'API : tous les endpoints sous `/api/v1/`
- Utiliser les Serializers DRF pour la validation (jamais de `ModelForm` dans le contexte API)
- ViewSets + Routers pour les endpoints CRUD standards
- Permissions DRF (`IsAuthenticated`, `IsOwner`, etc.) pour l'isolation des données
- Pagination systématique sur les endpoints de listing
- Filtrage via `django-filter` intégré à DRF

## ⚠️ Design System

Avant tout travail sur les templates HTML, **lire obligatoirement** `sprints/_design-system.md`.

Résumé :
- **Style** : Minimaliste / Clean, light mode, Tailwind CSS
- **Couleur primaire** : `blue-600` (#2563eb)
- **Cartes** : `bg-white rounded-xl shadow-sm border border-gray-200`
- **Responsive** : mobile-first (2 cols → 3 cols → 4 cols)
- **Font** : system font stack (Tailwind default)
- **Prix** : format `X XXX DH`
- **Icônes** : Heroicons (SVG inline)

## ⚠️ Règle d'architecture non négociable : système EAV hiérarchique

C'est le cœur de la valeur ajoutée du produit face à Avito. **Ne jamais y déroger.**

### Principe

Les caractéristiques techniques des produits (RAM, GPU, cycle de charge, capacité de stockage, etc.) ne sont **jamais** des champs en dur sur le modèle `Product`, et **jamais** des champs de texte libre saisis par l'utilisateur.

Elles sont entièrement pilotées par un schéma défini en base de données et administrable depuis le Django Admin :

- `Category` : auto-référencée (`parent` nullable), 2 niveaux (catégorie racine → sous-catégorie)
- `AttributeDefinition` : attaché à une catégorie (racine ou sous-catégorie), typé (`INT`, `DECIMAL`, `CHOICE`, `MULTI_CHOICE`, `BOOLEAN`, `TEXT_SHORT`), avec contraintes (`valeur_min`/`valeur_max`, `obligatoire`, `filtrable`)
- `AttributeChoice` : liste fermée de valeurs autorisées pour les types `CHOICE`/`MULTI_CHOICE`
- `ProductAttributeValue` : la valeur réelle saisie par le vendeur pour un attribut donné sur son annonce
- Une sous-catégorie **hérite** des attributs de sa catégorie racine (`get_inherited_attributes()` fusionne les deux niveaux sans doublon)

### Conséquences pour le code généré

- **Interdiction formelle** d'ajouter un champ spécifique à une catégorie sur le modèle `Product` (ex: ne jamais faire `cycle_charge = models.IntegerField()` directement sur `Product`). Si une caractéristique technique est demandée, créer/utiliser un `AttributeDefinition` à la place.
- **Interdiction formelle** de créer un `Serializer` ou une vue dédiée par catégorie de produit. Le serializer de création d'annonce est **unique et générique** (`DynamicProductSerializer`), il se construit dynamiquement à partir de `get_inherited_attributes()`.
- **Aucun champ texte libre** pour les caractéristiques techniques. Le seul champ de texte libre toléré est `description_complementaire` (optionnel, max 300 caractères, non filtrable, jamais un substitut aux attributs structurés).
- Toute valeur numérique soumise doit être validée côté serveur contre `valeur_min`/`valeur_max` (pas seulement côté client).
- Toute valeur de type `CHOICE`/`MULTI_CHOICE` doit être validée contre les `AttributeChoice` existants pour cet attribut — rejet sinon.
- Les filtres de recherche (page de listing) sont générés selon la **même logique d'héritage** que le formulaire de dépôt, à partir des attributs où `filtrable=True`.

## Modèle de comptes utilisateurs

Séparation stricte en deux modèles distincts (pas un simple booléen `is_pro`) :

- **`Particulier` (C2C)** : inscription rapide email/WhatsApp, limite d'annonces actives simultanées (anti-spam).
- **`Boutique` (B2C)** : page vitrine publique `/store/<slug>/`, champ `statut_verification` (`EN_ATTENTE`/`VERIFIE`/`REJETE`) qui pilote l'affichage du badge "Vendeur Vérifié", possibilité d'activer l'option "Garantie Boutique + Facture" sur ses annonces.

## Images des annonces

- **Nombre max d'images** : configurable via `MAX_IMAGES_PER_PRODUCT` (settings), valeur par défaut : 8.
- **Compression automatique** : si une image dépasse un seuil (`MAX_IMAGE_SIZE_MB`, ex: 2 Mo), elle est compressée/redimensionnée côté serveur avant stockage.
- **Formats acceptés** : JPEG, PNG, WebP.
- **Image principale** : la première image uploadée sert de thumbnail dans les listings.

## Recherche et tri

- **Tri par défaut** : plus récent en premier.
- **Filtres dynamiques** : générés automatiquement à partir des `AttributeDefinition` filtrables (via le système EAV).
- **Recherche textuelle** : sur le titre et la description complémentaire (recherche simple, pas de moteur full-text au MVP).

## Favoris (wishlist)

- Les utilisateurs connectés peuvent sauvegarder des annonces en favoris.
- Endpoints : `GET/POST/DELETE /api/v1/favorites/`
- Accessible depuis le dashboard utilisateur.

## Contact : WhatsApp First, pas de chat interne

- Pas de système de messagerie interne dans le MVP.
- Chaque fiche produit a un bouton principal généré en lien `https://wa.me/<numero>?text=<message_pré-rempli>`.
- Le numéro utilisé est celui du vendeur (`Particulier.telephone_whatsapp` ou `Boutique.telephone_whatsapp`).
- Chaque clic est tracké (`ProductClickWhatsapp`) sans bloquer la redirection. Chaque vue de fiche est trackée (`ProductView`) avec déduplication basique par session.
- La transaction se finalise en main à main dans un lieu sécurisé (Tanger City Mall, Ibn Batouta Mall, ou boutique pro partenaire) — c'est une mention informative statique, pas un système de réservation.

## Avis et notation des vendeurs

- Les avis portent sur le **vendeur** (profil), pas sur un produit.
- Tout utilisateur connecté peut laisser un avis (1 seul par vendeur, modifiable).
- Contenu : note étoiles (1-5) + commentaire texte (max 500 car.) + tags prédéfinis (`Produit conforme`, `Vendeur réactif`, `Bon prix`, `Emballage soigné`, `Ponctuel au RDV`).
- Le vendeur peut répondre une seule fois à chaque avis (max 300 car.).
- Publication immédiate + signalement possible. Modération admin manuelle.
- Endpoints : `GET/POST /api/v1/sellers/<id>/reviews/`, `POST /api/v1/reviews/<id>/reply/`, `POST /api/v1/reviews/<id>/report/`

## Modération et signalement

- **Publication immédiate** : pas de file d'attente de modération. Modération **a posteriori** via signalements.
- Bouton "Signaler" sur chaque fiche produit (`POST /api/v1/products/<id>/report/`).
- Raisons prédéfinies : annonce frauduleuse, prix irréaliste, produit interdit, contenu inapproprié, doublon.
- Traitement manuel par l'admin (Django Admin). Pas d'automatisation au MVP.

## Expiration et rappels

- Les annonces **n'expirent pas automatiquement**.
- Après **30 jours** sans changement de statut → notification dans le dashboard pour rappeler au vendeur de confirmer la disponibilité.
- Si aucune action après le rappel : l'annonce reste active mais perd en priorité dans le tri (optionnel, à évaluer post-lancement).

## Tableau de bord vendeur

Chaque vendeur (particulier ou boutique) a un espace privé `/dashboard/` affichant, **pour ses propres annonces uniquement** (isolation stricte des données à vérifier systématiquement) :
- Nombre de vues et de clics WhatsApp par annonce
- Changement de statut en un clic (`Disponible` / `Vendu` / `Archivé`)
- Notifications (rappels de disponibilité, signalements reçus)
- Liste des favoris sauvegardés

Exposé via des endpoints REST :
- `GET /api/v1/dashboard/my-products/` — liste des annonces du vendeur connecté
- `PATCH /api/v1/dashboard/my-products/<id>/status/` — changement de statut
- `GET /api/v1/dashboard/stats/` — statistiques agrégées (vues, clics WhatsApp)
- `GET /api/v1/dashboard/notifications/` — notifications du vendeur

## Conventions de code

- Langue du code (noms de variables, fonctions, modèles) : **anglais**.
- Langue des labels visibles utilisateur, messages d'erreur, contenu admin : **français**.
- Optimiser systématiquement les requêtes sur `ProductAttributeValue` avec `select_related`/`prefetch_related` — le modèle EAV est sujet aux problèmes de requêtes N+1.
- Éviter toute dépendance lourde non justifiée (pas de Celery/Redis sauf besoin avéré) — rester aligné avec la contrainte Asset-Light du projet.
- Avant de proposer un changement de modèle de données touchant `Product`, `Category` ou `AttributeDefinition`, vérifier la cohérence avec le principe EAV hiérarchique décrit plus haut.
- Variables de configuration globales (limites, seuils) centralisées dans `settings.py` ou un fichier `constants.py` dédié.
- **Ne pas écrire de tests unitaires** — la validation se fait manuellement via les endpoints API.

## Hors périmètre MVP (ne pas développer sans demande explicite)

OTP WhatsApp, chat interne, système de réservation de créneau, paiement en ligne, extension géographique hors Tanger, vérification boutique automatisée, tri par pertinence avancé, notifications push, alertes prix sur favoris, modération automatisée (IA), système de boost activé (paiement).

> **Note** : L'application mobile n'est plus hors périmètre à long terme — l'architecture REST API-first est pensée pour la supporter. Cependant, le développement du client mobile lui-même reste hors MVP.
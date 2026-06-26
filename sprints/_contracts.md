# Contrats techniques — Setup.ma

## Format de réponse API standard

### Succès (single object)
```json
{
  "data": { ... }
}
```

### Succès (liste paginée)
```json
{
  "count": 50,
  "next": "http://api/v1/products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Erreur de validation (400)
```json
{
  "errors": {
    "field_name": ["Message d'erreur en français."],
    "non_field_errors": ["Erreur générale."]
  }
}
```

### Erreur d'authentification (401)
```json
{
  "detail": "Identifiants invalides."
}
```

### Erreur de permission (403)
```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

### Erreur not found (404)
```json
{
  "detail": "Non trouvé."
}
```

## Structure des apps Django

```
app_name/
├── __init__.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── permissions.py        (si permissions custom)
├── filters.py            (si filtres custom)
├── services.py           (si logique métier complexe)
├── admin.py
└── migrations/
```

## Conventions de nommage

| Type | Convention | Exemple |
|------|-----------|---------|
| Modèle | PascalCase singulier | `Product`, `AttributeDefinition` |
| Serializer | `{Model}Serializer` | `ProductSerializer` |
| Serializer (liste) | `{Model}ListSerializer` | `ProductListSerializer` |
| Serializer (création) | `{Model}CreateSerializer` | `ProductCreateSerializer` |
| ViewSet | `{Model}ViewSet` | `ProductViewSet` |
| Permission | `Is{Condition}` | `IsOwner`, `IsVerifiedBoutique` |
| Filtre | `{Model}Filter` | `ProductFilter` |
| URL pattern | `/api/v1/{app}/{resource}/` | `/api/v1/products/` |

## Règles de modification rétroactive

Un sprint peut modifier un modèle/fichier d'un sprint précédent SI :
1. Le changement est documenté dans `_changelog.md`
2. Le `_registry.md` est mis à jour immédiatement

## Configuration DRF commune

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
}
```

## Pagination

- Toujours utiliser `PageNumberPagination` avec `PAGE_SIZE = 20`.
- Le client peut demander `?page=N`.

## Authentification JWT

- `POST /api/v1/auth/token/` → obtenir access + refresh token
- `POST /api/v1/auth/token/refresh/` → renouveler l'access token
- Access token durée : 1 heure
- Refresh token durée : 7 jours

## Variables de configuration globales (settings.py)

Centraliser toutes les constantes métier :
```python
# Limites produits
MAX_IMAGES_PER_PRODUCT = 8
MAX_IMAGE_SIZE_MB = 2
MAX_ACTIVE_ADS_PARTICULIER = 10
MAX_DESCRIPTION_LENGTH = 300

# Expiration
AD_REMINDER_DAYS = 30

# Review
MAX_REVIEW_LENGTH = 500
MAX_REPLY_LENGTH = 300
```

## Langue

- Code (variables, fonctions, classes, noms de fichiers) : **anglais**
- Messages d'erreur API, labels admin, contenu user-facing : **français**

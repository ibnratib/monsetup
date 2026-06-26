import json

from django.conf import settings

from catalog.models import AttributeChoice, AttributeDefinition, Category


def generate_catalog_from_ai(product_type: str) -> dict:
    """
    Call OpenAI GPT-4o to generate a full category schema for a product type.
    Returns a dict with the generated catalog structure.
    """
    import openai

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = """Tu es un expert en e-commerce spécialisé dans la classification de produits.
Tu dois générer un schéma de catalogue complet pour un type de produit donné.

RÈGLES IMPORTANTES :
- Maximum 2 niveaux de catégories (racine → sous-catégorie)
- Les attributs sont attachés à une sous-catégorie
- Types d'attributs disponibles : INT, DECIMAL, CHOICE, MULTI_CHOICE, BOOLEAN, TEXT_SHORT
- Les attributs CHOICE/MULTI_CHOICE doivent avoir des choix prédéfinis
- Certains attributs peuvent dépendre d'un choix spécifique (ex: "Puce Apple Silicon" ne s'affiche que si Marque = Apple)
- Les attributs doivent être pertinents pour le marché marocain
- Labellise en français (label_fr)
- Sois exhaustif sur les marques et modèles populaires au Maroc

RÉPONDS UNIQUEMENT en JSON valide avec ce format :
{
  "parent_category": "Nom de la catégorie racine (existante ou nouvelle)",
  "subcategory": "Nom de la sous-catégorie",
  "attributes": [
    {
      "name": "identifiant_technique_snake_case",
      "label_fr": "Label affiché en français",
      "attribute_type": "CHOICE",
      "required": true,
      "filterable": true,
      "unit": "",
      "min_value": null,
      "max_value": null,
      "choices": ["Option 1", "Option 2"],
      "depends_on": null
    },
    {
      "name": "modele_specifique",
      "label_fr": "Modèle spécifique",
      "attribute_type": "CHOICE",
      "required": true,
      "filterable": true,
      "unit": "",
      "choices": ["Model A", "Model B"],
      "depends_on": {"attribute_name": "marque", "choice_value": "Apple"}
    }
  ]
}

depends_on est null pour les attributs toujours visibles, ou un objet {attribute_name, choice_value} pour les attributs conditionnels.
"""

    user_prompt = f"Génère le schéma de catalogue complet pour : {product_type}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    result = json.loads(content)
    return result


def save_ai_catalog_result(result: dict):
    """
    Take the AI-generated catalog result and persist it to the database.
    Creates Category, AttributeDefinition, and AttributeChoice objects.
    """
    parent_name = result.get('parent_category', '').strip()
    subcategory_name = result.get('subcategory', '').strip()
    attributes_data = result.get('attributes', [])

    if not parent_name or not subcategory_name:
        raise ValueError("parent_category et subcategory sont obligatoires.")

    # Get or create parent category
    parent, _ = Category.objects.get_or_create(
        name=parent_name,
        parent=None,
        defaults={'order': 0},
    )

    # Get or create subcategory
    subcategory, _ = Category.objects.get_or_create(
        name=subcategory_name,
        parent=parent,
        defaults={'order': 0},
    )

    # First pass: create all attributes without dependencies
    attr_map = {}  # name -> AttributeDefinition
    choice_map = {}  # (attr_name, choice_value) -> AttributeChoice

    for i, attr_data in enumerate(attributes_data):
        attr_name = attr_data.get('name', '').strip()
        if not attr_name:
            continue

        attr = AttributeDefinition.objects.create(
            category=subcategory,
            name=attr_name,
            label_fr=attr_data.get('label_fr', attr_name),
            attribute_type=attr_data.get('attribute_type', 'TEXT_SHORT'),
            required=attr_data.get('required', False),
            filterable=attr_data.get('filterable', False),
            order=i,
            unit=attr_data.get('unit', '') or '',
            min_value=attr_data.get('min_value'),
            max_value=attr_data.get('max_value'),
        )
        attr_map[attr_name] = attr

        # Create choices
        choices = attr_data.get('choices', [])
        if choices and attr.attribute_type in ('CHOICE', 'MULTI_CHOICE'):
            for j, choice_value in enumerate(choices):
                choice = AttributeChoice.objects.create(
                    attribute=attr,
                    value=str(choice_value),
                    order=j,
                )
                choice_map[(attr_name, str(choice_value))] = choice

    # Second pass: set depends_on_choice for conditional attributes
    for attr_data in attributes_data:
        depends_on = attr_data.get('depends_on')
        if not depends_on:
            continue

        attr_name = attr_data.get('name', '').strip()
        parent_attr_name = depends_on.get('attribute_name', '').strip()
        parent_choice_value = str(depends_on.get('choice_value', '')).strip()

        if attr_name in attr_map and (parent_attr_name, parent_choice_value) in choice_map:
            attr = attr_map[attr_name]
            attr.depends_on_choice = choice_map[(parent_attr_name, parent_choice_value)]
            attr.save(update_fields=['depends_on_choice'])

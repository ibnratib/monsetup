import json
import logging

from openai import OpenAI

from django.conf import settings
from django.db.models import Q

from catalog.models import AttributeDefinition, Category
from core.models import City
from products.models import Product

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Tu es un assistant de recherche pour Setup.ma, une marketplace d'annonces tech au Maroc.
Ton rôle est d'aider l'utilisateur à trouver le produit idéal.

COMPORTEMENT :
1. Analyse le message de l'utilisateur et identifie ce qui manque pour faire une bonne recherche.
2. Pose UNE SEULE question par message pour compléter les informations manquantes.
3. Adapte tes questions au contexte
4. Utilise tes outils pour explorer les catégories et attributs disponibles afin de poser des questions pertinentes.
5. Quand tu estimes avoir assez d'informations (minimum 2 critères), lance la recherche avec search_products.
6. Ne pose JAMAIS plusieurs questions dans un même message.
7. Sois concis, amical, et tutoie l'utilisateur.
8. Réponds toujours en français.
9. Après avoir montré des résultats, si l'utilisateur dit que ça ne convient pas, continue la conversation et affine la recherche avec de nouveaux critères. Ne considère jamais la conversation comme terminée.
"""

# OpenAI function definitions (tools)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": "Liste toutes les catégories disponibles sur la marketplace. Utilise cet outil pour connaître les catégories existantes.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_attributes",
            "description": "Récupère les attributs filtrables d'une catégorie donnée (ex: RAM, stockage, marque...). Utilise cet outil pour connaître les critères de filtrage disponibles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_slug": {
                        "type": "string",
                        "description": "Le slug de la catégorie",
                    },
                },
                "required": ["category_slug"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_cities",
            "description": "Liste toutes les villes disponibles.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Recherche des produits dans la base de données avec des filtres. Utilise cet outil quand tu as assez d'informations pour lancer une recherche.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_slug": {
                        "type": "string",
                        "description": "Slug de la catégorie (optionnel)",
                    },
                    "keywords": {
                        "type": "string",
                        "description": "Mots-clés à chercher dans le titre et la description (optionnel)",
                    },
                    "price_min": {
                        "type": "number",
                        "description": "Prix minimum en DH (optionnel)",
                    },
                    "price_max": {
                        "type": "number",
                        "description": "Prix maximum en DH (optionnel)",
                    },
                    "ville": {
                        "type": "string",
                        "description": "Nom de la ville (optionnel)",
                    },
                },
            },
        },
    },
]


def _execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool call and return the result as a JSON string."""
    if name == "list_categories":
        categories = Category.objects.select_related('parent').order_by('order', 'name')
        result = []
        for cat in categories:
            entry = {"name": cat.name, "slug": cat.slug}
            if cat.parent:
                entry["parent"] = cat.parent.name
            result.append(entry)
        return json.dumps(result, ensure_ascii=False)

    elif name == "get_category_attributes":
        slug = arguments.get("category_slug", "")
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return json.dumps({"error": f"Catégorie '{slug}' introuvable."}, ensure_ascii=False)

        attrs = category.get_inherited_attributes() if hasattr(category, 'get_inherited_attributes') else list(category.attributes.all())
        filterable_attrs = [a for a in attrs if a.filterable]
        result = []
        for attr in filterable_attrs:
            entry = {
                "name": attr.name,
                "label": attr.label_fr,
                "type": attr.attribute_type,
            }
            if attr.unit:
                entry["unit"] = attr.unit
            if attr.attribute_type in ('CHOICE', 'MULTI_CHOICE'):
                entry["choices"] = list(attr.choices.values_list('value', flat=True))
            if attr.min_value is not None:
                entry["min_value"] = float(attr.min_value)
            if attr.max_value is not None:
                entry["max_value"] = float(attr.max_value)
            result.append(entry)
        return json.dumps(result, ensure_ascii=False)

    elif name == "list_cities":
        cities = list(City.objects.values_list('name', flat=True))
        return json.dumps(cities, ensure_ascii=False)

    elif name == "search_products":
        from ai_search.search import execute_search
        filters = {k: v for k, v in arguments.items() if v is not None and v != ""}
        qs = execute_search(filters)
        count = qs.count()
        products = list(qs[:10].values(
            'id', 'title', 'price', 'ville__name', 'category__name', 'category__slug'
        ))
        # Format for AI readability
        result = {
            "total": count,
            "products": [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "price": float(p["price"]),
                    "ville": p["ville__name"],
                    "category": p["category__name"],
                }
                for p in products
            ],
        }
        return json.dumps(result, ensure_ascii=False)

    return json.dumps({"error": "Outil inconnu"}, ensure_ascii=False)


def get_ai_response(conversation_history: list[dict]) -> dict:
    """
    Send conversation to OpenAI with tools and handle tool calls.

    Returns:
        dict with keys:
        - "type": "question" or "search"
        - "message": str (the AI message)
        - "filters": dict (only if type == "search")
        - "products_data": list (only if type == "search")
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    # Allow up to 5 rounds of tool calls
    for _ in range(5):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            temperature=0.3,
            max_tokens=600,
        )

        choice = response.choices[0]

        # If the model wants to call tools
        if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
            # Add the assistant message with tool calls
            messages.append(choice.message)

            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info(f"AI tool call: {fn_name}({fn_args})")
                tool_result = _execute_tool(fn_name, fn_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

                # If search_products was called, capture results for the response
                if fn_name == "search_products":
                    search_data = json.loads(tool_result)
                    # Continue the loop so the AI can summarize results

            continue

        # Model is done — return the final text response
        content = choice.message.content
        if not content:
            return {
                "type": "question",
                "message": "Désolé, je n'ai pas compris. Pouvez-vous reformuler ?",
            }

        assistant_message = content.strip()

        # Check if search was performed (look back in messages for search_products calls)
        search_result = _find_last_search_result(messages)
        if search_result:
            return {
                "type": "search",
                "message": assistant_message,
                "filters": {},
                "products_data": search_result,
            }

        return {
            "type": "question",
            "message": assistant_message,
        }

    # Fallback if we hit the loop limit
    return {
        "type": "question",
        "message": "Je n'arrive pas à traiter votre demande. Pouvez-vous reformuler ?",
    }


def _find_last_search_result(messages: list[dict]) -> dict | None:
    """Find the last search_products tool result in the message history."""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "tool":
            try:
                data = json.loads(msg["content"])
                if "products" in data and "total" in data:
                    return data
            except (json.JSONDecodeError, TypeError):
                pass
    return None

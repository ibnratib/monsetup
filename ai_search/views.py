import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_search.serializers import ChatMessageSerializer
from ai_search.service import get_ai_response
from products.models import Product
from products.serializers import ProductListSerializer

logger = logging.getLogger(__name__)

SESSION_KEY = 'ai_search_conversation'


class AISearchChatView(APIView):
    """
    Conversational AI search endpoint.

    POST: Send a message to the AI assistant.
    DELETE: Reset the conversation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']

        # Get or initialize conversation history from session
        conversation = request.session.get(SESSION_KEY, [])

        # Add user message
        conversation.append({"role": "user", "content": user_message})

        # Get AI response
        try:
            ai_result = get_ai_response(conversation)
        except Exception as e:
            logger.error(f"AI search error: {e}\n{__import__('traceback').format_exc()}")
            return Response(
                {"error": "Une erreur est survenue avec l'assistant IA. Réessayez."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Add assistant response to conversation
        conversation.append({"role": "assistant", "content": ai_result["message"]})

        # Save conversation to session
        request.session[SESSION_KEY] = conversation

        # Build response
        if ai_result["type"] == "search":
            products_data_from_ai = ai_result.get("products_data", {})
            product_ids = [p["id"] for p in products_data_from_ai.get("products", [])]
            total = products_data_from_ai.get("total", 0)

            # Fetch full product objects for proper serialization
            if product_ids:
                products_qs = Product.objects.filter(
                    id__in=product_ids, status='DISPONIBLE'
                ).select_related(
                    'category', 'ville', 'seller'
                ).prefetch_related('images')
                products_data = ProductListSerializer(
                    products_qs, many=True, context={'request': request}
                ).data
            else:
                products_data = []

            # Keep conversation alive so user can refine
            # request.session[SESSION_KEY] = []  -- removed to allow follow-up

            return Response({
                "type": "search",
                "message": ai_result["message"],
                "products": products_data,
                "total_results": total,
            })

        return Response({
            "type": "question",
            "message": ai_result["message"],
        })

    def delete(self, request):
        """Reset the conversation."""
        request.session[SESSION_KEY] = []
        return Response({"message": "Conversation réinitialisée."})


class AISearchHistoryView(APIView):
    """Get current conversation history."""
    permission_classes = [AllowAny]

    def get(self, request):
        conversation = request.session.get(SESSION_KEY, [])
        return Response({
            "conversation": [
                msg for msg in conversation if msg["role"] != "system"
            ]
        })

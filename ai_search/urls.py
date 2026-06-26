from django.urls import path

from ai_search.views import AISearchChatView, AISearchHistoryView

api_urlpatterns = [
    path('chat/', AISearchChatView.as_view(), name='ai-search-chat'),
    path('history/', AISearchHistoryView.as_view(), name='ai-search-history'),
]

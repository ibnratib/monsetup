from django.urls import path

from adminpanel import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/edit/', views.CategoryEditView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Attributes (under a category)
    path('categories/<int:cat_pk>/attributes/', views.AttributeListView.as_view(), name='attribute-list'),
    path('categories/<int:cat_pk>/attributes/create/', views.AttributeCreateView.as_view(), name='attribute-create'),
    path('attributes/<int:pk>/edit/', views.AttributeEditView.as_view(), name='attribute-edit'),
    path('attributes/<int:pk>/delete/', views.AttributeDeleteView.as_view(), name='attribute-delete'),

    # Choices (under an attribute)
    path('attributes/<int:attr_pk>/choices/', views.ChoiceListView.as_view(), name='choice-list'),
    path('attributes/<int:attr_pk>/choices/create/', views.ChoiceCreateView.as_view(), name='choice-create'),
    path('choices/<int:pk>/edit/', views.ChoiceEditView.as_view(), name='choice-edit'),
    path('choices/<int:pk>/delete/', views.ChoiceDeleteView.as_view(), name='choice-delete'),

    # Reorder
    path('categories/reorder/', views.CategoryReorderView.as_view(), name='category-reorder'),
    path('attributes/reorder/', views.AttributeReorderView.as_view(), name='attribute-reorder'),
    path('choices/reorder/', views.ChoiceReorderView.as_view(), name='choice-reorder'),

    # AI Generation
    path('ai-generate/', views.AIGenerateView.as_view(), name='ai-generate'),
    path('ai-generate/confirm/', views.AIGenerateConfirmView.as_view(), name='ai-generate-confirm'),
]

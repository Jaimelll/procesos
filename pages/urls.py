from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    home_view, SignUpView, proceso_list, proceso_detail, proceso_create, 
    proceso_update, proceso_delete, evento_list, evento_detail, 
    evento_create_update, evento_delete, about_view, parametro_list, 
    parametro_detail, parametro_create, parametro_update, parametro_delete, 
    formula_list, formula_detail, formula_create, formula_update, formula_delete
)

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),  # Ruta de logout
    path('procesos/', proceso_list, name='proceso_list'),
    path('procesos/<int:pk>/', proceso_detail, name='proceso_detail'),
    path('procesos/new/', proceso_create, name='proceso_create'),
    path('procesos/<int:pk>/edit/', proceso_update, name='proceso_update'),
    path('procesos/<int:pk>/delete/', proceso_delete, name='proceso_delete'),
    
    # URLs para eventos
    path('procesos/<int:proceso_id>/eventos/', evento_list, name='evento_list'),
    path('procesos/<int:proceso_id>/eventos/<int:pk>/', evento_detail, name='evento_detail'),
    path('procesos/<int:proceso_id>/eventos/new/', evento_create_update, name='evento_create'),
    path('procesos/<int:proceso_id>/eventos/create/', evento_create_update, name='evento_create'),
    path('procesos/<int:proceso_id>/eventos/<int:evento_id>/update/', evento_create_update, name='evento_update'),
    path('procesos/<int:proceso_id>/eventos/<int:pk>/delete/', evento_delete, name='evento_delete'),
    path('about/', about_view, name='about'),
    path('parametros/', parametro_list, name='parametro_list'),
    path('parametros/<int:pk>/', parametro_detail, name='parametro_detail'),
    path('parametros/new/', parametro_create, name='parametro_create'),
    path('parametros/<int:pk>/edit/', parametro_update, name='parametro_update'),
    path('parametros/<int:pk>/delete/', parametro_delete, name='parametro_delete'),
    
    # URLs para fórmulas
    path('parametros/<int:parametro_id>/formulas/', formula_list, name='formula_list'),
    path('parametros/<int:parametro_id>/formulas/<int:pk>/', formula_detail, name='formula_detail'),
    path('parametros/<int:parametro_id>/formulas/new/', formula_create, name='formula_create'),
    path('parametros/<int:parametro_id>/formulas/<int:pk>/edit/', formula_update, name='formula_update'),
    path('parametros/<int:parametro_id>/formulas/<int:pk>/delete/', formula_delete, name='formula_delete'),
]

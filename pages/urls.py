from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import home_view, SignUpView, proceso_list, proceso_detail, proceso_create, proceso_update, proceso_delete, evento_list, evento_detail, evento_create, evento_update, evento_delete, about_view  # Importar 'about_view'

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
    path('procesos/<int:proceso_id>/eventos/new/', evento_create, name='evento_create'),
    path('procesos/<int:proceso_id>/eventos/<int:pk>/edit/', evento_update, name='evento_update'),
    path('procesos/<int:proceso_id>/eventos/<int:pk>/delete/', evento_delete, name='evento_delete'),
    path('about/', about_view, name='about'),
]

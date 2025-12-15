from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # IMPORTANT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('swigo.urls', namespace='swigo')),
    
    # AJOUTEZ CES LIGNES AU NIVEAU RACINE
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
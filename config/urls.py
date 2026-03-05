from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная страница - должна быть name='home'
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Или если у тебя есть отдельное приложение для главной:
    # path('', include('mailings.urls')),
    
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('mailings/', include('mailings.urls')),
]
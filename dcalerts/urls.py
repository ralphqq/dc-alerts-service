"""dcalerts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from homepage.views import HomepageView, SignUpView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView.as_view(), name='homepage'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path(
        'about/',
        TemplateView.as_view (template_name='homepage/about.html'),
        name='about'
    ),
    path(
        'contact/',
        TemplateView.as_view(template_name='homepage/contact.html'),
        name='contact'
    ),
    path(
        'terms/',
        TemplateView.as_view(template_name='homepage/terms.html'),
        name='terms'
    ),
    path(
        'privacy/',
        TemplateView.as_view(template_name='homepage/privacy.html'),
        name='privacy'
    ),
    path('subscribers/', include('subscribers.urls')),
]

# encoding: utf-8
"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve

from example.core.utils import api_doc

apipatterns = [
    path('demo/', include('example.apps.demo.views')),
]
urlpatterns = [
    path('cool/', include('cool.urls')),
    path('admin/', admin.site.urls),
    path('api/', include(apipatterns)),
    path('doc.md', api_doc)
]
if settings.DEBUG:
    urlpatterns.append(
        path('%s/<path:path>' % settings.MEDIA_URL.strip('/'), serve, {'document_root': settings.MEDIA_ROOT})
    )

"""torstat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, re_path

from . import views

handler404 = "torstat.views.error404"
handler500 = "torstat.views.error500"
handler403 = "torstat.views.error403"
handler400 = "torstat.views.error400"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("relay/<str:name>", views.node, name="relay"),
    path("bridge/<str:name>", views.node, name="bridge"),
    path("exit/<str:name>", views.node, name="exit"),
    path("search/<str:name>", views.node, name="search"),
    path("search/", views.relayRaw, name="search"),
    path("license/", views.license, name="license"),
    path("LICENSE/", views.license, name="license"),
    path("", views.index, name="index"),
    path("donate/", views.donate, name="donate"),
]

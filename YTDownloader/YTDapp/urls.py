from django.contrib import admin
from django.urls import path

from YTDownloader.YTDapp import views

urlpatterns = (
    path('',views.home.as_view(),name="home"),
)
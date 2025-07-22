from django.contrib import admin
from django.urls import path

from menu.views import MenuView, SendMessageView

urlpatterns = [
    path('v1/menu/',MenuView.as_view(), name="menu"),
    path('v1/menu/send-message/',SendMessageView.as_view(), name="send-message"),
]
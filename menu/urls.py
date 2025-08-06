from django.contrib import admin
from django.urls import path

from menu.views import MenuView, SendMessageView, TemplatesListView, CreateTemplateView, DashboardView, ValidateTokenView

urlpatterns = [
    path('v1/menu/', MenuView.as_view(), name="menu"), # menu api
    path('v1/menu/dashboard/', DashboardView.as_view(), name="dashboard"), # dashboard api

    path('v1/menu/send-message/', SendMessageView.as_view(), name="send-message"), # send message api
    path('v1/menu/templates-list/', TemplatesListView.as_view(), name="templates-list"), # templates list api
    path('v1/menu/create-template/', CreateTemplateView.as_view(), name="create-template"), # create template api

    path('v1/menu/validate-token/', ValidateTokenView.as_view(), name="validate-token"), #token validation api
]
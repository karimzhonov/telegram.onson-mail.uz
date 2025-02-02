from django.urls import path

from .views import OrderByNumberView

urlpatterns = [
    path('order/<number>/', OrderByNumberView.as_view(), name='index'),
]

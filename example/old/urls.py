from django.urls import path

from . import views

urlpatterns = [
    # ex: /old/
    path('', views.index, name='index'),
    # ex: /old/5/
    path('<int:collection_id>/', views.detail, name='detail'),
]

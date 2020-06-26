from django.urls import path

from . import views

urlpatterns = [
    # ex: /new/
    path('', views.index, name='index'),
    # ex: /new/5/
    path('<int:collection_id>/', views.detail, name='detail'),
]


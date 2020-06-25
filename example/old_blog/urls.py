from django.urls import path

from . import views

urlpatterns = [
    # ex: /old_blog/
    path('', views.index, name='index'),
    # ex: /old_blog/5/
    path('<int:article_id>/', views.detail, name='detail'),
]

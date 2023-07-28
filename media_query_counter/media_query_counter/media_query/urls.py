from django.urls import path
from .views import count_media_queries

urlpatterns = [
    path('', count_media_queries, name='count_media_queries'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-nearest-station/', views.nearest_station, name='index'),
    path('map/', views.map_view, name='map_view'),
    path('save-marker/', views.save_marker, name='save_marker'),
    path('remove-markers/', views.remove_all_markers, name='remove_all_markers'),
    path('load_markers/', views.load_markers, name='load_markers'),
]

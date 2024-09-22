from django.http import JsonResponse
from django.shortcuts import render
from core.models import EVChargingLocation
from geopy.distance import geodesic
import json

# Create your views here.
def index(request):
    stations = list(EVChargingLocation.objects.values('latitude','longitude')[:100])
    context = {'stations' : stations}
    return render(request, 'index.html', context)

def nearest_station(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    user_location = latitude,longitude
    station_distances = {}
    for station in EVChargingLocation.objects.all()[:100]:
        station_location = station.latitude, station.longitude

        distance = geodesic(user_location,station_location).km
        station_distances[distance] = station_location

    min_distance = min(station_distances)
    station_coords = station_distances[min_distance]

    return JsonResponse({
        'coordinates' : station_coords,
        'distance' : min_distance,
    })


def map_view(request):
    return render(request, 'map.html')


def save_marker(request):
    if request.method == 'POST':
        markers = request.POST.get('markers')
        if markers:
            marker_data = json.loads(markers)
            for marker in marker_data:
                latitude = marker.get('latitude')
                longitude = marker.get('longitude')
                EVChargingLocation.objects.create(
                    station_name='Unnamed Station',  # Default name or customize as needed
                    latitude=latitude,
                    longitude=longitude
                )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def remove_all_markers(request):
    if request.method == 'POST':
        # Delete all markers from the database
        EVChargingLocation.objects.all().delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


def load_markers(request):
    markers = EVChargingLocation.objects.all()
    marker_list = [{'latitude': marker.latitude, 'longitude': marker.longitude} for marker in markers]
    return JsonResponse({'markers': marker_list})


from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        "status": "online",
        "message": "FKC Legal Backend API is running",
        "contact_endpoint": "/api/contact/"
    })


urlpatterns = [
    path('', api_root),
    path('api/', include('api.urls')),
]

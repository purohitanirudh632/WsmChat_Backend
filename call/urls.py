# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Existing chat URLs...
    
    # Call management URLs
    path('calls/', views.CallListCreateView.as_view(), name='call-list-create'),
    path('calls/<uuid:id>/', views.CallDetailView.as_view(), name='call-detail'),
    path('calls/<uuid:call_id>/ice-candidates/', views.add_ice_candidate, name='add-ice-candidate'),
    path('calls/<uuid:call_id>/ice-candidates/get/', views.get_ice_candidates, name='get-ice-candidates'),
]
from rest_framework.routers import DefaultRouter
from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView

from .views import AuthViewsets ,UserViewset , MyTokenObtainPairView


router = DefaultRouter()
router.register(r'user',UserViewset)
router.register(r'auth',AuthViewsets,basename='auth')

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    path('api/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API documentation (if using DRF browsable API)
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
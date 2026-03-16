from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'semestre', SemestreViewSet)
router.register(r'tcp', TCPViewSet)
router.register(r'asignatura', AsignaturaViewSet)
router.register(r'estudiante', EstudianteViewSet)
router.register(r'nota', NotaViewSet)

# URLs de autenticación (definidas como lista para mejor organización)
auth_patterns = [
    path('registro/', registro, name='registro'),
    path('login/', login, name='login'),
    #path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('perfil/', perfil, name='perfil'),
]

urlpatterns = [
    # API endpoints (ej: /api/semestre/, /api/estudiante/, etc)
    path('', include(router.urls)),
    
    # Auth endpoints (ej: /api/auth/login/, /api/auth/registro/, etc)
    path('auth/', include(auth_patterns)),
]
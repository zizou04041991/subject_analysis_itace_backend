from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError, models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Semestre, Asignatura, Estudiante, Nota,TCP
from .serializers import (
    SemestreSerializer, AsignaturaSerializer, 
    EstudianteSerializer, NotaSerializer, PaginacionPersonalizada, TCPSerializer
)
from .filters import SemestreFilter, AsignaturaFilter, EstudianteFilter, NotaFilter

# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UsuarioSerializer, LoginSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UsuarioSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UsuarioSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def perfil(request):
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


class SemestreViewSet(viewsets.ModelViewSet):
    queryset = Semestre.objects.all()
    serializer_class = SemestreSerializer
    #pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SemestreFilter
    search_fields = ['numero']  # Búsqueda general con ?search=
    ordering_fields = ['id', 'numero']
    ordering = ['numero']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si hay estudiantes usando este semestre
            if instance.estudiantes_actuales.exists():
                return Response(
                    {'error': 'No se puede eliminar el semestre porque hay estudiantes asignados a él.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Semestre eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            if 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
        
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str:
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        return {'error': str(error)}


class AsignaturaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    #pagination_class = PaginacionPersonalizada
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AsignaturaFilter
    search_fields = ['nombre']
    ordering_fields = ['id', 'nombre', 'fecha_creacion']
    ordering = ['nombre']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si la asignatura tiene alguna relación (ejemplo con notas)
            # if instance.notas.exists():
            #     return Response(
            #         {'error': 'No se puede eliminar la asignatura porque tiene notas asociadas.'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Asignatura eliminada correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        """
        Formatea los errores para dar mensajes más específicos
        """
        if hasattr(error, 'detail'):
            # Si el error ya tiene el formato que queremos (con 'error')
            if isinstance(error.detail, dict) and 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
            
            # Si es un diccionario de errores por campo
            if isinstance(error.detail, dict):
                # Verificar si es el error específico de nombre
                if 'nombre' in error.detail:
                    nombre_errors = error.detail['nombre']
                    if isinstance(nombre_errors, list):
                        return {'error': nombre_errors[0]}
                    return {'error': str(nombre_errors)}
                
                # Verificar si es el error específico de color
                if 'color' in error.detail:
                    color_errors = error.detail['color']
                    if isinstance(color_errors, list):
                        return {'error': color_errors[0]}
                    return {'error': str(color_errors)}
                
                # Para otros campos, devolver el primer error encontrado
                for field, errors in error.detail.items():
                    if errors:
                        if isinstance(errors, list):
                            return {'error': f"{field}: {errors[0]}"}
                        return {'error': f"{field}: {str(errors)}"}
            
            # Si es una lista de errores
            elif isinstance(error.detail, list):
                return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
            
            # Si es un string
            elif isinstance(error.detail, str):
                return {'error': error.detail}
        
        # Si es IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                if "nombre" in error_str:
                    return {'error': 'Ya existe una asignatura con ese nombre.'}
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Por defecto
        return {'error': str(error)}


# views.py (parte de EstudianteViewSet)
class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all().select_related('semestre_actual')
    serializer_class = EstudianteSerializer
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EstudianteFilter
    search_fields = ['numero_control', 'nombre', 'apellidos', 'curp']
    ordering_fields = ['id', 'numero_control', 'nombre', 'apellidos', 'fecha_registro']
    ordering = ['apellidos', 'nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro adicional para nombre_completo si viene como parámetro directo
        nombre_completo = self.request.query_params.get('nombre_completo')
        if nombre_completo:
            queryset = queryset.filter(
                models.Q(nombre__icontains=nombre_completo) |
                models.Q(apellidos__icontains=nombre_completo)
            )
        
        # Filtro por número de control
        numero_control = self.request.query_params.get('numero_control')
        if numero_control:
            queryset = queryset.filter(numero_control__icontains=numero_control)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Verificar si el estudiante tiene notas registradas
            if instance.notas.exists():
                return Response(
                    {'error': 'No se puede eliminar el estudiante porque tiene notas registradas.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Estudiante eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        """
        Formatea los errores para dar mensajes más específicos
        """
        if hasattr(error, 'detail'):
            # Si el error ya tiene el formato que queremos (con 'error')
            if isinstance(error.detail, dict) and 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
            
            # Si es un diccionario de errores por campo
            if isinstance(error.detail, dict):
                # Verificar si es el error específico de número de control
                if 'numero_control' in error.detail:
                    numero_control_errors = error.detail['numero_control']
                    if isinstance(numero_control_errors, list):
                        return {'error': numero_control_errors[0]}
                    return {'error': str(numero_control_errors)}
                
                # Verificar si es el error específico de CURP
                if 'curp' in error.detail:
                    curp_errors = error.detail['curp']
                    if isinstance(curp_errors, list):
                        return {'error': curp_errors[0]}
                    return {'error': str(curp_errors)}
                
                # Para otros campos, devolver el primer error encontrado
                for field, errors in error.detail.items():
                    if errors:
                        if isinstance(errors, list):
                            return {'error': f"{field}: {errors[0]}"}
                        return {'error': f"{field}: {str(errors)}"}
            
            # Si es una lista de errores
            elif isinstance(error.detail, list):
                return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
            
            # Si es un string
            elif isinstance(error.detail, str):
                return {'error': error.detail}
        
        # Si es IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                if "numero_control" in error_str:
                    return {'error': 'Ya existe un estudiante con ese número de control.'}
                elif "curp" in error_str:
                    return {'error': 'Ya existe un estudiante con esa CURP.'}
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Por defecto
        return {'error': str(error)}

class TCPViewSet(viewsets.ModelViewSet):
    """ViewSet para TCP"""
    queryset = TCP.objects.all()
    serializer_class = TCPSerializer
    
    # Filtros
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_class = TCPFilter  # Si tienes un filtro personalizado
    search_fields = ['numero']
    ordering_fields = ['id', 'numero', 'fecha_creacion']
    ordering = ['numero']
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Aquí puedes agregar validaciones adicionales antes de eliminar
            # Por ejemplo, verificar si hay asignaturas usando este TCP
            
            self.perform_destroy(instance)
            
            return Response(
                {'error': 'TCP eliminado correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        """
        Formatear errores para que siempre tengan la estructura {'error': 'mensaje'}
        """
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            # Si ya tiene el formato {'error': 'mensaje'}
            if 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
            
            # Si viene con formato {'numero': ['mensaje']}
            for field, errors in error.detail.items():
                if errors:
                    if isinstance(errors, list):
                        return {'error': str(errors[0])}
                    return {'error': str(errors)}
        
        # Si es ValidationError con detail como lista o string
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        # Si es IntegrityError
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str or "duplicate key" in error_str:
                return {'error': 'ya existe este tcp'}
            return {'error': 'Error de integridad en la base de datos'}
        
        # Por defecto
        return {'error': str(error)}

class NotaViewSet(viewsets.ModelViewSet):
    queryset = Nota.objects.all().select_related(
        'estudiante', 'asignatura', 'semestre_cursado', 'tcp'
    )
    serializer_class = NotaSerializer
    
    ffilter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NotaFilter
    search_fields = [
        'estudiante__nombre', 
        'estudiante__apellidos',
        'semestre_cursado__numero',
        'asignatura__nombre',
        'tcp__numero',
    ]
    ordering_fields = [
        'id', 'nota', 'fecha_registro',
        'estudiante__apellidos', 'estudiante__nombre',
        'asignatura__nombre', 'semestre_cursado__numero',
        'tcp__numero'
    ]
    ordering = ['-fecha_registro']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        nombre_completo = self.request.query_params.get('estudiante_nombre_completo')
        if nombre_completo:
            queryset = queryset.filter(
                models.Q(estudiante__nombre__icontains=nombre_completo) |
                models.Q(estudiante__apellidos__icontains=nombre_completo)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                self._format_error_response(e),
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            
            return Response(
                {'mensaje': 'Nota eliminada correctamente'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _format_error_response(self, error):
        if hasattr(error, 'detail') and isinstance(error.detail, dict):
            if 'error' in error.detail:
                if isinstance(error.detail['error'], list):
                    return {'error': error.detail['error'][0]}
                return {'error': error.detail['error']}
        
        if isinstance(error, ValidationError):
            if hasattr(error, 'detail'):
                if isinstance(error.detail, dict):
                    for field, errors in error.detail.items():
                        if errors:
                            if isinstance(errors, list):
                                return {'error': str(errors[0])}
                            return {'error': str(errors)}
                elif isinstance(error.detail, list):
                    return {'error': str(error.detail[0]) if error.detail else 'Error de validación'}
                elif isinstance(error.detail, str):
                    return {'error': error.detail}
        
        if isinstance(error, IntegrityError):
            error_str = str(error).lower()
            if "unique constraint" in error_str:
                return {'error': 'Ya existe un registro con estos datos'}
            return {'error': 'Error de integridad en la base de datos'}
        
        return {'error': str(error)}
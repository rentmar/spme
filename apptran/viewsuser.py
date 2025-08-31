# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate, login, logout
from .serializerusr import (
    UsuarioSerializer,
    RegistrarSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UsuatiosNicksSerializer
)
from spme_autenticacion.models import Usuario

class RegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = RegistrarSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UsuarioSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            
            if user:
                token, created = Token.objects.get_or_create(user=user)
                login(request, user)
                return Response({
                    'token': token.key,
                    'user': UsuarioSerializer(user).data
                })
        
        return Response(
            {'error': 'Credenciales inválidas'},
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response(
            {'message': 'Sesión cerrada correctamente'},
            status=status.HTTP_200_OK
        )

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Contraseña incorrecta.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Contraseña actualizada correctamente.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioListView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    #permission_classes = [permissions.IsAdminUser]

class UsuarioDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'


class UsuarioPorIdView(generics.RetrieveAPIView):
    """
    Endpoint para obtener un usuario por id
    """
    serializer_class = UsuarioSerializer
    queryset = Usuario.objects.all()
    lookup_field = id

    def get_object(self):
        try:
            user_id = self.kwargs['id']
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            raise NotFound("Usuario no encontrado")
        

#Registros de usuarios
class RegistrarUsuarioView(generics.CreateAPIView):
    """
    Endpoint para registrar nuevos usuarios
    """        
    serializer_class = RegistrarSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Crear token de autenticación
        #token, created = Token.objects.get_or_create(user=user)

        # Preparar datos de respuesta
        user_data = {
            'id': user.id,
            'username': user.username,
            'nombre_completo': f"{user.nombre} {user.paterno} {user.materno}",
            'cargo': user.cargo,
            'permisos': user.permisos
        }

        return Response({
            'usuario': user_data,
            'mensaje': 'Registro exitoso'
        }, status=status.HTTP_201_CREATED)

        
class UserListNicksViews(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuatiosNicksSerializer    
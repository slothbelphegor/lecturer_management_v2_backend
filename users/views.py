from .models import *
from .serializers import *

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Create your views here.
User = get_user_model()


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            })
        return Response(serializer.errors, status=400)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Add user to 'potential_lecturer' group
            group, _ = Group.objects.get_or_create(name='potential_lecturer')
            user.groups.set([group])  # Only this group
            user.save()
            # Return the User except the password since it is write only
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class UserViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = NewUserSerializer
    view_permissions = {
        'list,retrieve,update,create,destroy,partial_update': {
            'user': True,
            'anon': True,
        },
        'me': {
            'user': True,
        }
    }

    def list(self, request):
        queryset = User.objects.all()
        serializer = NewUserSerializer(queryset, many=True)
        return Response(serializer.data)
   
    def create(self, request):
        serializer = NewUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def retrieve(self, request, pk=None):
        try:
            queryset = self.queryset.get(pk=pk)
            serializer = NewUserSerializer(queryset)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Evaluation not found"}, status=404)
    
    def update(self, request, pk=None):
        try:
            evaluation = self.queryset.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=404)

        serializer = self.serializer_class(evaluation, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        # Log lỗi nếu có
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=400)
    
    def partial_update(self, request, pk=None):
        try:
            user = self.queryset.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=404)

        serializer = NewUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print("Update failed:", serializer.errors)
        return Response(serializer.errors, status=400)
    
    def destroy(self, request, pk=None):
        try:
            user = self.queryset.get(pk=pk)
            user.delete()
            return Response(status=204)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        serializer = NewUserSerializer(user)
        return Response(serializer.data)
    

class GroupViewSet(viewsets.ModelViewSet):
    """
    Model View Set for Group
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    http_method_names = ("get", "post", "patch", "delete")

    def list(self, request, *args, **kwargs):
        return super().list(request, fields=("id", "name"), *args, **kwargs)

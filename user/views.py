"""Views for the user API."""

from rest_framework import generics, authentication, permissions, viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (UserSerializer, AuthTokenSerializer,
                              AddressSerializer,
                              CartSerializer)
from user.models import ShippingAddress, CartItem


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create view for auth tokens."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update view for user profile."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class UserAddressView(viewsets.ModelViewSet):
    """Viewsets for user shipping address."""
    serializer_class = AddressSerializer
    queryset = ShippingAddress.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
     
        
class CartItemUserView(viewsets.ModelViewSet):
    """Viewsets for the cart items of a user."""
    serializer_class = CartSerializer
    queryset = CartItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

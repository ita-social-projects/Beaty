"""This module provides all needed views."""
import logging

from django.db.models import Q
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import status
from rest_framework.generics import (GenericAPIView, get_object_or_404, ListCreateAPIView,
                                     ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import CustomUser, Order, Business
from .permissions import IsAdminOrBusinessOwner, IsAccountOwnerOrReadOnly
from .serializers.business_serializers import (BusinessDetailSerializer, BusinessesSerializer,
                                               BusinessAllDetailSerializer)
from .serializers.serializers_customuser import (CustomUserDetailSerializer, CustomUserSerializer,
                                                 ResetPasswordSerializer, UserOrderDetailSerializer)


logger = logging.getLogger(__name__)


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods."""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class UserActivationView(GenericAPIView):
    """Generic view for user account activation."""

    def get(self, request, uidb64, token):
        """Activate user and redirect to personal page."""
        activated_id = int(force_str(urlsafe_base64_decode(uidb64)))

        user = get_object_or_404(CustomUser, id=activated_id)
        user.is_active = True
        user.save()

        logger.info(f"User {user} was activated")

        return redirect(reverse("api:user-detail", kwargs={"pk": activated_id}))


class ResetPasswordView(GenericAPIView):
    """Generic view for reset password."""
    serializer_class = ResetPasswordSerializer
    model = CustomUser

    def post(self, request, uidb64, token):
        """Reset password POST method."""
        user_id = int(force_str(urlsafe_base64_decode(uidb64)))
        user = get_object_or_404(CustomUser, id=user_id)
        self.get_serializer().validate(request.POST)
        user.set_password(request.POST.get("password"))
        user.save()

        logger.info(f"User {user} password was reset")

        return redirect(reverse("api:user-detail", kwargs={"pk": user_id}))


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for users custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy
    """

    permission_classes = [IsAccountOwnerOrReadOnly]

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.

        Makes current user inactive by changing its' field
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()

            logger.info(f"User {instance} was deactivated")

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserOrderDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.

    RUD - Retrieve, Update, Destroy
    """

    queryset = Order.objects.all()
    serializer_class = UserOrderDetailSerializer
    multiple_lookup_fields = ("user", "id")

    def get_object(self):
        """Get order objects by using both order user id and order id lookup fields."""
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            Q(customer=self.kwargs["user"]) | Q(specialist=self.kwargs["user"]),
            id=self.kwargs["id"])
        self.check_object_permissions(self.request, obj)

        user = (obj.customer if self.kwargs["user"] == obj.customer.id else obj.specialist)

        logger.info(f"{obj} was got for the user {user} (id={user.id})")

        return obj


class AllBusinessesListAPIView(ListAPIView):
    """List View for all businesses."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Business.objects.all()
    serializer_class = BusinessesSerializer

    logger.debug("A view to display all businesses has opened")


class OwnerBusinessesListAPIView(ListAPIView):
    """List View for businesses of certain owner."""

    permission_classes = [IsAdminOrBusinessOwner]
    # permission_classes = [AllowAny]

    queryset = Business.objects.all()
    serializer_class = BusinessesSerializer

    logger.debug("A view to display businesses of certain owner opened")

    def list(self, request, owner_id): # noqa
        """Filter businesses of certain owner."""
        self.permission_classes = (IsAdminOrBusinessOwner,)
        queryset = self.get_queryset().filter(owner=owner_id)
        serializer = BusinessesSerializer(queryset, many=True)
        return Response(serializer.data)


class OwnerBusinessDetailRUDView(RetrieveUpdateDestroyAPIView):
    """RUD View for business editing."""

    permission_classes = [IsAdminOrBusinessOwner]
    # permission_classes = [AllowAny]

    queryset = Business.objects.all()
    serializer_class = BusinessAllDetailSerializer

    logger.debug("A view to edit business has opened")


class BusinessDetailRetrieveAPIView(RetrieveAPIView):
    """Retrieve View for business details."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    queryset = Business.objects.all()
    serializer_class = BusinessDetailSerializer

    logger.debug("A view to display certain business has opened")

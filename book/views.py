from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Returns a list of all user profiles that match the specified username parameter, if provided"""
        queryset = self.queryset
        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def perform_create(self, serializer):
        """Creates a new user profile and associates it with the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Updates an existing user profile for the authenticated user"""
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        """Deletes the specified user profile if the authenticated user is the owner"""
        instance.delete()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type=OpenApiTypes.STR,
                description="Filter by book title (ex. ?title=dicaprio)",
            ),
        ]
    )
    @action(detail=True, methods=["GET"], permission_classes=[AllowAny])
    def filtered_list(self, request, *args, **kwargs):
        """Returns a list of all user profiles that match the 'username' parameter if it is specified"""
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return super().get_permissions()

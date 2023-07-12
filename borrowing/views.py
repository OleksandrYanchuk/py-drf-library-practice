from django.utils import timezone, dateformat
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Borrowing
from .permissions import IsOwnerOrAdmin
from .serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingReturnSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['user__email', 'book__title']  # Add additional fields for search
    ordering_fields = ['borrow_date', 'expected_return_date',
                       'actual_return_date']  # Add additional fields for ordering

    def get_queryset(self):
        user = self.request.user
        is_active = self.request.query_params.get('is_active', None)
        user_id = self.request.query_params.get('user_id', None)

        if user.is_superuser:
            borrowings = Borrowing.objects.all()
            if is_active is not None and is_active.lower() == 'true':
                borrowings = borrowings.filter(actual_return_date__isnull=True)
            if user_id is not None:
                borrowings = borrowings.filter(user_id=user_id)
            return borrowings
        elif user.is_authenticated:
            borrowings = Borrowing.objects.filter(user=user)
            if is_active is not None and is_active.lower() == 'true':
                borrowings = borrowings.filter(actual_return_date__isnull=True)
            return borrowings
        else:
            return Borrowing.objects.none()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingListSerializer

        if self.action == "book_return":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Decrease book inventory by 1
        book = serializer.validated_data['book']
        if book.inventory == 0:
            return Response({"detail": "Book is not available for borrowing."}, status=status.HTTP_400_BAD_REQUEST)
        book.inventory -= 1
        book.save()

        serializer.validated_data['user'] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active borrowings",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if borrowing is already returned
        if borrowing.actual_return_date is not None:
            return Response({"detail": "Borrowing has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        borrowing.actual_return_date = dateformat.format(timezone.now(), 'Y-m-d')
        borrowing.save()

        # Increase book inventory by 1
        book = serializer.validated_data['book']
        book.inventory += 1
        book.save()

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data)

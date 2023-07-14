from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PaymentViewSet

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
                  path(
                      "payments/<int:pk>/success/",
                      PaymentViewSet.as_view({"get": "payment_success"}),
                      name="payment_success",
                  ),
                  path(
                      "payments/<int:pk>/cancel/",
                      PaymentViewSet.as_view({"get": "payment_cancel"}),
                      name="payment_cancel",
                  ),
              ] + router.urls

app_name = "payments"

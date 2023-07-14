from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers

from user.serializers import UserSerializer


class UserSerializerTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        serializer = UserSerializer()
        validated_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "is_staff": False,
        }
        user = serializer.create(validated_data)
        self.assertEqual(user.email, validated_data["email"])
        self.assertFalse(user.is_staff)

    def test_update_user_with_password(self):
        user = self.User.objects.create_user(
            email="test@example.com", password="testpassword", is_staff=False
        )
        serializer = UserSerializer(instance=user)
        validated_data = {
            "email": "updated@example.com",
            "password": "updatedpassword",
            "is_staff": True,
        }
        updated_user = serializer.update(user, validated_data)
        self.assertEqual(updated_user.email, validated_data["email"])
        self.assertTrue(updated_user.is_staff)

    def test_update_user_without_password(self):
        user = self.User.objects.create_user(
            email="test@example.com", password="testpassword", is_staff=False
        )
        serializer = UserSerializer(instance=user)
        validated_data = {
            "email": "updated@example.com",
            "is_staff": True,
        }
        updated_user = serializer.update(user, validated_data)
        self.assertEqual(updated_user.email, validated_data["email"])
        self.assertTrue(updated_user.is_staff)

    def test_serializer_invalid_password(self):
        """Test that an invalid password raises a validation error"""
        invalid_data = {
            "email": "testuser@example.com",
            "password": "pass",
            "is_staff": False,
        }
        serializer = UserSerializer(data=invalid_data)

        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

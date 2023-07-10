from django.test import TestCase
from django.contrib.auth import get_user_model
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

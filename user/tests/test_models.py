from django.test import TestCase
from django.contrib.auth import get_user_model


class UserTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        email = "test@example.com"
        password = "testpassword"
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.get_full_name(), "")
        self.assertEqual(user.get_short_name(), "")

    def test_create_superuser(self):
        User = get_user_model()
        email = "admin@example.com"
        password = "adminpassword"
        superuser = User.objects.create_superuser(email=email, password=password)
        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.get_full_name(), "")
        self.assertEqual(superuser.get_short_name(), "")

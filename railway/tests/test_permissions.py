from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.views import APIView

from railway.permissions import IsAdminOrIsAuthenticatedReadOnly


class IsAdminOrIsAuthenticatedReadOnlyTest(TestCase):
    """
    Testing the IsAdminOrIsAuthenticatedReadOnly class
    """

    def setUp(self):
        self.permission = IsAdminOrIsAuthenticatedReadOnly()
        self.view = APIView()

        # Regular authenticated user
        self.normal_user = get_user_model().objects.create_user(
            username="normal_user", password="testpass123", is_staff=False
        )

        # Administrator
        self.admin_user = get_user_model().objects.create_user(
            username="admin_user", password="testpass123", is_staff=True
        )

    def test_anonymous_user_no_access(self):
        """Anonymous user has no access"""

        # Create a simple mock request object
        class MockRequest:
            def __init__(self, method="GET", user=None):
                self.method = method
                self.user = user

        # GET method
        request = MockRequest("GET", AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

        # POST method
        request = MockRequest("POST", AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_normal_user_read_only(self):
        """Regular user has read-only access"""

        class MockRequest:
            def __init__(self, method="GET", user=None):
                self.method = method
                self.user = user

        # Safe methods (GET, HEAD, OPTIONS) - access granted
        for method in ["GET", "HEAD", "OPTIONS"]:
            request = MockRequest(method, self.normal_user)
            self.assertTrue(self.permission.has_permission(request, self.view))

        # Unsafe methods (POST, PUT, PATCH, DELETE) - access denied
        for method in ["POST", "PUT", "PATCH", "DELETE"]:
            request = MockRequest(method, self.normal_user)
            self.assertFalse(self.permission.has_permission(request, self.view))

    def test_admin_user_full_access(self):
        """Administrator has full access"""

        class MockRequest:
            def __init__(self, method="GET", user=None):
                self.method = method
                self.user = user

        # All methods - access granted
        for method in ["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]:
            request = MockRequest(method, self.admin_user)
            self.assertTrue(self.permission.has_permission(request, self.view))

    def test_user_not_authenticated(self):
        """User is not authenticated - no access"""

        class MockRequest:
            def __init__(self, method="GET", user=None):
                self.method = method
                self.user = user

        # User exists but is not authenticated
        request = MockRequest("GET", AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

        # User doesn't exist at all
        request = MockRequest("GET", None)
        self.assertFalse(self.permission.has_permission(request, self.view))
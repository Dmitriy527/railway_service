from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.views import APIView

from railway.permissions import IsAdminOrIsAuthenticatedReadOnly


class IsAdminOrIsAuthenticatedReadOnlyTest(TestCase):
    """
    Тестування класу IsAdminOrIsAuthenticatedReadOnly
    """

    def setUp(self):
        self.permission = IsAdminOrIsAuthenticatedReadOnly()
        self.view = APIView()

        # Звичайний автентифікований користувач
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123',
            is_staff=False
        )

        # Адміністратор
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='testpass123',
            is_staff=True
        )

    def test_anonymous_user_no_access(self):
        """Анонімний користувач не має доступу"""

        # Створюємо простий мок-об'єкт запиту
        class MockRequest:
            def __init__(self, method='GET', user=None):
                self.method = method
                self.user = user

        # GET метод
        request = MockRequest('GET', AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

        # POST метод
        request = MockRequest('POST', AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_normal_user_read_only(self):
        """Звичайний користувач має доступ тільки для читання"""

        class MockRequest:
            def __init__(self, method='GET', user=None):
                self.method = method
                self.user = user

        # Безпечні методи (GET, HEAD, OPTIONS) - доступ є
        for method in ['GET', 'HEAD', 'OPTIONS']:
            request = MockRequest(method, self.normal_user)
            self.assertTrue(self.permission.has_permission(request, self.view))

        # Небезпечні методи (POST, PUT, PATCH, DELETE) - доступу немає
        for method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            request = MockRequest(method, self.normal_user)
            self.assertFalse(self.permission.has_permission(request, self.view))

    def test_admin_user_full_access(self):
        """Адміністратор має повний доступ"""

        class MockRequest:
            def __init__(self, method='GET', user=None):
                self.method = method
                self.user = user

        # Всі методи - доступ є
        for method in ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE']:
            request = MockRequest(method, self.admin_user)
            self.assertTrue(self.permission.has_permission(request, self.view))

    def test_user_not_authenticated(self):
        """Користувач не автентифікований - немає доступу"""

        class MockRequest:
            def __init__(self, method='GET', user=None):
                self.method = method
                self.user = user

        # Користувач є, але не автентифікований
        request = MockRequest('GET', AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, self.view))

        # Користувача взагалі немає
        request = MockRequest('GET', None)
        self.assertFalse(self.permission.has_permission(request, self.view))
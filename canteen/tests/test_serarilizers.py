from django.test import TestCase
from canteen.serializers import RegisterSerializer, LoginSerializer, MenuSerializer, VoteSerializer
from canteen.models import User, menu, Vote
from datetime import date
from rest_framework.exceptions import ValidationError

class RegisterSerializerTest(TestCase):
    def test_valid_registration(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'pass1234',
            'role': 1
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertNotEqual(user.password, 'pass1234')  # Password should be hashed

    def test_missing_field(self):
        data = {
            'first_name': 'Test',
            'email': 'test@example.com',
            'password': 'pass1234',
            'role': 1
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('last_name', serializer.errors)
        self.assertIn('username', serializer.errors)

class LoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass123")

    def test_valid_login(self):
        data = {"username": "user1", "password": "testpass123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, self.user)

    def test_invalid_login(self):
        data = {"username": "user1", "password": "wrongpass"}
        serializer = LoginSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

class MenuSerializerTest(TestCase):
    def test_menu_serialization(self):
        menu_obj = menu.objects.create(date=date.today(), dishes="Thakali Set", max_capacity=50)
        serializer = MenuSerializer(menu_obj)
        self.assertEqual(serializer.data['dishes'], "Thakali Set")

    def test_menu_validation(self):
        data = {
            "date": str(date.today()),
            "dishes": "Burger",
            "max_capacity": 30
        }
        serializer = MenuSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class VoteSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="voter", password="vote123")
        self.menu = menu.objects.create(date=date.today(), dishes="Pizza", max_capacity=25)

    def test_vote_serialization(self):
        vote = Vote.objects.create(user=self.user, menu=self.menu, will_attend=True)
        serializer = VoteSerializer(vote)
        self.assertEqual(serializer.data['menu'], self.menu.id)
        self.assertTrue(serializer.data['will_attend'])

    def test_vote_validation(self):
        data = {
            "menu": self.menu.id,
            "will_attend": True
        }
        serializer = VoteSerializer(data=data)
        serializer.context = {'request': None}  # Needed if you have request.user override
        self.assertTrue(serializer.is_valid())

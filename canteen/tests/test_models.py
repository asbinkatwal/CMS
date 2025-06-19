from django.test import TestCase
from django.contrib.auth import get_user_model
from canteen.models import menu, Vote
from datetime import date

User = get_user_model()

class MenuModelTest(TestCase):

    def setUp(self):
        self.menu1 = menu.objects.create(date=date(2025, 6, 12), dishes="Rice and Curry", max_capacity=50)
        self.menu2 = menu.objects.create(date=date(2025, 6, 13), dishes="Noodles", max_capacity=30)

        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')

    def test_menu_str(self):
        self.assertEqual(str(self.menu1), "menu for 2025-06-12")

    def test_vote_creation(self):
        vote1 = Vote.objects.create(user=self.user1, menu=self.menu1, will_attend=True)
        self.assertTrue(vote1.will_attend)
        self.assertEqual(vote1.menu, self.menu1)

    def test_vote_unique_constraint(self):
        Vote.objects.create(user=self.user2, menu=self.menu2, will_attend=False)
        with self.assertRaises(Exception):
            Vote.objects.create(user=self.user2, menu=self.menu2, will_attend=True)

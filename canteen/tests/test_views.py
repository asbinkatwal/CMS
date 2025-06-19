# from rest_framework.test import APITestCase, APIClient
# from django.urls import reverse
# from canteen.models import User, menu, Vote
# from datetime import date

# class ViewTestCase(APITestCase):
#     def setUp(self):
#         self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="admin123", role=2)
#         self.employee = User.objects.create_user(username="emp", email="emp@example.com", password="emp123", role=1)

#         self.admin_client = APIClient()
#         self.admin_client.force_authenticate(user=self.admin)

#         self.emp_client = APIClient()
#         self.emp_client.force_authenticate(user=self.employee)

#     def test_register_user(self):
#         url = reverse("register_user") 
#         data = {
#             "first_name": "New",
#             "last_name": "User",
#             "username": "newuser",
#             "email": "newuser@example.com",
#             "password": "pass1234",
#             "role": 1
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 201)

#     def test_login_user(self):
#         url = reverse("login_user")
#         data = {
#             "username": "admin",
#             "password": "admin123"
#         }
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("access", response.data)

#     def test_menu_create_by_admin(self):
#         url = reverse("create_menu")
#         data = {"date": str(date.today()), "dishes": "Pizza", "max_capacity": 20}
#         response = self.admin_client.post(url, data)
#         self.assertEqual(response.status_code, 201)

#     def test_menu_create_by_employee_forbidden(self):
#         url = reverse("create_menu")
#         data = {"date": str(date.today()), "dishes": "Rice", "max_capacity": 30}
#         response = self.emp_client.post(url, data)
#         self.assertEqual(response.status_code, 403)

#     def test_submit_vote_once_only(self):
#         m = menu.objects.create(date=date.today(), dishes="Noodles", max_capacity=20)
#         url = reverse("submit_vote")
#         vote_data = {"menu": m.id, "will_attend": True}

#         first = self.emp_client.post(url, vote_data)
#         self.assertEqual(first.status_code, 201)

#         second = self.emp_client.post(url, vote_data)
#         self.assertEqual(second.status_code, 200)
#         self.assertIn("already voted", second.data["message"])

#     def test_check_votes_admin(self):
#         m = menu.objects.create(date=date.today(), dishes="Momo", max_capacity=25)
#         Vote.objects.create(user=self.employee, menu=m, will_attend=True)
#         url = reverse("check_votes")
#         response = self.admin_client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("vote_summary", response.data)

#     def test_logout_user(self):
#         url = reverse("logout_user")
#         response = self.admin_client.post(url)
#         self.assertEqual(response.status_code, 200)

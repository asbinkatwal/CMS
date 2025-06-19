# from django.test import TestCase
# from canteen.models import Vote, menu, User
# from canteen.tasks import generate_report_task
# from datetime import date, datetime, timedelta
# import os
# from django.conf import settings

# class CeleryTaskTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create_user(username="reporter", password="report123", role=1)
#         self.menu = menu.objects.create(date=date.today(), dishes="Thakali", max_capacity=50)
#         Vote.objects.create(user=self.user, menu=self.menu, will_attend=True)

#         self.from_date = date.today().strftime('%Y-%m-%d')
#         self.to_date = date.today().strftime('%Y-%m-%d')

#     def test_generate_csv_report(self):
#         result = generate_report_task(self.from_date, self.to_date, "csv")
#         self.assertEqual(result['status'], 'success')
#         file_path = os.path.join(settings.MEDIA_ROOT, result['file_path'])
#         self.assertTrue(os.path.exists(file_path))

#     def test_generate_pdf_report(self):
#         result = generate_report_task(self.from_date, self.to_date, "pdf")
#         self.assertEqual(result['status'], 'success')
#         file_path = os.path.join(settings.MEDIA_ROOT, result['file_path'])
#         self.assertTrue(os.path.exists(file_path))

#     def test_generate_no_data(self):
#         old_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
#         result = generate_report_task(old_date, old_date, "csv")
#         self.assertEqual(result['status'], 'no_data')

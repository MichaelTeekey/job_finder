from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthViewsTests(APITestCase):
    def setUp(self):
        self.register_url = '/api/register/'
        self.login_url = '/api/login/'

    def test_register_success(self):
        data = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'strong-password-123',
            'role': 'student'
        }
        resp = self.client.post(self.register_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['email'], data['email'])
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_register_duplicate_email(self):
        email = 'bob@example.com'
        User.objects.create_user(username='bob', email=email, password='pwd123')
        data = {'username': 'bob2', 'email': email, 'password': 'pwd456'}
        resp = self.client.post(self.register_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', resp.data)

    def test_login_success(self):
        email = 'carol@example.com'
        password = 'login-pass-1'
        # create user in DB first
        User.objects.create_user(username='carol', email=email, password=password)
        data = {'email': email, 'password': password}
        resp = self.client.post(self.login_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['email'], email)

    def test_login_invalid_credentials(self):
        email = 'dave@example.com'
        password = 'correct-pass'
        User.objects.create_user(username='dave', email=email, password=password)
        data = {'email': email, 'password': 'wrong-pass'}
        resp = self.client.post(self.login_url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', resp.data)
# from django.contrib.auth import get_user_model
# from rest_framework import status
# from rest_framework.test import APITestCase
# from .models import Job
# import uuid

# User = get_user_model()


# class AdminJobViewsTests(APITestCase):
#     def setUp(self):
#         # users
#         self.admin = User.objects.create_user(
#             username='admin', email='admin@example.com', password='adminpass', role='admin', is_staff=True
#         )
#         self.employer = User.objects.create_user(
#             username='emp', email='emp@example.com', password='emppass', role='employer'
#         )

#         # jobs
#         self.unapproved_job = Job.objects.create(
#             employer=self.employer,
#             title='Unapproved Internship',
#             description='To be approved',
#             approved=False
#         )
#         self.approved_job = Job.objects.create(
#             employer=self.employer,
#             title='Approved Internship',
#             description='Already approved',
#             approved=True
#         )

#         self.pending_url = '/api/admin/pending-jobs/'
#         self.approve_url = f'/api/admin/approve/{self.unapproved_job.id}/'

#     def test_pending_jobs_visible_to_admin_only(self):
#         # admin can view pending jobs
#         self.client.force_authenticate(user=self.admin)
#         resp = self.client.get(self.pending_url)
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         # only unapproved jobs should be returned
#         ids = [item.get('id') for item in resp.data]
#         self.assertIn(str(self.unapproved_job.id), ids)
#         self.assertNotIn(str(self.approved_job.id), ids)

#     def test_pending_jobs_forbidden_for_non_admin(self):
#         self.client.force_authenticate(user=self.employer)
#         resp = self.client.get(self.pending_url)
#         self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

#     def test_admin_can_approve_job(self):
#         self.client.force_authenticate(user=self.admin)
#         resp = self.client.post(self.approve_url)
#         self.assertEqual(resp.status_code, status.HTTP_200_OK)
#         self.assertEqual(resp.data.get('message'), 'Job approved successfully.')
#         # refresh from db
#         self.unapproved_job.refresh_from_db()
#         self.assertTrue(self.unapproved_job.approved)

#     def test_non_admin_cannot_approve(self):
#         self.client.force_authenticate(user=self.employer)
#         resp = self.client.post(self.approve_url)
#         self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
#         self.unapproved_job.refresh_from_db()
#         self.assertFalse(self.unapproved_job.approved)
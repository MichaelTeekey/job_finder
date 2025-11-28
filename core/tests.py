from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Job
import uuid

User = get_user_model()


class AdminJobViewsTests(APITestCase):
    def setUp(self):
        # users
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com', password='adminpass', role='admin', is_staff=True
        )
        self.employer = User.objects.create_user(
            username='emp', email='emp@example.com', password='emppass', role='employer'
        )

        # jobs
        self.unapproved_job = Job.objects.create(
            employer=self.employer,
            title='Unapproved Internship',
            description='To be approved',
            approved=False
        )
        self.approved_job = Job.objects.create(
            employer=self.employer,
            title='Approved Internship',
            description='Already approved',
            approved=True
        )

        self.pending_url = '/api/admin/pending-jobs/'
        self.approve_url = f'/api/admin/approve/{self.unapproved_job.id}/'

    def test_pending_jobs_visible_to_admin_only(self):
        # admin can view pending jobs
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.pending_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # only unapproved jobs should be returned
        ids = [item.get('id') for item in resp.data]
        self.assertIn(str(self.unapproved_job.id), ids)
        self.assertNotIn(str(self.approved_job.id), ids)

    def test_pending_jobs_forbidden_for_non_admin(self):
        self.client.force_authenticate(user=self.employer)
        resp = self.client.get(self.pending_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_approve_job(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(self.approve_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('message'), 'Job approved successfully.')
        # refresh from db
        self.unapproved_job.refresh_from_db()
        self.assertTrue(self.unapproved_job.approved)

    def test_non_admin_cannot_approve(self):
        self.client.force_authenticate(user=self.employer)
        resp = self.client.post(self.approve_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.unapproved_job.refresh_from_db()
        self.assertFalse(self.unapproved_job.approved)
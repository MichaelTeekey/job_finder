from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Job, Application, Resume
import io
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class JobFinderAPITest(APITestCase):

    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            username="student1", email="student1@test.com", password="password123", role="student"
        )
        self.employer = User.objects.create_user(
            username="employer1", email="employer1@test.com", password="password123", role="employer"
        )
        self.admin = User.objects.create_superuser(
            username="admin1", email="admin1@test.com", password="password123"
        )

        # Initialize client
        self.client = APIClient()

    # -----------------------------------------
    # AUTH TESTS
    # -----------------------------------------
    def test_register_student(self):
        url = reverse("register")
        data = {"username": "student2", "email": "student2@test.com", "password": "pass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["role"], "student")

    def test_login_success(self):
        url = reverse("login")
        data = {"email": "student1@test.com", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_fail_wrong_password(self):
        url = reverse("login")
        data = {"email": "student1@test.com", "password": "wrongpass"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -----------------------------------------
    # JOB TESTS
    # -----------------------------------------
    def test_employer_create_job(self):
        self.client.force_authenticate(user=self.employer)
        url = reverse("employer-job-create")
        data = {"title": "Dev Job", "description": "Developer needed", "location": "Remote", "duration": "3 months", "skills": "Python"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Dev Job")
        self.assertFalse(response.data["approved"])

    def test_student_list_jobs_only_approved(self):
        # Create approved and unapproved jobs
        Job.objects.create(title="Job 1", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=True)
        Job.objects.create(title="Job 2", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=False)
        url = reverse("job-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["approved"], True)

    # -----------------------------------------
    # APPLICATION TESTS
    # -----------------------------------------
    def test_student_apply_job(self):
        job = Job.objects.create(title="Job Apply", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=True)
        self.client.force_authenticate(user=self.student)
        url = reverse("apply-job", kwargs={"job_id": job.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["job"]["title"], "Job Apply")

    def test_student_cannot_apply_twice(self):
        job = Job.objects.create(title="Job Apply", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=True)
        Application.objects.create(job=job, student=self.student, match_score=90)
        self.client.force_authenticate(user=self.student)
        url = reverse("apply-job", kwargs={"job_id": job.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_list_their_applications(self):
        job = Job.objects.create(title="Job Apply", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=True)
        Application.objects.create(job=job, student=self.student, match_score=90)
        self.client.force_authenticate(user=self.student)
        url = reverse("student-applications")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # -----------------------------------------
    # RESUME UPLOAD
    # -----------------------------------------
    def test_student_upload_resume(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("upload-resume")
        resume_file = SimpleUploadedFile("resume.pdf", b"dummy content", content_type="application/pdf")
        response = self.client.post(url, {"file": resume_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("resume_score", response.data)

    # -----------------------------------------
    # EMPLOYER APPLICATION STATUS UPDATE
    # -----------------------------------------
    def test_employer_update_application_status(self):
        job = Job.objects.create(title="Job", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=True)
        app = Application.objects.create(job=job, student=self.student, match_score=90)
        self.client.force_authenticate(user=self.employer)
        url = reverse("update-application-status", kwargs={"application_id": app.id})
        response = self.client.post(url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, "accepted")

    # -----------------------------------------
    # ADMIN APPROVE JOB
    # -----------------------------------------
    def test_admin_approve_job(self):
        job = Job.objects.create(title="Job", description="Desc", location="Loc", duration="1 mo", skills="Python", employer=self.employer, approved=False)
        self.client.force_authenticate(user=self.admin)
        url = reverse("approve-job", kwargs={"job_id": job.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertTrue(job.approved)

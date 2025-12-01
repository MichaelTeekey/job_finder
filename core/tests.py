import io
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Job, Application, Resume  # adjust import paths
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class JobApplicationTests(APITestCase):

    def setUp(self):
        # ----------------------------
        # Create users
        # ----------------------------
        self.student = User.objects.create_user(
            username="student1", email="student1@test.com", password="123456", role="student"
        )
        self.employer = User.objects.create_user(
            username="employer1", email="emp1@test.com", password="123456", role="employer"
        )
        self.other_employer = User.objects.create_user(
            username="employer2", email="emp2@test.com", password="123456", role="employer"
        )
        self.admin = User.objects.create_user(
            username="admin1", email="admin@test.com", password="123456", role="admin", is_staff=True, is_superuser=True
        )

        # ----------------------------
        # JWT tokens
        # ----------------------------
        self.student_token = str(RefreshToken.for_user(self.student).access_token)
        self.emp_token = str(RefreshToken.for_user(self.employer).access_token)
        self.other_emp_token = str(RefreshToken.for_user(self.other_employer).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)

    # ----------------------------
    # Helper method to auth client
    # ----------------------------
    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ----------------------------
    # STUDENT TESTS
    # ----------------------------
    def test_student_can_view_jobs(self):
        Job.objects.create(employer=self.employer, title="Backend", description="Django", approved=True)
        self.auth(self.student_token)
        res = self.client.get(reverse("job-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) >= 1)

    def test_student_cannot_create_jobs(self):
        self.auth(self.student_token)
        res = self.client.post(reverse("employer-job-create"), {"title": "Hack", "description": "Illegal"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_apply_once_and_cannot_reapply(self):
        job = Job.objects.create(employer=self.employer, title="Intern", description="Desc", approved=True)
        self.auth(self.student_token)
        # first application
        res1 = self.client.post(reverse("apply-job", args=[job.id]))
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        # second application → fail
        res2 = self.client.post(reverse("apply-job", args=[job.id]))
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_apply_unapproved_job(self):
        job = Job.objects.create(employer=self.employer, title="Unapproved", description="Desc", approved=False)
        self.auth(self.student_token)
        res = self.client.post(reverse("apply-job", args=[job.id]))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_can_view_own_applications(self):
        job = Job.objects.create(employer=self.employer, title="Intern", description="Desc", approved=True)
        Application.objects.create(job=job, student=self.student)
        self.auth(self.student_token)
        res = self.client.get(reverse("student-applications"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_student_resume_upload_success_and_fail(self):
        self.auth(self.student_token)
        # upload with file → success
        file = io.BytesIO(b"Test resume content")
        file.name = "resume.pdf"
        res = self.client.post(reverse("upload-resume"), {"file": file}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # upload without file → fail
        res2 = self.client.post(reverse("upload-resume"), {})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # EMPLOYER TESTS
    # ----------------------------
    def test_employer_create_update_delete_job(self):
        self.auth(self.emp_token)
        # create
        res_create = self.client.post(reverse("employer-job-create"), {"title": "Backend Dev", "description": "Desc"})
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        job_id = res_create.data["id"]
        # update
        res_update = self.client.put(reverse("employer-job-update", args=[job_id]), {"title": "Updated", "description": "New Desc"})
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        # delete
        res_delete = self.client.delete(reverse("employer-job-delete", args=[job_id]))
        self.assertEqual(res_delete.status_code, status.HTTP_200_OK)

    def test_other_employer_cannot_edit_or_delete_others_job(self):
        job = Job.objects.create(employer=self.employer, title="Job", description="Desc")
        self.auth(self.other_emp_token)
        res_update = self.client.put(reverse("employer-job-update", args=[job.id]), {"title": "Hack", "description": "No"})
        self.assertEqual(res_update.status_code, status.HTTP_403_FORBIDDEN)
        res_delete = self.client.delete(reverse("employer-job-delete", args=[job.id]))
        self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_can_view_applications_and_update_status(self):
        job = Job.objects.create(employer=self.employer, title="Job", description="Desc", approved=True)
        app = Application.objects.create(job=job, student=self.student)
        self.auth(self.emp_token)
        # view applications
        res = self.client.get(reverse("employer-job-applications", args=[job.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # update application status
        res2 = self.client.post(reverse("update-application-status", args=[app.id]), {"status": "accepted"})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, "accepted")
        # other employer cannot update
        self.auth(self.other_emp_token)
        res3 = self.client.post(reverse("update-application-status", args=[app.id]), {"status": "rejected"})
        self.assertEqual(res3.status_code, status.HTTP_403_FORBIDDEN)

    # ----------------------------
    # ADMIN TESTS
    # ----------------------------
    def test_admin_can_view_pending_and_approve(self):
        job = Job.objects.create(employer=self.employer, title="Pending", description="Desc", approved=False)
        self.auth(self.admin_token)
        # view pending
        res = self.client.get(reverse("pending-jobs"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # approve
        res2 = self.client.post(reverse("approve-job", args=[job.id]))
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertTrue(job.approved)

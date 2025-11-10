from django.urls import path
from . import api_views, auth_views

urlpatterns = [
    # AUTH ROUTES
    path('api/register/', auth_views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', auth_views.LoginAPIView.as_view(), name='login'),
    # STUDENT ROUTES
    path('api/jobs/', api_views.JobListAPIView.as_view(), name='job-list'),
    path('api/apply/<uuid:job_id>/', api_views.ApplyJobAPIView.as_view(), name='apply-job'),
    path('api/upload-resume/', api_views.UploadResumeAPIView.as_view(), name='upload-resume'),

    # EMPLOYER ROUTES
    path('api/employer/jobs/', api_views.EmployerJobListAPIView.as_view(), name='employer-jobs'),
    path('api/employer/jobs/create/', api_views.EmployerJobCreateAPIView.as_view(), name='employer-job-create'),
    path('api/employer/applications/', api_views.ViewApplicationsAPIView.as_view(), name='employer-applications'),

    # ADMIN ROUTES
    path('api/admin/pending-jobs/', api_views.PendingJobsAPIView.as_view(), name='pending-jobs'),
    path('api/admin/approve/<uuid:job_id>/', api_views.ApproveJobAPIView.as_view(), name='approve-job'),
]

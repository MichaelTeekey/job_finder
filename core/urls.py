from django.urls import path
from . import api_views, auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
    
urlpatterns = [
    # AUTH ROUTES
    path('api/register/', auth_views.RegisterAPIView.as_view(), name='register'),
    path('api/login/', auth_views.LoginAPIView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # STUDENT ROUTES
    path('api/jobs/', api_views.JobListAPIView.as_view(), name='job-list'),
    path('api/jobs/<uuid:job_id>/', api_views.JobDetailAPIView.as_view(), name='job-detail'),
    path('api/apply/<uuid:job_id>/', api_views.ApplyJobAPIView.as_view(), name='apply-job'),
    path('api/student/applications/', api_views.StudentApplicationsAPIView.as_view(), name='student-applications'),
    path('api/upload-resume/', api_views.UploadResumeAPIView.as_view(), name='upload-resume'),

    # EMPLOYER ROUTES
    path('api/employer/jobs/', api_views.EmployerJobListAPIView.as_view(), name='employer-jobs'),
    path('api/employer/jobs/create/', api_views.EmployerJobCreateAPIView.as_view(), name='employer-job-create'),
    path('api/employer/jobs/<uuid:job_id>/update/', api_views.EmployerJobUpdateAPIView.as_view(), name='employer-job-update'),
    path('api/employer/jobs/<uuid:job_id>/delete/', api_views.EmployerJobDeleteAPIView.as_view(), name='employer-job-delete'),
    path('api/employer/jobs/<uuid:job_id>/applications/', api_views.EmployerJobApplicationsAPIView.as_view(), name='employer-job-applications'),
    path('api/employer/applications/<uuid:application_id>/status/', api_views.UpdateApplicationStatusAPIView.as_view(), name='update-application-status'),

    # ADMIN ROUTES
    path('api/admin/pending-jobs/', api_views.PendingJobsAPIView.as_view(), name='pending-jobs'),
    path('api/admin/approve/<uuid:job_id>/', api_views.ApproveJobAPIView.as_view(), name='approve-job'),
]

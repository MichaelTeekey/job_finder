from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import User, Job, Application, Resume
from .serializers import (
    UserSerializer,
    JobSerializer,
    JobCreateSerializer,
    ApplicationSerializer,
    ResumeSerializer
)
import random

# ============================================================
# CUSTOM PERMISSIONS
# ============================================================

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employer'

# ============================================================
# STUDENT ENDPOINTS
# ============================================================

class JobListAPIView(generics.ListAPIView):
    """List all approved jobs for students"""
    queryset = Job.objects.filter(approved=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

class JobDetailAPIView(generics.RetrieveAPIView):
    """View one job details"""
    queryset = Job.objects.filter(approved=True)
    serializer_class = JobSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'
    permission_classes = [permissions.AllowAny]

class ApplyJobAPIView(APIView):
    """Student applies for a job"""
    permission_classes = [IsStudent]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, approved=True)
        if Application.objects.filter(job=job, student=request.user).exists():
            return Response({'message': 'Already applied!'}, status=status.HTTP_400_BAD_REQUEST)

        app = Application.objects.create(
            job=job,
            student=request.user,
            match_score=random.randint(50, 100)
        )
        return Response(ApplicationSerializer(app).data, status=status.HTTP_201_CREATED)

class StudentApplicationsAPIView(generics.ListAPIView):
    """Student views their applications"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(student=self.request.user)

class UploadResumeAPIView(APIView):
    """Student uploads a resume"""
    permission_classes = [IsStudent]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        resume = Resume.objects.create(
            student=request.user,
            file=file,
            resume_score=random.randint(60, 95),
            feedback='Add more technical details and expand soft skills.'
        )
        return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)

# ============================================================
# EMPLOYER ENDPOINTS
# ============================================================

class EmployerJobListAPIView(generics.ListAPIView):
    """List all jobs posted by this employer"""
    serializer_class = JobSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)

class EmployerJobCreateAPIView(generics.CreateAPIView):
    serializer_class = JobCreateSerializer
    permission_classes = [IsEmployer]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user, approved=False)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        
        job = serializer.instance
        return Response(JobSerializer(job).data, status=status.HTTP_201_CREATED)

class EmployerJobUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobCreateSerializer
    permission_classes = [IsEmployer]
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)

class EmployerJobDeleteAPIView(APIView):
    permission_classes = [IsEmployer]

    def delete(self, request, job_id):
        job = get_object_or_404(Job, id=job_id, employer=request.user)
        job.delete()
        return Response({'message': 'Job deleted successfully.'}, status=status.HTTP_200_OK)

class EmployerJobApplicationsAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Application.objects.filter(job__id=job_id, job__employer=self.request.user)

class UpdateApplicationStatusAPIView(APIView):
    permission_classes = [IsEmployer]

    def post(self, request, application_id):
        app = get_object_or_404(Application, id=application_id, job__employer=request.user)
        new_status = request.data.get('status')
        if new_status not in ['accepted', 'rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        app.status = new_status
        app.save()
        return Response(ApplicationSerializer(app).data, status=status.HTTP_200_OK)

# ============================================================
# ADMIN ENDPOINTS
# ============================================================

class PendingJobsAPIView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Job.objects.filter(approved=False)

class ApproveJobAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        job.approved = True
        job.save()
        return Response({'message': 'Job approved successfully.'}, status=status.HTTP_200_OK)

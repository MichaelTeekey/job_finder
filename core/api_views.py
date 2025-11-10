from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
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


# -------------------------------------------------
# STUDENT ENDPOINTS
# -------------------------------------------------
class JobListAPIView(generics.ListAPIView):
    """List all approved jobs for students"""
    queryset = Job.objects.filter(approved=True)
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]


class ApplyJobAPIView(APIView):
    """Student applies for a job"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        if request.user.role != 'student':
            return Response({'error': 'Only students can apply.'}, status=status.HTTP_403_FORBIDDEN)

        # Prevent duplicate applications
        if Application.objects.filter(job=job, student=request.user).exists():
            return Response({'message': 'Already applied!'}, status=status.HTTP_400_BAD_REQUEST)

        app = Application.objects.create(
            job=job,
            student=request.user,
            match_score=random.randint(50, 100)
        )
        return Response(ApplicationSerializer(app).data, status=status.HTTP_201_CREATED)


class UploadResumeAPIView(APIView):
    """Upload a resume and simulate AI feedback"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != 'student':
            return Response({'error': 'Only students can upload resumes.'}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        resume = Resume.objects.create(
            student=request.user,
            file=file,
            resume_score=random.randint(60, 95),
            feedback='Add more technical details and soft skills.'
        )
        return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)


# -------------------------------------------------
# EMPLOYER ENDPOINTS
# -------------------------------------------------
class EmployerJobListAPIView(generics.ListAPIView):
    """Employer's own jobs"""
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user)


class EmployerJobCreateAPIView(generics.CreateAPIView):
    """Employer posts a new internship"""
    serializer_class = JobCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'employer':
            raise permissions.PermissionDenied("Only employers can post jobs.")
        serializer.save(employer=self.request.user, approved=False)


class ViewApplicationsAPIView(generics.ListAPIView):
    """Employer views student applications for their jobs"""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(job__employer=self.request.user)


# -------------------------------------------------
# ADMIN ENDPOINTS
# -------------------------------------------------
class PendingJobsAPIView(generics.ListAPIView):
    """Admin sees all pending jobs"""
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Job.objects.filter(approved=False)


class ApproveJobAPIView(APIView):
    """Admin approves a job"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        job.approved = True
        job.save()
        return Response({'message': 'Job approved successfully.'})

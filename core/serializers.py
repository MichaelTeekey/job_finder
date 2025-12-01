from rest_framework import serializers
from .models import User, Job, Application, Resume

# ---------------------------------------------------------
# USER SERIALIZER
# ---------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


# ---------------------------------------------------------
# JOB SERIALIZER (for reading job data, nested employer info)
# ---------------------------------------------------------
class JobSerializer(serializers.ModelSerializer):
    employer = UserSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id',
            'employer',
            'title',
            'description',
            'location',
            'duration',
            'skills',
            'approved',
            'created_at',
        ]


# ---------------------------------------------------------
# JOB CREATE / UPDATE SERIALIZER (employer creates/edits job)
# ---------------------------------------------------------
class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'duration', 'skills']


# ---------------------------------------------------------
# APPLICATION SERIALIZER (nested student + job info)
# ---------------------------------------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'student',
            'status',       # allow employer to update (accepted/rejected)
            'match_score',  # read-only score generated on application
            'created_at',
        ]
        read_only_fields = ['match_score', 'created_at']


# ---------------------------------------------------------
# RESUME SERIALIZER (nested student info)
# ---------------------------------------------------------
class ResumeSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Resume
        fields = [
            'id',
            'student',
            'file',
            'resume_score',
            'feedback',
            'uploaded_at',
        ]
        read_only_fields = ['resume_score', 'feedback', 'uploaded_at']

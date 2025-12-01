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
# JOB SERIALIZER (for reading job data)
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
# JOB CREATE SERIALIZER (employer creates job)
# ---------------------------------------------------------
class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'duration', 'skills']


# ---------------------------------------------------------
# APPLICATION SERIALIZER
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
            'status',
            'match_score',
            'created_at',
        ]


# ---------------------------------------------------------
# RESUME SERIALIZER
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
        read_only_fields = ['resume_score', 'feedback']

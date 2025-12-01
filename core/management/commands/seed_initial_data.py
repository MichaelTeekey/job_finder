from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Job  # adjust import if needed
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with employer accounts and job listings"

    def handle(self, *args, **kwargs):

        companies = [
            "Econet Wireless Zimbabwe",
            "Delta Corporation",
            "CBZ Holdings",
            "ZIMRA (Zimbabwe Revenue Authority)",
            "Dendairy Zimbabwe",
            "MTN Group",
            "Shoprite Holdings",
            "Sasol",
            "Pick n Pay",
            "Vodacom"
        ]

        job_titles = [
            "Software Engineer",
            "Data Analyst",
            "Marketing Officer",
            "Human Resources Assistant",
            "Finance Intern",
            "Sales Representative",
            "IT Support Technician",
            "Customer Service Agent",
            "Project Coordinator",
            "Business Analyst",
            "Graphic Designer",
            "Supply Chain Assistant"
        ]

        descriptions = [
            "Looking for a motivated individual to join our team.",
            "Must have strong communication and technical skills.",
            "Great opportunity to grow within the company.",
            "We value teamwork, innovation and dedication.",
        ]

        locations = [
            "Harare", "Bulawayo", "Johannesburg", "Cape Town",
            "Gaborone", "Pretoria", "Lusaka"
        ]

        created_employers = []

        self.stdout.write(self.style.NOTICE("Seeding employers..."))

        # ------------------------------------------
        # CREATE EMPLOYERS (REQUIRED FIELDS)
        # ------------------------------------------
        for company in companies:

            username = company.lower().replace(" ", "_").replace("(", "").replace(")", "")
            email = f"{username}@example.com"

            employer = User.objects.filter(email=email).first()
            if not employer:
                employer = User(
                    username=username,
                    email=email,
                    role="employer",
                )
                employer.set_password("Pass1234!")  # secure default
                employer.save()

                self.stdout.write(self.style.SUCCESS(f"Created employer: {company}"))
            else:
                self.stdout.write(self.style.WARNING(f"Employer already exists: {company}"))

            created_employers.append(employer)

        # ------------------------------------------
        # CREATE JOBS
        # ------------------------------------------
        self.stdout.write(self.style.NOTICE("Seeding jobs..."))

        for employer in created_employers:
            for i in range(6):  # At least 6 jobs per employer
                title = random.choice(job_titles)

                job = Job.objects.create(
                    employer=employer,
                    title=title,
                    description=random.choice(descriptions),
                    location=random.choice(locations),
                    duration=f"{random.randint(1, 12)} months",
                    skills="Communication, Teamwork, Problem-Solving",
                    approved=True  # seeded jobs auto-approved
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Created job: {job.title} for {employer.username}")
                )

        self.stdout.write(self.style.SUCCESS("✔ Database seeding completed successfully"))

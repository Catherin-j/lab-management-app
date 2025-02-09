from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

class Lab(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labs')

    def __str__(self):
        return self.name

class Assignment(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='assignments')
    question = models.TextField()
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')

    def __str__(self):
        return f"{self.question} - {self.lab.name}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    output = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    score = models.IntegerField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews')

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.question}"
from django.db import models
from django.conf import settings
from django.utils.timesince import timesince
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
import os
import datetime

## Model for Classroom
class Classrooms(models.Model):
    classroom_name = models.CharField(max_length=100)
    class_code = models.CharField(max_length=10, default="0000000")

    class Meta:
        app_label = "auth"

    def __str__(self):
        return self.classroom_name


## Model for Student
class Students(models.Model):
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom_id = models.ForeignKey(Classrooms, on_delete=models.CASCADE)

    class Meta:
        app_label = "auth"


## Model for Teacher
class Teachers(models.Model):
    teacher_id = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom_id = models.ForeignKey(Classrooms, on_delete=models.CASCADE)

    class Meta:
        app_label = "auth"


## Model for Notification
class Notification(models.Model):
    classroom_id = models.ForeignKey(Classrooms, on_delete=models.CASCADE)
    header = models.TextField(null=True)
    message = models.TextField(null=True)
    posted_date = models.DateField(auto_now_add=True)
    posted_time = models.TimeField(auto_now_add=True)
    author = models.TextField(null=True)

    class Meta:
        app_label = "auth"


## Model for Assignment
class Assignments(models.Model):
    assignment_name = models.CharField(max_length=50)
    classroom_id = models.ForeignKey(Classrooms, on_delete=models.CASCADE)
    due_date = models.DateField()
    due_time = models.TimeField(default=datetime.time(10, 10))
    posted_date = models.DateField(auto_now_add=True)
    instructions = models.TextField()
    num_ques = models.IntegerField(
        default=10, validators=[MaxValueValidator(180), MinValueValidator(1)]
    )
    positive_marks = models.IntegerField(
        default=4, validators=[MaxValueValidator(1000), MinValueValidator(1)]
    )
    negative_marks = models.IntegerField(
        default=1, validators=[MaxValueValidator(1000), MinValueValidator(0)]
    )
    question_file = models.FileField(upload_to="documents/")
    ans_key = models.TextField(null=True, blank=True)
    result = models.FileField(upload_to="documents/")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.assignment_name

    class Meta:
        app_label = "auth"


## Model for Submissions
class Submissions(models.Model):
    assignment_id = models.ForeignKey(Assignments, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    submitted_date = models.DateField(auto_now_add=True)
    submitted_time = models.TimeField(auto_now_add=True)
    submitted_on_time = models.BooleanField(default=True)
    submitted_ans = models.TextField(null=True)
    marks_alloted = models.IntegerField(default=0)
    response_key = models.TextField(null=True)

    class Meta:
        app_label = "auth"

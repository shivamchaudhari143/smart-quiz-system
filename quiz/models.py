from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField(blank=True, default="")
    duration = models.IntegerField(help_text="Duration in minutes")
    total_marks = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.TextField()

    option1 = models.CharField(max_length=200, default="")
    option2 = models.CharField(max_length=200, default="")
    option3 = models.CharField(max_length=200, default="")
    option4 = models.CharField(max_length=200, default="")

    correct_option = models.IntegerField(default=1)

    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.question





class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

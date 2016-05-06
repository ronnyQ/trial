from django.db import models
from django.contrib.auth.models import User

# This model stores all courses that use the ARS
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

# This model stores which tutors are assigned to which course
class Tutor_assignment(models.Model):
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)

    def __str__(self):
        return "User: {0}, Course: {1}".format(self.user.username, self.course.title)

# This model stores individual sessions (lectures/lessons) of each course
class Session(models.Model):
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=255)
    url_code = models.CharField(max_length=5, default='')
    running = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# This model stores individual questions
class Question(models.Model):
    session = models.ForeignKey(Session)
    question_body = models.TextField()

    def __str__(self):
        return self.question_body


# This model stores each possible answer for a question
class Question_option(models.Model):
    question = models.ForeignKey(Question)
    body = models.TextField()
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.body


class Current_question(models.Model):
    session = models.ForeignKey(Session)
    question = models.ForeignKey(Question)
    start_time = models.DateTimeField()
    run_time = models.PositiveIntegerField()

    def __str__(self):
        return "Session: {0}".format(self.session.title)


class Session_run(models.Model):
    session = models.ForeignKey(Session)
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Session: {0}, Start Time: {1}".format(self.session.title, self.start_time)


# This model stores which question option was picked by a student
class Student_response(models.Model):
    session_run = models.ForeignKey(Session_run)
    option = models.ForeignKey(Question_option)

    def __str__(self):
        return "Option: {0}, Session Run: {1}".format(self.option.body, self.session_run.id)


class Responding_student(models.Model):
    session = models.ForeignKey(Session)
    responder_uuid = models.CharField(max_length=32)
    last_seen = models.DateTimeField()

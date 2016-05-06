from django.contrib import admin
from .models import *

@admin.register(Course)
class Course_admin(admin.ModelAdmin):
    pass

@admin.register(Tutor_assignment)
class Tutor_assignment_admin(admin.ModelAdmin):
    pass

@admin.register(Session)
class Session_admin(admin.ModelAdmin):
    pass

@admin.register(Question)
class Question_admin(admin.ModelAdmin):
    pass

@admin.register(Question_option)
class Question_option_admin(admin.ModelAdmin):
    pass

@admin.register(Current_question)
class Current_question_admin(admin.ModelAdmin):
    pass

@admin.register(Student_response)
class Student_response_admin(admin.ModelAdmin):
    pass

@admin.register(Session_run)
class Session_run_admin(admin.ModelAdmin):
    pass

@admin.register(Responding_student)
class Responding_student_admin(admin.ModelAdmin):
    pass
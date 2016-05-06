from main.models import Tutor_assignment
from django.core.exceptions import ObjectDoesNotExist

def course_assignments_processor(request):            
    if request.user:
        course_assignments = Tutor_assignment.objects.filter(user=request.user.id) # Get all course assignments
    else:
        course_assignments = []

    return {'course_assignments': course_assignments}
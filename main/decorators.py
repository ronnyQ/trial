from django.http import HttpResponseRedirect

# If a course has not been seleceted in the tutor area, redirect to the tutor home
# page which will show a message telling the user to select a course
def tutor_course_is_selected(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if 'course_id' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/tutor/')
    return _wrapped_view_func
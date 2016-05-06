from django.shortcuts import render, render_to_response
from main.decorators import tutor_course_is_selected
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from main.models import Tutor_assignment, Session, Question, Question_option, Current_question, Student_response, Session_run, Responding_student
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from tutor.helpers import *
from tutor.statistics import Statistics
from django.utils import timezone
import json
import datetime

@login_required
def welcome(request):
    return render_to_response('welcome.html', context_instance=RequestContext(request))

@csrf_exempt
@login_required
def select_course(request):
    course_id = int(request.POST['course'])

    # We first must check if the tutor is actually assigned to this course
    assignments = Tutor_assignment.objects.filter(user=request.user, course_id=course_id)

    # Could throw a pretty error here but in this should never happen in normal use of
    # the application
    if len(assignments) == 0:
        return HttpResponseRedirect('/tutor/')

    # We have verified that the tutor is assigned to the course
    # so we can set the session variable
    request.session['course_id'] = course_id
    return HttpResponseRedirect('/tutor/')

@login_required
@tutor_course_is_selected
def sessions(request):
    data = {}

    data['sessions'] = Session.objects.filter(course_id=request.session['course_id'])

    return render_to_response('sessions.html', data, context_instance=RequestContext(request))

@login_required
@tutor_course_is_selected
def new_session(request):
    data = {}

    # If the form has been submitted, add the session
    if request.method == 'POST':
        session_title = request.POST['session-title']

        # Title must be set, if not set an error message
        if session_title:
            # Add the session then redirect to the page to allow editing of it
            s = Session()
            s.title = session_title
            s.course_id = request.session['course_id']
            s.save()

            return HttpResponseRedirect('/tutor/sessions/{0}'.format(s.pk))
        else:
            data['error'] = 'You must specify a title for this session'


    return render_to_response('new_session.html', data, context_instance=RequestContext(request))

@login_required
@tutor_course_is_selected
def edit_session(request, session_id):
    data = {}

    # If the form has been submitted, work out what action should be taken and do it
    if request.method == 'POST':
        question_id = request.POST['question-id']
        if 'delete' in request.POST:
            try:
                s = Session.objects.get(id=session_id, course=request.session['course_id'])
                q = Question.objects.get(pk=question_id, session=s.id)
                q.delete()
            except ObjectDoesNotExist:
                pass # If the question doesn't exist, we don't need to really do anything


    # Get the session and all questions in it
    try:
        data['session'] = Session.objects.get(id=session_id, course=request.session['course_id'])
    except ObjectDoesNotExist:
        data['error'] = 'The session specified could not be found'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

    data['questions'] = Question.objects.filter(session=session_id)

    return render_to_response('edit_session.html', data, context_instance=RequestContext(request))

@login_required
@tutor_course_is_selected
def edit_question(request, session_id, question_id):
    data = {'type': 'edit'}

    # Check we are allowed to actually access this session
    if not Session.objects.filter(id=session_id, course=request.session['course_id']):
        data['error'] = 'The session specified could not be found'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

    if request.method == 'POST':
        question = request.POST.get('question')
        max_options = request.POST.get('max-options')

        # Question must have a body set and the current course must contain the session
        if question and max_options:
            # We can now add the question to the database
            q = Question.objects.get(pk=question_id)
            q.question_body = question
            q.save()

            # Delete all current question options
            Question_option.objects.filter(question_id=question_id).delete()
            for x in range(0,int(max_options)):
                # Is there an option set at this index?
                option_body = request.POST.get('option-body[{0}]'.format(x))
                option_correct = bool(request.POST.get('option-correct[{0}]'.format(x)))
                if option_body:
                    o = Question_option()
                    o.question_id = question_id
                    o.body = option_body
                    o.correct = option_correct
                    o.save()

            return HttpResponseRedirect('/tutor/sessions/{0}/'.format(session_id))
        else:
            if not max_options:
                data['error'] = '"max-options" option was missing from your request'
            else:
                data['error'] = 'Your question must have a body'

    # Get the question and check the session to be sure the tutor owns the question
    try:
        q = Question.objects.get(pk=question_id)
        s = Session.objects.get(pk=q.session.pk, course=request.session['course_id'])
    except ObjectDoesNotExist:
        data['error'] = 'The question specified could not be found'
        return render_to_response('error.html', data, context_instance=RequestContext(request))
    data['question'] = q
    data['question_options'] = Question_option.objects.filter(question=q)

    return render_to_response('question_form.html', data, context_instance=RequestContext(request))

@login_required
@tutor_course_is_selected
def new_question(request, session_id):
    data = {'type': 'new'}

    # Check we are allowed to actually access this session
    if not Session.objects.filter(id=session_id, course=request.session['course_id']):
        data['error'] = 'The session specified could not be found'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

    if request.method == 'POST':
        question = request.POST.get('question')
        max_options = request.POST.get('max-options')

        # Question must have a body set and the current course must contain the session
        if question and max_options:
            # We can now add the question to the database
            q = Question()
            q.session_id = session_id
            q.question_body = question
            q.save()

            for x in range(0,int(max_options)):
                # Is there an option set at this index?
                option_body = request.POST.get('option-body[{0}]'.format(x))
                option_correct = bool(request.POST.get('option-correct[{0}]'.format(x)))
                if option_body:
                    o = Question_option()
                    o.question_id = q.pk
                    o.body = option_body
                    o.correct = option_correct
                    o.save()

            return HttpResponseRedirect('/tutor/sessions/{0}/'.format(session_id))
        else:
            if not max_options:
                data['error'] = '"max-options" option was missing from your request'
            else:
                data['error'] = 'Your question must have a body'


    return render_to_response('question_form.html', data, context_instance=RequestContext(request))

@login_required
@tutor_course_is_selected
def run_session(request, session_id):
    data = {}

    # If the session is already running, just get it.  If it is not currently running,
    # we will then stop all sessions in the selected course then mark this session
    # as running and generate a URL for it.
    try:
        s = Session.objects.get(pk=session_id, course=request.session['course_id'])
    except ObjectDoesNotExist:
        data['error'] = 'The session specified could not be found'
        return render_to_response('error.html', data, context_instance=RequestContext(request))
    
    data['questions'] = Question.objects.filter(session=s)
    if not len(data['questions']):
        data['error'] = 'You cannot launch a session that does not contain any questions'
        return render_to_response('error.html', data, context_instance=RequestContext(request))

    resume = request.GET.get('resume')

    # Only create a new session if we are not resuming or the session is inactive
    if not resume or not s.running:
        Session.objects.filter(course=request.session['course_id']).exclude(pk=session_id).update(running=False)
        s.running = True
        s.url_code = generate_session_url_code()
        s.save()

        # Insert session run
        run = Session_run()
        run.session = s
        run.save()
    else:
        run = Session_run.objects.order_by('-start_time')[0]


    data['session'] = s
    data['session_run'] = run
    data['response_url'] = build_url(request, s.url_code)


    return render_to_response('running_session.html', data, context_instance=RequestContext(request))

@csrf_exempt
@login_required
@tutor_course_is_selected
def api_start_question(request):
    time_offset = 5; # This could possibly be moved into the database to allow the user to configure it

    data = {}

    # If this isn't a POST request, fail
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'error': 'Request to API methods must be POST'}), content_type='application/json')

    session_id = request.POST.get('sessionId')
    question_id = request.POST.get('questionId')
    run_time = request.POST.get('runTime')

    # Check that the currently selected course owns this session and that the question
    # is part of the session
    if (Session.objects.filter(course_id=request.session['course_id'], pk=session_id) and
        Question.objects.filter(session_id=session_id, pk=question_id)):
        # Delete any existing question assignments for this session and insert our new one
        # the return the timing data
        Current_question.objects.filter(session_id=session_id).delete()
        cq = Current_question()
        cq.session_id = session_id
        cq.question_id = question_id
        cq.run_time = run_time
        cq.start_time = timezone.now() + datetime.timedelta(0,time_offset) # 5 seconds from now
        cq.save()

        # Remove any responses stored against this question in the current session run
        session_run = Session_run.objects.filter(session=session_id).order_by('-start_time')[0]
        Student_response.objects.filter(option__question_id=question_id, session_run=session_run).delete()

        data['time_offset'] = time_offset
        data['start_time'] = str(cq.start_time)
        data['run_time'] = int(run_time)
    else:
        data['error'] = 'Session and/or question could not be found'

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@csrf_exempt
@tutor_course_is_selected
def api_get_question_totals(request):
    # If this isn't a POST request, fail
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'error': 'Request to API methods must be POST'}), content_type='application/json')

    question_id = request.POST.get('questionId')
    session_run_id = request.POST.get('sessionRunId')

    # Check user is allowed to access this session_run
    try:
        session_run = Session_run.objects.get(pk=session_run_id, session__course=request.session['course_id'])
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'error': 'You do not have permission to access this session run'}), content_type='application/json')

    data = {}
    s = Statistics()
    data['question_totals'] = s.get_question_totals(question_id, session_run_id)

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@csrf_exempt
@tutor_course_is_selected
def api_get_number_responding_students(request):
    # If this isn't a POST request, fail
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'error': 'Request to API methods must be POST'}), content_type='application/json')

    session_id = request.POST.get('sessionId')

    must_have_pinged_after = timezone.now() - datetime.timedelta(0,5) # 5 seconds ago
    students = Responding_student.objects.filter(session=session_id, last_seen__gt=must_have_pinged_after, session__course=request.session['course_id'])

    data = {
        'num_students': len(students)
    }

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@csrf_exempt
@tutor_course_is_selected
def api_get_number_responses(request):
    # If this isn't a POST request, fail
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'error': 'Request to API methods must be POST'}), content_type='application/json')

    session_id = request.POST.get('sessionId')
    question_id = request.POST.get('questionId')

    session_run = Session_run.objects.filter(session=session_id).order_by('-start_time')[0]
    responses = Student_response.objects.filter(session_run=session_run, option__question=question_id)

    data = {
        'num_responses': len(responses)
    }

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@tutor_course_is_selected
def reports_home(request):
    sessions = Session.objects.filter(course=request.session['course_id'])

    data = {
        'sessions': sessions
    }

    return render_to_response('reports_home.html', data, context_instance=RequestContext(request))

@login_required
@csrf_exempt
@tutor_course_is_selected
def api_report_get_session_runs(request):
    # If this isn't a POST request, fail
    if not request.method == 'POST':
        return HttpResponse(json.dumps({'error': 'Request to API methods must be POST'}), content_type='application/json')

    session_id = request.POST.get('sessionId')

    session_runs = Session_run.objects.filter(session=session_id, session__course=request.session['course_id']).order_by('start_time')

    session_runs_clean = []
    for session_run in session_runs:
        session_run_clean = {
            'id': session_run.pk,
            'start_time': session_run.start_time.strftime("%A, %d. %B %Y %I:%M%p")
        }
        session_runs_clean.append(session_run_clean)

    data = {
        'session_runs': session_runs_clean
    }

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
@tutor_course_is_selected
def session_run_report(request):
    session_run_id = request.GET.get('session_run')

    data = {}

    try:
        data['session_run'] = Session_run.objects.get(pk=session_run_id, session__course=request.session['course_id'])
    except ObjectDoesNotExist:
        raise Http404

    # This is the data that we process to make the leaderboard
    question_responses = Student_response.objects.filter(session_run=session_run_id)

    # Get the leaderboard for question response quantity
    question_response_quantities = {}
    for response in question_responses:
        question_body = response.option.question.question_body
        if not question_body in question_response_quantities:
            question_response_quantities[question_body] = 0

        question_response_quantities[question_body] += 1

    data['question_response_quantities'] = []
    # We must now loop through the dictionary in order and convert it to an ordered list
    position = 1
    for question in sorted(question_response_quantities, key=question_response_quantities.get, reverse=True):
        question_entry = {
            'position': position,
            'body': question,
            'num_responses': question_response_quantities[question]
        }
        data['question_response_quantities'].append(question_entry)
        position += 1

    # Get the leaderboard for question accuracy

    # First pass through the responses and count the number of correct/incorrect for each question
    question_response_counts = {}
    for response in question_responses:
        question_body = response.option.question.question_body
        if not question_body in question_response_counts:
            question_response_counts[question_body] = {'correct': 0, 'incorrect': 0}

        if response.option.correct:
            question_response_counts[question_body]['correct'] += 1
        else:
            question_response_counts[question_body]['incorrect'] += 1

    # Now pass through the list again and generate the percentage correct for each question
    question_response_percentages = {}
    for question in question_response_counts:
        question_counts = question_response_counts[question]
        percentage_correct = (question_counts['correct'] / (question_counts['correct'] + question_counts['incorrect'])) * 100

        question_response_percentages[question] = percentage_correct

    data['question_response_percentages'] = []
    # We must now loop through the dictionary in order and convert it to an ordered list
    position = 1
    for question in sorted(question_response_percentages, key=question_response_percentages.get, reverse=True):
        question_entry = {
            'position': position,
            'body': question,
            'percentage_correct': question_response_percentages[question]
        }
        data['question_response_percentages'].append(question_entry)
        position += 1

    return render_to_response('session_run_report.html', data, context_instance=RequestContext(request))
import time
import json
import random

from django.test import TestCase, Client
from main.models import Session, Session_run

class TestRunningSesson(TestCase):
    fixtures = ['basic_setup.json']
    
    def setUp(self):
        # Create our client, login and select a course
        self.client = Client()
        self.client.post('/login/', {'username': 'tutor1', 'password': '1234'})
        self.client.post('/tutor/select_course/', {'course': 1}, follow=True)

    # Get a session, start it and then check that it changes to active and that
    # the URL code changes
    def test_start_new_session(self):
        s_old = Session.objects.get(pk=1)
        s_old.running = False;
        s_old.save()

        response = self.client.get('/tutor/sessions/run/1/')

        s_new = Session.objects.get(pk=1)
        self.assertEqual(s_new.running, True)
        self.assertNotEqual(s_new.url_code, s_old.url_code)

    # Get a session, resume it and check that the url_code has not changed
    def test_resume_existing_session(self):
        s_old = Session.objects.get(pk=1)

        response = self.client.get('/tutor/sessions/run/1/?resume=true')

        s_new = Session.objects.get(pk=1)
        self.assertEqual(s_new.url_code, s_old.url_code)

    # Massive test - Start a question, send some random responses to it and
    # check that they were all recorded correctly
    def test_full_question_run(self):
        # First we make the server call to start the question running for 10 seconds
        self.client.post('/tutor/sessions/api/start_question/', {
            'questionId': 1,
            'sessionId': 1,
            'runTime': 10
        })

        # Get the URL code for sending response requests to
        s = Session.objects.get(pk=1)

        # Get the question data
        response = self.client.get('/student/check_question_availability/', {
            'session_code': s.url_code,
            # Dummy UUID used to satisfy constraints
            'responder_uuid': 'de305d54-75b4-431b-adb2-eb6b9e546013'
        })

        question_data = json.loads(response.content.decode('utf-8'))

        # Build a dictionary to record how many times each option is sent to
        # the server, this will be used later for verification
        option_counts = {}
        for option in question_data['question_options']:
            option_counts[option['id']] = 0

        # Sleep until the question is due to start
        time.sleep(question_data['time_to_start']/1000)
        
        num_options = len(option_counts.keys())

        # Answer with random responses in a loop
        for x in range(1,1000):
            # Pick a random option to respond with
            option_ids = list(option_counts.keys())
            option_id = option_ids[random.randint(0, num_options-1)]

            # Record which option was picked in the option_counts dictionary
            option_counts[option_id] += 1

            # Respond to the question
            self.client.post('/student/log_response/', {
                'optionId': option_id,
                'sessionCode': s.url_code
            })

        # Find the most recent session run
        sr = Session_run.objects.filter(session=1).order_by('-start_time')[0]

        # Get the recorded results for the question
        response = self.client.post('/tutor/sessions/api/get_question_totals/', {
            'questionId': 1,
            'sessionRunId': sr.pk
        })

        # Now decode the response and check that the totals returned from the server
        # match up with the data that was sent
        response_question_totals = json.loads(response.content.decode('utf-8'))['question_totals']

        # Check each option in turn and check that the number of returned responses
        # matches the number of responses set
        for option_id in response_question_totals:
            response_count = response_question_totals[option_id]['count']
            sent_count = option_counts[int(option_id)]
            self.assertEqual(response_count, sent_count)
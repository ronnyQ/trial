import uuid
import random

from django.test import TestCase, Client
from main.models import Question_option

class TestSesson(TestCase):
    fixtures = ['basic_setup.json']
    
    def setUp(self):
        # Create our client, login and select a course
        self.client = Client()
        self.client.post('/login/', {'username': 'tutor1', 'password': '1234'})
        self.client.post('/tutor/select_course/', {'course': 1}, follow=True)

    # If no name is specified, an error should be displayed
    def test_session_create_missing_name(self):
        response = self.client.post('/tutor/sessions/new/', {'session-title': ''})
        self.assertContains(response, 'You must specify a title for this session')

    # Add a session and then check it appears in the list of sessions
    def test_session_create(self):
        session_name = uuid.uuid4() # Get a random session name
        response = self.client.post('/tutor/sessions/new/', {'session-title': session_name}, follow=True)
        self.assertContains(response, session_name)

    # Attempt to add a question with no body to this session
    def test_session_add_question_no_name(self):
        response = self.client.post('/tutor/sessions/2/questions/add/', {'question': '', 'max-options': 0})
        self.assertContains(response, 'Your question must have a body')

    # Add a random question and ensure it is recalled properly
    def test_session_add_question(self):
        question_data = {}

        # Give the question a random name
        question_data['question'] = uuid.uuid4()
        question_data['max-options'] = 10

        # Loop and add 10 options to the question
        for i in range(1,question_data['max-options']):
            question_data['option-body[{0}]'.format(i)] = uuid.uuid4()
            # Only set option correct if a random variable is true, this similates checkboxes
            if (random.getrandbits(1)):
                question_data['option-correct[{0}]'.format(i)] = True

        response = self.client.post('/tutor/sessions/2/questions/add/', question_data, follow=True)

        self.assertContains(response, question_data['question'])

        # We know that the name has saved correctly, now check that the options were correctly saved
        for i in range(1,question_data['max-options']):
            # Check if option i exists
            correct = bool('option-correct[{0}]'.format(i) in question_data)
            option_body = question_data['option-body[{0}]'.format(i)]
            self.assertTrue(Question_option.objects.filter(correct=correct, body=option_body).exists())

    # Attempt to add a question where the "max-options" hidden input is missing 
    def test_session_add_question_missing_max_options(self):
        question_data = {
            'question': 'foo',
            'option-body[0]': 'bar'
        }

        response = self.client.post('/tutor/sessions/2/questions/add/', question_data, follow=True)

        self.assertContains(response, '&quot;max-options&quot; option was missing from your request')

    # Attempt to load the edit page for a question in a course that the tutor is not assigned to teach
    def test_session_view_unassigned_question(self):
        response = self.client.get('/tutor/sessions/3/questions/edit/4/')
        self.assertContains(response, 'The session specified could not be found')

    # Attempt to load the edit page for a question that does not exist anywhere in the system
    def test_session_view_non_existant_question(self):
        response = self.client.get('/tutor/sessions/1/questions/edit/999/')
        self.assertContains(response, 'The question specified could not be found')

    # Attempt to load the edit page for a session in a course that the tutor is not assigned to teach
    def test_session_view_unassigned_session(self):
        response = self.client.get('/tutor/sessions/3/questions/edit/4/')
        self.assertContains(response, 'The session specified could not be found')
from django.test import TestCase, Client

class TestCourseSelection(TestCase):
    fixtures = ['basic_setup.json']
    
    def makeNewClient(self):
        # Remove any existing clients, make a new one and then login
        self.client = None
        self.client = Client()
        self.client.post('/login/', {'username': 'tutor1', 'password': '1234'})

    # "Select a course" message should be displayed on the tutor page
    def test_no_course_selected(self):
        self.makeNewClient()
        response = self.client.get('/tutor/')
        
        self.assertContains(response, 'you must select a course')

    # "Select a course" message should be displayed again after attempting to
    # select a course that does not exist
    def test_select_nonexistant_course(self):
        self.makeNewClient()
        response = self.client.post('/tutor/select_course/', {'course': -1}, follow=True)
        
        self.assertContains(response, 'you must select a course')

    # "Select a course" message should be displayed again after attempting to
    # select a course is not assigned to the logged in user
    def test_select_unassigned_course(self):
        self.makeNewClient()
        response = self.client.post('/tutor/select_course/', {'course': 2}, follow=True)
        
        self.assertContains(response, 'you must select a course')

    # "Select a course" message disappear after selecting a course that the tutor is assigned to
    def test_select_assigned_course(self):
        self.makeNewClient()
        response = self.client.post('/tutor/select_course/', {'course': 1}, follow=True)
        
        self.assertNotContains(response, 'you must select a course')

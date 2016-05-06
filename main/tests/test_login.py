from django.test import TestCase, Client

class TestLogin(TestCase):
    fixtures = ['basic_setup.json']
    correct_login = {'username': 'tutor1', 'password': '1234'}

    # If the user is not logged in, they should be redirected to
    # the login page if they try and access the tutor area
    def test_not_logged_in(self):
        c = Client()
        response = c.get('/tutor/')
        self.assertRedirects(response, '/login/?next=/tutor/')

    # If the user logs in with correct details, they will be
    # taken to the tutor area and be able to view it
    def test_correct_login(self):
        c = Client()
        response = c.post('/login/', {
            'username': self.correct_login['username'],
            'password': self.correct_login['password']}, follow=True)
        
        # Use the "tutor.js" include to identify that we have reached
        # the tutor area correctly
        self.assertContains(response, 'tutor.js')

    # If the user logs in with a correct username but incorrect
    # password, the login should be rejected
    def test_incorrect_password(self):
        c = Client()
        response = c.post('/login/', {
            'username': self.correct_login['username'],
            'password': 'incorrect password'}, follow=True)
        
        # Use the login error message to identify if the login failed
        self.assertContains(response, 'No user with that username/password found!')

    # If the user logs in with both an incorrect username and password
    # the login should be rejected
    def test_non_existant_user(self):
        c = Client()
        response = c.post('/login/', {
            'username': 'non existant user',
            'password': 'incorrect password'}, follow=True)
        
        # Use the login error message to identify if the login failed
        self.assertContains(response, 'No user with that username/password found!')

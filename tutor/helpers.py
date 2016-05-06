from main.models import Session
import string
import random

def generate_session_url_code():
    # Generates a random string of characters to be used as the URL for a session
    # If it already exists keep regenerating it until it does not
    length = 5
    generate = True
    while generate:
        code = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

        s = Session.objects.filter(url_code=code)
        if not s:
            generate = False

    return code

def build_url(request, slug):
    protocol = 'https' if request.is_secure() else 'http'

    return "{0}://{1}/{2}/".format(protocol, request.get_host(), slug)

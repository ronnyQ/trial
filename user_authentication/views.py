from django.shortcuts import render, render_to_response
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

def login_form(request):
    data = {}
    data.update(csrf(request))

    # Has the form been submitted?
    if request.method == 'POST':
        data['login_error'] = True, # This will be set to false later if login successful

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                data['login_error'] = False;

                return HttpResponseRedirect('/tutor/')

    return render_to_response('login_form.html', data);

def do_logout(request):
    logout(request)

    return render_to_response('logout_confirmation.html')
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import PollForm

API_BASE = 'http://127.0.0.1:8000/api/v1/polls/'
API_AUTH_SIGNIN = 'http://127.0.0.1:8000/api/v1/auth/signin/'  # Your JWT signin API URL


def get_auth_headers(request):
    token = request.session.get('access_token')
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)
            return redirect("signin")
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {"form": form})


def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Django session login for DRF UI

            # Get JWT tokens from backend API
            resp = requests.post(API_AUTH_SIGNIN, data={
                'username': user.username,
                'password': request.POST['password'],
            })

            if resp.status_code == 200:
                tokens = resp.json()
                # Store tokens in session
                request.session['access_token'] = tokens['access']
                request.session['refresh_token'] = tokens['refresh']
            else:
                # If token fetch fails, optionally logout user or notify
                logout(request)
                form.add_error(None, "Could not get auth token from server.")
                return render(request, 'signin.html', {'form': form})

            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})


def signout(request):
    if request.method == "POST":
        logout(request)  # Session logout
        request.session.pop('access_token', None)
        request.session.pop('refresh_token', None)
    return redirect("home")


def poll_list_view(request):
    response = requests.get(API_BASE)
    polls = response.json().get('results', [])
    return render(request, 'home.html', {'polls': polls})


@login_required(login_url="signin/")
def poll_create_view(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            headers = get_auth_headers(request)
            requests.post(API_BASE, data=form.cleaned_data, headers=headers)
            return redirect('home')
    else:
        form = PollForm()
    return render(request, 'create.html', {'form': form})


def poll_vote_view(request, pk):
    poll_response = requests.get(f'{API_BASE}{pk}/')
    poll = poll_response.json()

    print(poll)

    if request.method == 'POST':
        selected_option = request.POST.get('poll')
        if selected_option in ['option_one', 'option_two', 'option_three']:
            requests.post(f'{API_BASE}vote/{pk}/', data={'option': selected_option})
            return redirect('results', pk=pk)

    return render(request, 'vote.html', {'poll': poll})


def poll_result_view(request, pk):
    response = requests.get(f'{API_BASE}results/{pk}/')
    poll = response.json()
    return render(request, 'results.html', {'poll': poll})


def poll_delete_view(request, pk):
    headers = get_auth_headers(request)
    requests.delete(f'{API_BASE}{pk}/',headers=headers)
    return redirect('home')

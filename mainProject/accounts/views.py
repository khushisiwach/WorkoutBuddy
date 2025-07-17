import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm

FASTAPI_BASE_URL = 'http://localhost:8000'


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'oauth_provider': 'local',
            }
            try:
                response = requests.post(f'{FASTAPI_BASE_URL}/api/register', json=data)
                new_response = response.json()
                if new_response["status"] == 201:
                    messages.success(request, new_response["message"])
                    return redirect('login')
                else:
                    messages.error(request, new_response["message"])
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Request failed: {e}")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            try:
                response = requests.post(f'{FASTAPI_BASE_URL}/api/login', json=data)
                if response.status_code == 200:
                    user_data = response.json()["data"]
                    token = user_data.get("access_token")
                    user_id = user_data.get("user_id")

                    if token and user_id:
                        request.session['token'] = token
                        request.session['user_id'] = user_id
                        messages.success(request, user_data.get("message", "Login successful"))
                        return redirect('profile')
                    else:
                        messages.error(request, 'Invalid token or user ID.')
                else:
                    error_detail = response.json().get('detail', 'Invalid credentials')
                    messages.error(request, f"Login failed: {error_detail}")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Login request failed: {e}")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def google_login_redirect(request):
    return redirect(f'{FASTAPI_BASE_URL}/auth/google/login')


def google_login_callback(request):
    print(request)
    token = request.GET.get('token')
    user_id = request.GET.get('user_id')
    print(f"UserId:-{user_id}")

    if token and user_id:
        request.session['token'] = token
        request.session['user_id'] = user_id
        messages.success(request, "Google login successful!")
        return redirect('profile')
    else:
        messages.error(request, "Google login failed: Missing credentials.")
        return redirect('login')



def view_or_edit_profile(request):
    token = request.session.get('token')
    user_id = request.session.get('user_id')

    if not token or not user_id:
        messages.error(request, 'You must be logged in.')
        return redirect('login')

    headers = {'Authorization': f'Bearer {token}'}

    if request.method == 'GET':
        try:
            response = requests.get(f'{FASTAPI_BASE_URL}/api/user/{user_id}/profile', headers=headers)
            if response.status_code == 200:
                profile_data = response.json().get("data", {})
                form = ProfileForm(initial=profile_data)
                return render(request, 'accounts/profileForm.html', {
                    'form': form,
                    'is_editing': True
                })
            else:
                form = ProfileForm()
                return render(request, 'accounts/profileForm.html', {
                    'form': form,
                    'is_editing': False
                })
        except requests.exceptions.RequestException as e:
            messages.error(request, "The server is currently unavailable. Please try again later.")
            return render(request, 'accounts/profileForm.html', {
                'form': ProfileForm(),
                'is_editing': False
            })

    elif request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["user_id"] = user_id

            try:
                # Check profile existence
                exists_check = requests.get(f'{FASTAPI_BASE_URL}/api/user/{user_id}/profile', headers=headers)
                if exists_check.status_code == 200:
                    response = requests.put(f'{FASTAPI_BASE_URL}/api/user/{user_id}/profile', json=data, headers=headers)
                else:
                    response = requests.post(f'{FASTAPI_BASE_URL}/api/user/{user_id}/profile', json=data, headers=headers)

                if response.status_code in [200, 201]:
                    messages.success(request, 'Profile saved successfully.')
                    updated = requests.get(f'{FASTAPI_BASE_URL}/api/user/{user_id}/profile', headers=headers)
                    if updated.status_code == 200:
                        profile_data = updated.json().get("data", {})
                        return render(request, 'accounts/viewProfile.html', {
                            'profile': profile_data
                        })
                    else:
                        messages.error(request, "Failed to load saved profile.")
                        return redirect('profile')
                else:
                    error_detail = response.json().get('detail', response.text)
                    messages.error(request, f"Profile save failed: {error_detail}")
                    return render(request, 'accounts/profileForm.html', {
                        'form': form,
                        'is_editing': True
                    })
            except requests.exceptions.RequestException as e:
                messages.error(request, "The server is currently unavailable. Please try again later.")
                return render(request, 'accounts/profileForm.html', {
                    'form': form,
                    'is_editing': True
                })
        else:
            messages.error(request, "Form validation failed.")
            return render(request, 'accounts/profileForm.html', {
                'form': form,
                'is_editing': True
            })

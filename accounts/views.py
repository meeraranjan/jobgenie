from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile
from recruiters.models import Recruiter
# Create your views here.
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    next_url = request.GET.get('next') or request.POST.get('next') or 'home.index'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            # Redirect to login page instead of auto-login
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
            {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    template_data['next'] = request.GET.get('next', '')
    if request.method == 'GET':
        return render(request, 'accounts/login.html',{'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
        request,
        username = request.POST['username'],
        password = request.POST['password']
        )
        next_url = request.POST.get('next') or 'home.index'
        if user is None: 
            template_data['error'] ='The username or password is incorrect.'
            return render(request, 'accounts/login.html',{'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect(next_url)
        
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import recruiter_required
# # Create your views here.

from .forms import JobSeekerProfileForm
from .models import JobSeekerProfile


@login_required
def create_profile(request):
    if hasattr(request.user, "jobseekerprofile"):
        return redirect("profiles.view_profile")  # already exists

    if request.method == "POST":
        form = JobSeekerProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("profiles:view_profile")
    else:
        form = JobSeekerProfileForm()
    return render(request, "profiles/create_profile.html", {"form": form})

@login_required
def view_profile(request):
    try:
        profile = request.user.jobseekerprofile
    except JobSeekerProfile.DoesNotExist:
        profile = None

    return render(request, "profiles/view_profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    profile = request.user.jobseekerprofile
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles:view_profile')
    else:
        form = JobSeekerProfileForm(instance=profile)
    return render(request, 'profiles/edit_profile.html', {'form': form})

@recruiter_required
def jobseeker_list(request):
    profiles = JobSeekerProfile.objects.filter(is_public=True)
    return render(request, 'profiles/jobseeker_list.html', {'profiles': profiles})

@recruiter_required
def jobseeker_detail(request, pk):
    profile = get_object_or_404(JobSeekerProfile, pk=pk, is_public=True)
    return render(request, 'profiles/jobseeker_detail.html', {'profile': profile})

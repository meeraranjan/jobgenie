from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from profiles.models import UserProfile, JobSeekerProfile
from recruiters.models import Recruiter

from .models import Conversation, Message
from .forms import MessageForm

User = get_user_model()


def _get_display_name(user, viewer=None):
	try:
		seeker = user.jobseekerprofile
		if seeker and seeker.is_public:
			if seeker.first_name or seeker.last_name:
				return f"{(seeker.first_name or '').strip()} {(seeker.last_name or '').strip()}".strip()
	except Exception:
		pass

	try:
		recruiter = user.recruiter_profile
		if recruiter and recruiter.is_public:
			name = "".join([recruiter.first_name or "", " ", recruiter.last_name or ""]).strip()
			if name:
				return name
			if recruiter.company_name:
				return recruiter.company_name
	except Exception:
		pass

	#fallback to username
	return user.username


@login_required
def messaging_home(request):
	"""Messaging tab: list of conversations for the logged-in user."""
	conversations = (
		Conversation.objects.filter(participants=request.user)
		.prefetch_related('participants', 'messages')
		.order_by('-updated_at')
	)

	items = []
	for conv in conversations:
		other = conv.participants.exclude(pk=request.user.pk).first()
		other_display = _get_display_name(other, request.user) if other else ''
		last = conv.messages.order_by('created_at').last()
		unread = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
		items.append({
			'conversation': conv,
			'other': other,
			'other_display': other_display,
			'show_username': bool(other and other_display and other.username and other_display != other.username),
			'last': last,
			'unread': unread,
		})

	context = {
		'items': items,
	}
	return render(request, 'messaging/inbox.html', context)


def _get_existing_conversation(user1, user2):
	"""Return existing conversation between two users or None."""
	return (
		Conversation.objects.filter(participants=user1)
		.filter(participants=user2)
		.distinct()
		.first()
	)


@login_required
@login_required
def select_user_to_message(request):
    """List only PUBLIC recruiters + PUBLIC job seekers (except current user)."""

    users = User.objects.exclude(pk=request.user.pk)
    user_list = []

    for user in users:

        # determine role (if exists)
        try:
            profile = user.userprofile
            role = profile.get_role_display()
        except UserProfile.DoesNotExist:
            continue   # skip if no role profile

        # ------------ FILTER PRIVACY ------------
        # If Job Seeker → require is_public=True
        if profile.role == "JOB_SEEKER":
            try:
                seeker = user.jobseekerprofile
                if not seeker.is_public:
                    continue  # skip private job seeker
            except JobSeekerProfile.DoesNotExist:
                continue

        # If Recruiter → require is_public=True
        if profile.role == "RECRUITER":
            try:
                recruiter = user.recruiter_profile
                if not recruiter.is_public:
                    continue  # skip private recruiter
            except Recruiter.DoesNotExist:
                continue
        # -----------------------------------------

        # ------------ DISPLAY NAME ------------
        # Job Seeker
        display_name = None
        if profile.role == "JOB_SEEKER":
            seeker = user.jobseekerprofile
            full = f"{seeker.first_name or ''} {seeker.last_name or ''}".strip()
            display_name = full if full else user.username

        # Recruiter
        elif profile.role == "RECRUITER":
            recruiter = user.recruiter_profile
            full = f"{recruiter.first_name or ''} {recruiter.last_name or ''}".strip()
            display_name = full if full else user.username
        # -----------------------------------------

        # Company (only for recruiters)
        company = None
        if profile.role == "RECRUITER":
            company = recruiter.company_name

        user_list.append({
            "user": user,
            "role": role,
            "company": company,
            "display_name": display_name,
        })

    return render(request, "messaging/select_user.html", {"user_list": user_list})


@login_required
def start_conversation(request, username):
    """Start or return an existing conversation between request.user and username."""
    other = get_object_or_404(User, username=username)
    if other == request.user:
        return redirect('messaging:messaging_home')

    conversation = _get_existing_conversation(request.user, other)
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other)

    return redirect('messaging:conversation_detail', pk=conversation.pk)
@login_required
def conversation_detail(request, pk):
	conversation = get_object_or_404(Conversation, pk=pk)


	if not conversation.participants.filter(pk=request.user.pk).exists():
		return redirect('messaging:messaging_home')



	Message.objects.filter(conversation=conversation, is_read=False).exclude(sender=request.user).update(is_read=True)

	if request.method == 'POST':
		form = MessageForm(request.POST)
		if form.is_valid():
			msg = form.save(commit=False)
			msg.conversation = conversation
			msg.sender = request.user
			msg.save()
			conversation.save()
			return redirect('messaging:conversation_detail', pk=conversation.pk)
	else:
		form = MessageForm()
	raw_messages = conversation.messages.select_related('sender').order_by('created_at')
    
	messages_data = []
	for msg in raw_messages:
		sender_user = msg.sender
		sender_display = _get_display_name(sender_user, request.user)
		messages_data.append({
			'id': msg.id,
			'sender': sender_user.username,
			'sender_display': sender_display,
			'body': msg.body,
			'created_at': msg.created_at,
			'is_read': msg.is_read,
		})
	
	other = conversation.participants.exclude(pk=request.user.pk).first()

	other_display = _get_display_name(other, request.user) if other else ''

	if request.GET.get('format') == 'json':
		return JsonResponse({
			'messages': [
				{
					'id': msg['id'],
					'sender': msg['sender'],
					'sender_display': msg.get('sender_display') or msg['sender'],
					'body': msg['body'],
					'created_at': msg['created_at'].isoformat(),
					'is_read': msg['is_read'],
				}
				for msg in messages_data
			]
		})

	context = {
		'conversation': conversation,
		'form': form,
		'other': other,
		'other_display': other_display,
	}
	return render(request, 'messaging/conversation_detail.html', context)

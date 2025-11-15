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
		last = conv.messages.order_by('created_at').last()
		unread = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
		items.append({
			'conversation': conv,
			'other': other,
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
def select_user_to_message(request):
    """List all users (except current) to start a conversation with."""
    users = User.objects.exclude(pk=request.user.pk)
    
    user_list = []
    for user in users:
        try:
            profile = user.userprofile
            role = profile.get_role_display()
        except UserProfile.DoesNotExist:
            profile = None
            role = 'Unknown'
        
		# skip privates
        try:
            seeker_profile = user.jobseekerprofile
            if not seeker_profile.is_public:
                continue
        except JobSeekerProfile.DoesNotExist:
            pass
        
        # skip self
        if user == request.user:
            continue
        
        company = None
        if profile and profile.role == 'RECRUITER':
            try:
                recruiter = user.recruiter_profile
                company = recruiter.company_name
            except Recruiter.DoesNotExist:
                company = None
        
        user_list.append({
            'user': user,
            'role': role,
            'company': company,
        })
    
    context = {'user_list': user_list}
    return render(request, 'messaging/select_user.html', context)


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

	raw_messages = conversation.messages.select_related('sender').values(
		'id', 'body', 'created_at', 'is_read', 'sender__username'
	).order_by('created_at')
	
	messages_data = []
	for msg in raw_messages:
		messages_data.append({
			'id': msg['id'],
			'sender': msg['sender__username'],
			'body': msg['body'],
			'created_at': msg['created_at'],
			'is_read': msg['is_read'],
		})
	
	other = conversation.participants.exclude(pk=request.user.pk).first()

	if request.GET.get('format') == 'json':
		return JsonResponse({
			'messages': [
				{
					'id': msg['id'],
					'sender': msg['sender'],
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
	}
	return render(request, 'messaging/conversation_detail.html', context)

from django.db import models
from django.conf import settings


class Conversation(models.Model):
	"""A conversation between two users (participants)."""
	participants = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		related_name='conversations'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-updated_at']

	# def __str__(self):
	# 	users = list(self.participants.all()[:2])
	# 	if len(users) == 2:
	# 		return f"Conversation: {users[0].username} <-> {users[1].username}"
	# 	return f"Conversation {self.pk}"

	def other_party(self, user):
		"""Return the other participant in the conversation for a given user."""
		return self.participants.exclude(pk=user.pk).first()


class Message(models.Model):
	conversation = models.ForeignKey(
		Conversation,
		on_delete=models.CASCADE,
		related_name='messages'
	)
	sender = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='sent_messages'
	)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	class Meta:
		ordering = ['created_at']

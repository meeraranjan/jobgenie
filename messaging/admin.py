from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ('id', 'created_at', 'updated_at')
	filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('id', 'sender', 'created_at', 'is_read')
	list_filter = ('is_read', 'created_at')
	search_fields = ('sender__username', 'body')

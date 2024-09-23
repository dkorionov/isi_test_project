from django.db import models
from django.contrib.auth.models import User


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_threads')

    def __str__(self):
        return f"Thread - {self.id}"

    class Meta:
        verbose_name = 'Thread'
        verbose_name_plural = 'Threads'


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message - {self.id} - {self.sender} - {self.thread}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'


class UserUnreadMessages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unread_messages')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='user_unread_messages')
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Unread messages for {self.user}"
from django.db import models
from django.contrib.auth.models import User
from schools.models import School

class Conversation(models.Model):
    """A chat thread between participants in a school context"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ", ".join([u.username for u in self.participants.all()])
        return f"Conversation in {self.school.name} between {participant_names}"

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_other_participant(self, user):
        """Returns the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    """Individual chat message"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender.username} at {self.created_at}"

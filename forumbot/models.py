from django.db import models
from accounts.models import User

# Create your models here.

class Room(models.Model):
	#Host, topic, participants  == foreign keys
	host = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	description = models.CharField(max_length=400, null=True, blank=True)
	participants = models.ManyToManyField(User, related_name='participants', blank=True)
	topics = models.ForeignKey('Topic', on_delete=models.SET_NULL, blank=True, null=True)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)

	class Meta:
		ordering = ['-updated','-created']

	def __str__(self):
		return self.name


class Message(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	content = models.CharField(max_length=500)
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	created = models.DateTimeField(auto_now=False, auto_now_add=True)

	def __str__(self):
		return self.content[:50]

	class Meta:
		ordering = ['-updated','-created']

class Topic(models.Model):
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name
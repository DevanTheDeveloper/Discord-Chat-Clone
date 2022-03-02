from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from accounts.models import User
from .models import Room,Message

class LoginForm(ModelForm):
	class Meta:
		model = User 
		fields = ['email','password']


class UserCreationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['name','username','email','password1','password2']

class RoomForm(ModelForm):
	class Meta:
		model = Room
		fields = ['name','description','topics']


class RoomCommentForm(ModelForm):
	class Meta:
		model = Message
		fields = ['content']


class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['username','name', 'email','avatar','bio']
from django.shortcuts import render,HttpResponseRedirect,redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, Http404

from accounts.models import User

from . models import Room, Topic, Message
from .forms import RoomForm, RoomCommentForm, UserForm, UserCreationForm, LoginForm


# Create your views here.
def activityPage(request):
	q = request.GET.get('q') if request.GET.get('q') != None else ''
	recentActivity = Message.objects.filter(Q(room__topics__name__icontains=q))
	context = {'recentActivity':recentActivity}
	return render(request, 'site/mobile_activity.html',context )



def topicsPage(request):
	q = request.GET.get('q') if request.GET.get('q') != None else ''
	topics = Topic.objects.filter(name__icontains=q)
	context = {'topics':topics}
	return render(request, 'site/mobile_topics.html',context )

@login_required(login_url='login')
def updateUser(request):
	
	
	if request.method == "GET":
		form = UserForm(instance=request.user)
		context = {'form':form}
		return render(request,'site/update_user.html',context)

	elif request.method == "POST":

		form = UserForm(request.POST,request.FILES, instance = request.user)
		if form.is_valid():
			form.save()
			messages.success(request, 'Profile Updated!')
		else:
			print(form.errors)
			messages.error(request, 'Something went wrong! Please try again later.')
		return redirect('userProfile', pk=request.user.id)
 






def userProfile(request,pk):
	
	q = request.GET.get('q') if request.GET.get('q') != None else '' 
	user = get_object_or_404(User, id=pk)
	userRooms = user.room_set.all()
	userMessages = user.message_set.all()
	topics = Topic.objects.all()
	recentActivity = Message.objects.filter(Q(room__topics__name__icontains=q))

	context = {	'user':user,
				'rooms':userRooms,
				'room_messages':userMessages,
				'topics':topics,
				'recentActivity':recentActivity,

	}


	return render(request, 'site/profile.html', context)


def registerPage(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.username = user.username.lower()
			user.save()
			login(request,user)
			return redirect('index')
		else:
			messages.error(request,'There was an error!')
			return render(request, 'site/login_register.html',context)

	
	page = 'register'
	context = {'page':page, 'form':UserCreationForm()}
	return render(request, 'site/login_register.html',context)

def logoutPage(request):
	if request.method == "GET":
		logout(request)
		return redirect('index')

def loginPage(request):
	page = 'login'

	form = LoginForm()

	if request.method == "POST":
		email = request.POST.get('email').lower()
		#username = request.POST.get('username').lower()
		password = request.POST.get('password')

		try:
			user = User.objects.get(email=email)
		except:
			messages.error(request, "User doesn't exist!")
			return render(request, 'site/login_register.html')

		user = authenticate(request, email=email, password=password)

		if user is not None:
			login(request, user)
			return redirect('index')
		else:
			messages.error(request,'Incorrect Password')

	if request.user.is_authenticated:
		return redirect('index')

	context = {'page':page, 'form':form}

	return render(request, 'site/login_register.html', context)


@login_required(login_url='login')
def deleteRoom(request,pk):
	room = Room.objects.get(id=pk) 
	context = {'obj':room.name}
	
	if request.method == "POST":
		room.delete()
		return redirect('index')
	else:
		return render(request, 'site/delete.html',context)



@login_required(login_url='login')
def updateRoom(request,pk):

	topics = Topic.objects.all()
	room = Room.objects.get(id=pk) 
	form = RoomForm(instance=room)
	action = 'Update'


	if request.user != room.host:
		return HttpResponse('Your Not Allowed In Here!!!')


	if request.method == "POST" and request.user.is_authenticated:
		topic_name = request.POST.get('topics')
		topic, created = Topic.objects.get_or_create(name=topic_name)
		room.name = request.POST.get('name')
		room.description = request.POST.get('description')
		room.topics = topic
		room.save()		
		return HttpResponseRedirect(reverse('room', args=[pk]))



	else:
		
		context = {'form':form,'topics':topics,'room':room,'action':action}
		return render(request, 'site/room_form.html', context)


@login_required(login_url='login')
def createRoom(request):
	
	action = 'Create'
	topics = Topic.objects.all()

	context = {
				'form':RoomForm(),
				'topics':topics,
				'action':action
	}

	if request.method == "POST":
		topic_name = request.POST.get('topics')
		topic, created = Topic.objects.get_or_create(name=topic_name)
		
		newRoom = Room.objects.create(
			host = request.user,
			name = request.POST.get('name'),
			description = request.POST.get('description'),
			topics = topic, 
			)
		newRoom.participants.add(request.user)
		newRoom.save()
		#form = RoomForm(request.POST)
		#if form.is_valid():
		#	newRoom = form.save(commit=False)
		#	newRoom.host = request.user
		#	newRoom.save()
		return HttpResponseRedirect(reverse('room',args=[newRoom.id]))
		#else:
		#	print(form.errors)



	else:

		return render(request, 'site/room_form.html',context)

@login_required(login_url='login')
def deleteMessage(request,pk):
	#print(request.META)
	message = Message.objects.get(id=pk) 
	context = {}
	if request.user != message.user:
		raise HttpResponse("This action is not permitted.")

	if request.method == "POST":
		message.delete()
		return redirect('room', pk=message.room.id)

	context['obj'] = message 
	return render(request, 'site/delete.html',context)

def room(request,pk):
	room = Room.objects.get(id=pk)
	comments = room.message_set.all()
	

	if request.method == 'POST' and request.user.is_authenticated:
		form = RoomCommentForm(request.POST)
		if form.is_valid():
			newComment = form.save(commit=False)
			newComment.user = request.user
			newComment.room = room
			newComment.save()
			room.participants.add(request.user)
			room.save()
			comments = room.message_set.all() # already set orderby in model 
			
			context={'room':room,'room_messages':comments }
		else:
			messages.error(request,'Something went wrong when we tried to post your comment!')
			context={'room':room,'room_messages':comments }
		return render(request,'site/room.html',context)

	else:
		 
		context={'room':room,'room_messages':comments }
		return render(request,'site/room.html',context)


	

def index(request):
	if request.method == "GET":
		q = request.GET.get('q') if request.GET.get('q') != None else '' 

		rooms = Room.objects.filter(
			Q(topics__name__icontains=q) |
			Q(name__icontains=q) |
			Q(description__icontains=q)

				).distinct()

		topics = Topic.objects.all()[:10]
		roomCount = rooms.count
		recentActivity = Message.objects.filter(Q(room__topics__name__icontains=q))

		context = {'rooms':rooms,'topics':topics,'roomCount':roomCount,'recentActivity':recentActivity}
		return render(request,'site/index.html',context)





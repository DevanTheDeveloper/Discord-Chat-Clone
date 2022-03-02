from django.urls import path
from . import views


urlpatterns = [
				path('', views.getRoutes, name='getRoutes'),
				path('rooms/', views.allRooms, name='allRooms'),
				path('rooms/<int:pk>', views.getRoom, name='getRoom'),


				]
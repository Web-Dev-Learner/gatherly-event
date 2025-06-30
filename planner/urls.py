from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('event/create/', views.create_event_view, name='create_event'),
    path('event/my/', views.my_events_view, name='my_events'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('profile/', views.profile_view, name='profile'),
   
    path('event/<int:event_id>/rsvp/', views.rsvp_view, name='rsvp'),

    path('event/<int:event_id>/edit/', views.edit_event_view, name='edit_event'),
    path('event/<int:event_id>/delete/', views.delete_event_view, name='delete_event'),

    path('event/call/<int:event_id>/', views.join_video_call, name='join_video'),
   


]

from django.urls import path
from .views import *


urlpatterns = [
    path('polls/',PollAPIView.as_view()),
    path('polls/<int:pk>/',PollIdAPIView.as_view()),
    path('polls/vote/<int:pk>/', VoteAPIView.as_view()),     
    path('polls/results/<int:pk>/', PollResultAPIView.as_view()), 
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signin/', SigninView.as_view(), name='signin'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]
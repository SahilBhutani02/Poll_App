from django.urls import path
from .views import *

urlpatterns = [
    path('', poll_list_view, name='home'),
    path('polls/create/', poll_create_view, name='create'),
    path('polls/vote/<int:pk>/', poll_vote_view, name='vote'),
    path('polls/results/<int:pk>/', poll_result_view, name='results'),
    path('polls/delete/<int:pk>/', poll_delete_view, name='delete'),
    path('signup/',signup,name='signup'),
    path('signin/',signin,name='signin'),
    path('signout/',signout,name='signout'),
]

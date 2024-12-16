from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('questions/', views.questions_view, name='questions'),  # Questions page
    path('login/', views.custom_login_view, name='login'),  # Login page
    path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),  # Poll detail
    path('poll/<int:poll_id>/vote/', views.vote, name='vote'),  # Vote
    path('poll/<int:poll_id>/result/', views.poll_result, name='poll_result'),
    path('homeadmin/', views.homeadmin, name='homeadmin'),
    path('poll/<int:poll_id>/result/', views.poll_result, name='poll_results'),  # Poll results
    path('add_poll/', views.add_poll, name='add_poll'), 
    path('view_polls/', views.view_polls, name='view_polls'),
    path('poll/<int:poll_id>/toggle/', views.toggle_poll_status, name='toggle_poll_status'),
    path('poll/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'), 
    path('polls/results/', views.poll_result, name='poll_results'),
    path('add-user/', views.add_user_and_qr, name='add_user_and_qr'),
    # path('logout/', LogoutView.as_view(next_page='/'), name='logout'),


]

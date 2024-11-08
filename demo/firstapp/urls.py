from django.urls import path
from firstapp import views
        
urlpatterns = [
    
    #  path('', views.register, name='register'),
    path(r'register/', views.register, name='register'),
    path(r'home/', views.home, name='home'),
    path(r'login/', views.Login, name='login'),
    path(r'logout/', views.logout_view, name='logout'),
    
    path(r'about/', views.about, name='about'),
    path(r'courses/', views.courses, name='courses'),
    path(r'contact/', views.contact, name='contact'),
    path(r'exam/', views.exam, name='exam'),
    
    

    # path(r'update-profile/', views.update_profile, name='update_profile'),
  
    
    path(r'profile/', views.profile, name='profile'),
    path(r'playlist/', views.playlist, name='playlist'),
    path(r'update/', views.update_profile, name='update_profile'),
    path(r'watch-video/', views.watchvideo, name='watch-video'),
    path(r'certificate/', views.certificate, name='certiicate'),
    path(r'enroll_course/', views.enrollcourse, name='enroll_course'),
    
    path(r'search_result/', views.search_result, name='search_result'),
    path(r'course_detail/', views.course_detail, name='course_detail'),


]
    
    
    


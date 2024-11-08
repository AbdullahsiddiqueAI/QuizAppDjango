from django.urls import path
from firstapp import views
        
urlpatterns = [
    
     path('', views.index, name='index'),
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
    
     path('course/<int:id>/playlist/', views.course_playlist, name='course_playlist'),
    path(r'update/', views.update_profile, name='update_profile'),
    path(r'watch-video/', views.watchvideo, name='watch-video'),
    path(r'watch-video/<id>', views.watch_video, name='watch_video'),
    path(r'certificate/', views.certificate, name='certiicate'),
    path('enroll_course/', views.enroll_course_without_id, name='enroll_course_no_id'),  # Without ID
    path('enroll_course/<int:id>/', views.enroll_course_with_id, name='enroll_course'),  # With ID
    path('my_courses/', views.my_courses, name='my_courses'),
    path('mark_video_half_watched/<int:lesson_id>/', views.mark_video_half_watched, name='mark_video_half_watched'),

    path(r'search_result/', views.search_result, name='search_result'),
    path(r'course_detail/', views.course_detail, name='course_detail'),
    path('course_detail/<int:id>/', views.course_detail, name='course_detail'),



]
    
    
    


# admin.py

from django.contrib import admin
from .models import CustomUser, Course, Lesson, Quiz, Question, CourseEnrollment, QuizAttempt, Certificate

# Register the CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'city', 'phone_number')
    search_fields = ('email', 'full_name')
    list_filter = ('is_active', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)

# Register the Course model
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'tutor_name', 'date', 'video_count','description')
    search_fields = ('title', 'tutor_name')
    list_filter = ('date',)

admin.site.register(Course, CourseAdmin)

# Register the Lesson model
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'completed', 'video_file', 'thumbnail_image']
    search_fields = ['title']

admin.site.register(Lesson, LessonAdmin)

# Register the Quiz model
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_percentage')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)

admin.site.register(Quiz, QuizAdmin)

# Register the Question model
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_option')
    search_fields = ('text', 'quiz__title')
    list_filter = ('quiz',)

admin.site.register(Question, QuestionAdmin)

# Register the CourseEnrollment model
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'progress')
    search_fields = ('user__email', 'course__title')
    list_filter = ('course',)

admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)

# Register the QuizAttempt model
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'completed_at', 'is_passed')
    search_fields = ('user__email', 'quiz__title')
    # Removed the list_filter entirely

admin.site.register(QuizAttempt, QuizAttemptAdmin)

# Register the Certificate model
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_number', 'issued_at', 'is_verified')
    search_fields = ('user__email', 'course__title', 'certificate_number')
    list_filter = ('course', 'is_verified')

admin.site.register(Certificate, CertificateAdmin)

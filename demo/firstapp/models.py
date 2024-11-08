# models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model  # To get the custom user model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and returns a user with an email, password, and other fields."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and returns a superuser with an email, password, and other fields."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    username = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    city = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Empty list because 'email' is the only required field

    def __str__(self):
        return self.email


# Assuming we are using the CustomUser model you already defined
User = get_user_model()

class Course(models.Model):
    title = models.CharField(max_length=255)
    # title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    tutor_name = models.CharField(max_length=100)
    tutor_image = models.ImageField(upload_to='tutor_images/')
    thumbnail_image = models.ImageField(upload_to='course_thumbnails/')
    video_count = models.PositiveIntegerField()
    date = models.DateField()

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Video upload field (if you want to store video files locally)
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    
    # URL field for external video links (use either URL or FileField, not both)
    # video_url = models.URLField(blank=True, null=True)  # If you want to allow external video links

    # Thumbnail image for the video
    thumbnail_image = models.ImageField(upload_to='lessons/thumbnails/', blank=True, null=True)
    
    # content = models.TextField(blank=True, null=True)  # For text content, e.g., notes, lessons
    order = models.PositiveIntegerField()  # To order lessons
    completed = models.BooleanField(default=False)  # Track if the lesson is completed by user

    def __str__(self):
        return self.title

class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    pass_percentage = models.FloatField(default=50)  # % needed to pass the quiz

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    correct_option = models.IntegerField()  # Store which option is correct (1-4)

    def __str__(self):
        return f"Question: {self.text}"

class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course,related_name="CourseEnrollment", on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField(Lesson, blank=True)
    enrolled_at = models.DateField(auto_now_add=True)
    progress = models.FloatField(default=0.0)

    def update_progress(self):
        total_lessons = self.course.lessons.count()
        completed_count = self.completed_lessons.count()
        if total_lessons > 0:
            self.progress = (completed_count / total_lessons) * 100
        else:
            self.progress = 0
        self.save()

    def save(self, *args, **kwargs):
        if not self.enrolled_at:
            self.enrolled_at = timezone.now().date()  # Explicitly set if needed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()  # Store quiz score as a percentage
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.score}%"

    def is_passed(self):
        return self.score >= self.quiz.pass_percentage

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_number = models.CharField(max_length=255, unique=True)  # Unique certificate number
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return f"Certificate for {self.user.email} - {self.course.title}"

    def generate_certificate_number(self):
        """Generate a unique certificate number, e.g., `COURSE-00123`."""
        return f"{self.course.title[:5].upper()}-{self.id:05}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)

from django.shortcuts import render, redirect,get_object_or_404
from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash 
from django.contrib.auth.hashers import check_password

from django.http import JsonResponse
from .models import *
import json
def index(request):
    # Redirect to 'home' view
    return redirect('home')
@login_required
def home(request):            
    return render(request, 'home.html')


def Login(request):
    if request.method == "POST":
        # Display request data in the console for debugging
        print("Request POST data:", request.POST)
        
        # Get email and password from POST data
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Check if the email field is empty
        if not email:
            messages.error(request, "Email field cannot be empty.")
            return redirect('login')

        # Check if the password field is empty
        if not password:
            messages.error(request, "Password field cannot be empty.")
            return redirect('login')

        # Check if the user is registered
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Account not found. Please register first.")
            return redirect('register')  # Redirect to the registration page if not registered

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            print("User authenticated:", user)
            
            # Log the user in if authentication is successful
            login(request, user)
            messages.success(request, "Login successful. Welcome back, {}!".format(user.full_name or user.email))
            return redirect("home")  # Redirect to the homepage or another page after login
        
        else:
            print("Authentication failed")
            # If authentication fails, display an error message
            messages.error(request, "Invalid email or password. Please try again.")

    # Render the login page with any existing messages
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")  # Get the full name
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        city = request.POST.get("city")
        phone_number = request.POST.get("phone_number")
        profile_image = request.FILES.get("profile_image")

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        # Create the user with the full name
        user = CustomUser.objects.create_user(
            full_name=full_name,  # Save the full name in the user profile
            email=email,
            password=password,
            city=city,
            phone_number=phone_number,
            profile_image=profile_image
        )

        # Log the user in after registration
        login(request, user)
        messages.success(request, "Registration successful.")
        return redirect("home")

    return render(request, "register.html")
@login_required
def courses(request):
    courses = Course.objects.all()  # Fetch all courses from the database
    return render(request, 'courses.html', {'courses': courses})

@login_required
def exam(request):
    return render(request, 'exam.html')

@login_required
def playlist(request):
    return render(request, 'playlist.html')
@login_required
def course_playlist(request, id):
    # Get the course by ID
    selected_course = get_object_or_404(Course, id=id)
    progress=0
    if CourseEnrollment.objects.filter(user=request.user, course=selected_course).first():
        progress=CourseEnrollment.objects.filter(user=request.user, course=selected_course).first().progress
    
    
    # Fetch all lessons associated with the course
    lessons = selected_course.lessons.all().order_by('order')  # Or adjust ordering based on your needs

    # Render the playlist template, passing the course and lessons
    return render(request, 'course_playlist.html', {
        'selected_course': selected_course,
        'lessons': lessons,
        "progress": progress,
    })
 
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def update(request):
    return render(request, 'update.html')

@login_required
def watchvideo(request):
    return render(request, 'watch-video.html')

@login_required
def certificate(request):
    return render(request, 'certificate.html')
@login_required
def watch_video(request, id):
    # Get the specific lesson or return 404 if not found
    lesson = get_object_or_404(Lesson, id=id)

    context = {
        'lesson': lesson,
    }
    return render(request, 'watch-video.html', context)


@login_required
def mark_video_half_watched(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment, created = CourseEnrollment.objects.get_or_create(user=request.user, course=lesson.course)   
        # Mark lesson as completed at 50% if it’s not already marked
        if lesson not in enrollment.completed_lessons.all():
            enrollment.completed_lessons.add(lesson)
            lesson.completed = True
            lesson.save()
            enrollment.update_progress()  # Update course progress
            return JsonResponse({"message": "Lesson marked as 50% watched and progress updated."}, status=200)  
        return JsonResponse({"message": "Lesson already marked as completed."}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=400)


@login_required
def search_result(request):
    return render(request, 'search_result.html')

@login_required
def course_detail(request):
    
    courses = Course.objects.all()

    # Get the courses the user is enrolled in and extract course IDs
    enrolled_courses_ids = CourseEnrollment.objects.filter(user=request.user).values_list('course__id', flat=True)

    context = {
        'courses': courses,
        'enrolled_courses_ids': enrolled_courses_ids,  # List of course IDs the user is enrolled in
    }


    return render(request, 'course_detail.html', context)
    # return render(request, 'course_detail.html')
@login_required
def logout_view(request):
    # Log out the user
    logout(request)
    
    # Add a success message
    messages.success(request, "You have successfully logged out.")
    
    # Redirect to the login page
    return redirect('login')
 
 

@login_required
def update_profile(request):
    user = request.user  # Get the currently logged-in user

    if request.method == "POST":
        # Get form data
        full_name = request.POST.get("name", user.full_name)
        email = request.POST.get("email", user.email)
        old_password = request.POST.get("old_pass")
        new_password = request.POST.get("new_pass")
        confirm_password = request.POST.get("c_pass")
        profile_image = request.FILES.get("profile_image")

        # Update full name and email
        if full_name:
            user.full_name = full_name
        if email:
            if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "This email is already in use by another account.")
                return redirect('update_profile')
            user.email = email

        # Update profile picture if provided
        if profile_image:
            user.profile_image = profile_image
            messages.success(request, "Profile picture updated successfully.")

        # Password update section
        if old_password or new_password or confirm_password:
            # Check if the old password matches
            if check_password(old_password, user.password):
                # Validate new password match
                if new_password == confirm_password and len(new_password) > 0:
                    user.set_password(new_password)
                    update_session_auth_hash(request, user)  # Keep the user logged in
                    messages.success(request, "Password updated successfully.")
                else:
                    messages.error(request, "New password and confirmation do not match.")
                    return redirect('update_profile')
            else:
                messages.error(request, "Old password is incorrect.")
                return redirect('update_profile')

        # Save the updated information
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")  # Redirect to profile page with success message

    # Render the form with the current user data
    return render(request, "update.html", {'user': user})



@login_required
def enroll_course_with_id(request, id):
    # Fetch the specific course by ID
    selected_course = get_object_or_404(Course, id=id)
  

    # Check if the user is already enrolled in this course
    if CourseEnrollment.objects.filter(user=request.user, course=selected_course).exists():
        # If already enrolled, show an error message
        messages.error(request, "You are already enrolled in this course.")
        return redirect('my_courses')  # Redirect to the "My Courses" page or any other appropriate page

    if request.method == 'POST':
        # Get the starting date and authenticated user
        starting_date = request.POST['starting_date']
        user = request.user

        # Create a course enrollment for the user
        CourseEnrollment.objects.create(
            user=user,
            course=selected_course,
            enrolled_at=starting_date,
            progress=0.0
        )

        # Show a success message
        messages.success(request, "You have successfully enrolled in the course.")
        return redirect('my_courses')  # Redirect to the course dashboard or another page
   
    # Render the template with the selected course only
    return render(request, 'enroll_course.html', {
        'selected_course': selected_course,
        'user': request.user,
        
    })


@login_required
def enroll_course_without_id(request):
    # Fetch all courses
    all_courses = Course.objects.all()

    if request.method == 'POST':
        course_id = request.POST['course']
        starting_date = request.POST['starting_date']
        user = request.user

        # Get the course by ID and create enrollment
        course = get_object_or_404(Course, id=course_id)
        CourseEnrollment.objects.create(
            user=user,
            course=course,
            enrolled_at=starting_date,
            progress=0.0
        )
        messages.success(request, "You have successfully enrolled in the course.")
        return redirect('course_dashboard')

    # Render the template with all courses
    return render(request, 'enroll_course.html', {
        'all_courses': all_courses,
        'user': request.user
    })
@login_required
def my_courses(request):
    # Fetch courses where the user is enrolled
    enrolled_courses = CourseEnrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'my_courses.html', {'enrolled_courses': enrolled_courses})

@login_required
def quiz_detail(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    # Check if the user is enrolled in the course for this quiz
    course_enrollment = CourseEnrollment.objects.filter(user=request.user, course=quiz.course).first()

    if not course_enrollment:
        return HttpResponse("You are not enrolled in this course.")

    # Check if the course progress is above 50%
    if course_enrollment.progress < 50:
        messages.error(request, "You need to complete at least 50% of the course before attempting the quiz.")
        return redirect('course_detail', course_id=quiz.course.id)  # Redirect to course detail or playlist

    return render(request, 'quiz_detail.html', {'quiz': quiz})

# @login_required
# def Quiz(request):
#     return render(request, 'quiz.html')

@login_required
def quiz_view(request, Course_id):
    course=Course.objects.filter(id=Course_id).first()
    quiz = get_object_or_404(Quiz, course=course)
    questions = quiz.questions.all()
    return render(request, 'quizs.html', {'quiz': quiz, 'questions': questions})

@login_required
def check_answers(request):
    if request.method == 'POST':
        # Parse JSON data from POST
        data = json.loads(request.body)
        quiz_id = data.get("quiz_id")
        answers = data.get("answers")

        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()

        correct_count = 0
        results = []

        # Check answers
        for question in questions:
            user_answer = answers.get(str(question.id))
            correct = (user_answer == f"option_{question.correct_option}")
            results.append({
                "question": question.text,
                "user_answer": user_answer,
                "correct_answer": f"option_{question.correct_option}",
                "is_correct": correct,
            })
            if correct:
                correct_count += 1

        score_percentage = (correct_count / len(questions)) * 100
        passed = score_percentage >= quiz.pass_percentage

        # Record the attempt
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score_percentage)

        return JsonResponse({
            "results": results,
            "score": score_percentage,
            "passed": passed,
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)



@login_required
def quiz_attempts(request):
    # Retrieve all quiz attempts for the logged-in user
    attempts = QuizAttempt.objects.filter(user=request.user).select_related('quiz').order_by('-completed_at')
    
    context = {
        'attempts': attempts
    }
    
    return render(request, 'quiz_attempts.html', context)


@login_required
def generate_certificate(request, attempt_id):
    # Get the specific quiz attempt and check if the user has passed it
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if not attempt.is_passed():
        return render(request, 'error.html', {'message': 'You must pass the quiz to view the certificate.'})

    # Render the certificate template with the attempt data
    context = {
        'attempt': attempt,
        'user': request.user,
        'date': attempt.completed_at.date(),
        'quiz_title': attempt.quiz.course.title
    }
    return render(request, 'certificate.html', context)
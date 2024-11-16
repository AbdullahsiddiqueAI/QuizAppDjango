from django.shortcuts import render, redirect,get_object_or_404
from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
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

import re  # Add this import for regular expression support

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")  
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

        # Password validation
        if len(password) < 8 or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messages.error(request, "Password must be at least 8 characters long and contain at least one special character.")
            return redirect("register")

        # Check if the email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        # Create the user
        user = CustomUser.objects.create_user(
            full_name=full_name,  
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
def playlist(request):
    return render(request, 'playlist.html')

@login_required
def course_playlist(request, id):
    # Get the course by ID
    selected_course = get_object_or_404(Course, id=id)

    # Check user enrollment and calculate progress
    enrollment = CourseEnrollment.objects.filter(user=request.user, course=selected_course).first()
    progress = enrollment.progress if enrollment else 0

    # Retrieve all lessons associated with the course
    lessons = selected_course.lessons.all().order_by('order')

    # Get the quiz related to the course and count the user's attempts
    quiz = Quiz.objects.filter(course=selected_course).first()
    attempt_count = QuizAttempt.objects.filter(user=request.user, quiz=quiz).count() if quiz else 0

    # Render the playlist template, passing all necessary data
    return render(request, 'course_playlist.html', {
        'selected_course': selected_course,
        'lessons': lessons,
        'progress': progress,
        'attempt_count': attempt_count,
    })
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def about(request):
    return render(request, 'about.html')

def search_courses(request):
    query = request.GET.get("search_box", "")  # Get the search term from the request
    courses = Course.objects.filter(title__icontains=query) if query else []  # Search courses by title
    return render(request, "search_results.html", {"courses": courses, "query": query})
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        message = request.POST.get("message")

        # Validate the data (optional, you can add more validation as needed)
        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return render(request, "contact.html")

        # Save the data to the database
        Contact.objects.create(name=name, email=email, number=number, message=message)

        # Add a success message
        messages.success(request, "Your message has been sent successfully!")
        return render(request, "contact.html")

    return render(request, "contact.html")

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


@login_required
def quiz_view(request, Course_id):
    # Retrieve the course and quiz
    course = get_object_or_404(Course, id=Course_id)
    quiz = get_object_or_404(Quiz, course=course)

    # Check if the user is enrolled in the course
    enrollment = CourseEnrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        messages.error(request, "You need to be enrolled in this course to take the quiz.")
        return redirect('course_detail', course_id=course.id)  # Redirect to course detail page

    # Check if the user's progress is at least 50%
    if enrollment.progress < 50:
        messages.error(request, "You need to complete at least 50% of the course before attempting the quiz.")
        return redirect('course_playlist', id=course.id)  # Redirect to course playlist or detail page

    # Check if the user has already passed or reached max attempts
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
    if attempts.filter(score__gte=quiz.pass_percentage).exists():
        messages.info(request, "You have already passed this quiz.")
        return redirect(reverse('quiz_result', kwargs={'quiz_id': quiz.id}) + f"?passed=yes")
        # return redirect('quiz_result', quiz_id=quiz.id)  # Redirect to quiz result page

    if attempts.count() >= 3:
        messages.error(request, "You have reached the maximum number of attempts for this quiz.")
        return redirect('quiz_result', quiz_id=quiz.id)  # Redirect to quiz result page

    # Retrieve quiz questions and render the quiz page
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


def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all()
        score = 0
        total_questions = questions.count()

        # Calculate the score based on the submitted answers
        for question in questions:
            user_answer = request.POST.get(f'question{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                score += 1

        # Calculate the score percentage
        score_percentage = (score / total_questions) * 100
        passed = score_percentage >= quiz.pass_percentage

        # Save the quiz attempt
        quiz_attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score_percentage
        )

        # Redirect to the result page with the result information
        return redirect(reverse('quiz_result', kwargs={'quiz_id': quiz.id}) + f"?passed={'yes' if passed else 'no'}")
    return redirect('home')



# views.py

def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz_attempt = QuizAttempt.objects.filter(user=request.user, quiz=quiz).last()
    passed = request.GET.get('passed') == 'yes'
    
    # Calculate grade based on score
    grade = ''
    if quiz_attempt.score >= 90:
        grade = 'A'
    elif quiz_attempt.score >= 80:
        grade = 'B'
    elif quiz_attempt.score >= 70:
        grade = 'C'
    elif quiz_attempt.score >= 60:
        grade = 'D'
    else:
        grade = 'F'
    
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
        'passed': passed,
        'grade': grade,
    })

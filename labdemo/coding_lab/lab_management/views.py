from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User, Lab, Assignment, Submission
import requests

# Paiza.IO API endpoints
PAIZA_CREATE_URL = "https://api.paiza.io/runners/create"
PAIZA_DETAILS_URL = "https://api.paiza.io/runners/get_details"

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        user = User.objects.create_user(username=username, password=password, role=role)
        return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def dashboard(request):
    if request.user.role == 'teacher':
        labs = Lab.objects.filter(created_by=request.user)
        return render(request, 'teacher_dashboard.html', {'labs': labs})
    else:
        assignments = Assignment.objects.all()
        return render(request, 'student_dashboard.html', {'assignments': assignments})

@login_required
def create_lab(request):
    if request.method == 'POST' and request.user.role == 'teacher':
        name = request.POST.get('name')
        description = request.POST.get('description')
        lab = Lab.objects.create(name=name, description=description, created_by=request.user)
        return redirect('dashboard')
    return render(request, 'create_lab.html')

@login_required
def create_assignment(request, lab_id):
    if request.method == 'POST' and request.user.role == 'teacher':
        lab = Lab.objects.get(id=lab_id)
        question = request.POST.get('question')
        deadline = request.POST.get('deadline')
        Assignment.objects.create(lab=lab, question=question, deadline=deadline, created_by=request.user)
        return redirect('dashboard')
    return render(request, 'create_assignment.html')

@login_required
def compile_code(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    if request.method == 'POST':
        code = request.POST.get('code', '')
        language = request.POST.get('language', 'python3')

        # Step 1: Create a runner
        create_payload = {
            "source_code": code,
            "language": language,
            "api_key": "guest",
        }

        try:
            create_response = requests.post(PAIZA_CREATE_URL, json=create_payload)
            create_response.raise_for_status()
            runner_id = create_response.json().get("id")

            if not runner_id:
                return render(request, 'code_editor.html', {'output': "Failed to create runner."})

            # Step 2: Get the results
            details_payload = {
                "id": runner_id,
                "api_key": "guest",
            }

            while True:
                details_response = requests.get(PAIZA_DETAILS_URL, params=details_payload)
                details_response.raise_for_status()
                result = details_response.json()

                status = result.get("status")
                if status == "completed":
                    output = result.get("stdout", "").strip() or result.get("stderr", "Error")
                    break
                elif status in ["running", "pending"]:
                    continue
                else:
                    output = f"Error: {result.get('error', 'Unknown error')}"
                    break
        except Exception as e:
            output = f"An error occurred: {str(e)}"

        return render(request, 'code_editor.html', {'output': output, 'assignment': assignment})

    return render(request, 'code_editor.html', {'assignment': assignment})

@login_required
def submit_code(request, assignment_id):
    if request.method == 'POST':
        assignment = Assignment.objects.get(id=assignment_id)
        code = request.POST.get('code', '')
        output = request.POST.get('output', '')
        is_correct = "Correct" in output  # Simple correctness check
        Submission.objects.create(
            assignment=assignment,
            student=request.user,
            code=code,
            output=output,
            is_correct=is_correct
        )
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def review_submissions(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'submission_review.html', {'submissions': submissions, 'assignment': assignment})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
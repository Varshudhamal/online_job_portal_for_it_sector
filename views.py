from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, Application, Company
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Job
from django.core.mail import send_mail
from django.conf import settings
from .forms import ApplicationForm, ContactForm, JobForm, RegistrationForm, UserProfileForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

# Homepage View
def homepage(request):
    jobs = Job.objects.select_related('company').all()[:6]  # Use select_related for performance
    return render(request, 'jobs/homepage.html', {'jobs': jobs})


# Register View
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the user object
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # Handle the resume file (if exists)
            resume = request.FILES.get('resume')
            if resume:
                fs = FileSystemStorage()
                filename = fs.save(resume.name, resume)  # Save the file
                resume_url = fs.url(filename)

                # Create the user profile and associate it with the user
                user_profile = UserProfile(user=user, resume=resume_url)
                user_profile.save()

            # After successful registration, send a success message
            messages.success(request, 'You have successfully registered! You can now log in.')
            return redirect('login')  # Redirect to login page

        else:
            # If the form is invalid, show an error message
            messages.error(request, 'There was an error with your registration. Please try again.')
    else:
        form = RegistrationForm()

    return render(request, 'jobs/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')

                try:
                    user_profile = UserProfile.objects.get(user=user)
                except UserProfile.DoesNotExist:
                    messages.warning(request, "Your profile is incomplete, please complete your profile.")
                    return redirect('profile')  # Redirect to profile setup page

                # Redirect based on the user role (Employer or Employee)
                if user_profile.is_employer:
                    return redirect('employer_dashboard')
                elif user_profile.is_employee:
                    return redirect('employee_dashboard')
                else:
                    return redirect('employee_dashboard')  # If no role set, ask to complete profile

            else:
                messages.error(request, 'Invalid username or password')

        else:
            messages.error(request, 'Invalid form submission')

    else:
        form = AuthenticationForm()

    return render(request, 'jobs/login.html', {'form': form})

# Dashboard View - Redirect to appropriate dashboard based on user role
@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if user_profile.is_employer:
        return redirect('employer_dashboard')  # Redirect to employer dashboard
    else:
        return redirect('employee_dashboard')  # Redirect to employee dashboard


# Employer Dashboard
@login_required
def employer_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    if not user_profile.is_employer:
        return redirect('employee_dashboard')  # Redirect to employee dashboard if not employer

    # Updated Query to fetch jobs posted by the employer
    jobs_posted = Job.objects.filter(company__employer=request.user)
    total_applications = sum([job.total_applications() for job in jobs_posted])

    context = {
        'jobs_posted': jobs_posted,
        'total_applications': total_applications
    }
    return render(request, 'jobs/employer_dashboard.html', context)



# Employee Dashboard
@login_required
def employee_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    if not user_profile.is_employee:
        return redirect('employer_dashboard')  # Redirect to employer dashboard if not employee

    # Get active jobs
    jobs = Job.objects.filter(is_active=True)

    context = {
        'jobs': jobs
    }
    return render(request, 'jobs/employee_dashboard.html', context)


# Profile View - Update and Complete User Profile
@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the same page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'jobs/profile.html', {'form': form, 'user_profile': user_profile})

def job_details(request, id):
    job = get_object_or_404(Job, id=id)
    return render(request, 'jobs/job_details.html', {'job': job})

@login_required
def post_job(request):
    try:
        company = request.user.company  # Assuming employer has a linked company
    except Company.DoesNotExist:
        messages.error(request, "You need to have a company profile to post a job.")
        return redirect('profile')

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company  # Automatically link the job with the company
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('job_post_success')  # Redirect to the employer dashboard
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})

def job_post_success(request):
    return render(request, 'jobs/job_post_success.html')




# companies view
@login_required
def companies(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if user_profile and user_profile.is_employer:
        # Query companies owned by the logged-in employer
        companies = Company.objects.filter(employer__user=user)
    else:
        companies = []

    return render(request, 'jobs/companies.html', {'companies': companies})


# Applications View for Employers
@login_required
def applications(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if user_profile and user_profile.is_employer:
        # Correct query to filter applications by employer's company
        applications = Application.objects.filter(job__company__employer=user)
    else:
        applications = []

    return render(request, 'jobs/applications.html', {'applications': applications})


# Application Details View for Employers to see more details about an application
@login_required
def application_details(request, id):
    # Get the application object by its ID
    application = get_object_or_404(Application, id=id)

    return render(request, 'jobs/application_details.html', {'application': application})


def view_applications(request, job_id):
    # Get the job object based on the job_id
    job = get_object_or_404(Job, id=job_id)

    # Get all applications for the job
    applications = Application.objects.filter(job=job)

    return render(request, 'jobs/view_applications.html', {'job': job, 'applications': applications})

# This view assumes that an employer has a profile associated with a User and Company model


@login_required
def view_profile(request):
    # Get the current logged-in user
    user = request.user
    
    # Check if the user has an associated company
    try:
        company = user.company
    except Company.DoesNotExist:
        company = None

    return render(request, 'jobs/view_profile.html', {
        'user': user,
        'company': company,
    })


# Job Listings View for Employees to Browse Jobs
def job_listings(request):
    location_filter = request.GET.get('location', '')
    salary_filter = request.GET.get('salary', '')
    category_filter = request.GET.get('category', '')
    sort_order = request.GET.get('sort', 'posted_on')

    # Fetch active jobs
    jobs = Job.objects.filter(is_active=True).order_by('-posted_on')  # Default sorting by 'posted_on'

    # Apply filters
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
    if salary_filter:
        jobs = jobs.filter(salary__gte=salary_filter)
    if category_filter:
        jobs = jobs.filter(category__name__icontains=category_filter)

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_listings.html', {
        'location_filter': location_filter,
        'salary_filter': salary_filter,
        'request': request,
        'page_obj': page_obj,
    })



    return render(request, 'jobs/job_listings.html', {
        'location_filter': location_filter,
        'salary_filter': salary_filter,
        'request': request,
        'page_obj': page_obj,
    })



def view_job(request, job_id):
    # Fetch the job from the database by its ID
    job = get_object_or_404(Job, id=job_id)

    # Render the template and pass the job object to it
    return render(request, 'jobs/view_job.html', {'job': job})

def browse_jobs(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/browse_jobs.html', {'jobs': jobs})
# Apply for Job (Employee View)
@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        cover_letter = request.POST.get("cover_letter")
        resume = request.FILES.get("resume")

        Application.objects.create(
            user=request.user,
            job=job,
            full_name=full_name,
            email=email,
            cover_letter=cover_letter,
            resume=resume,
            status="Applied"
        )

        messages.success(request, "Your application has been submitted successfully!")
        return redirect('application_confirmation')

        

    return render(request, "jobs/apply_for_job.html", {"job": job})



# Application Confirmation View
def application_confirmation(request):
    return render(request, 'jobs/application_confirmation.html')


@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)

    if application.status == "Applied":
        application.delete()
        messages.success(request, "Your application has been withdrawn successfully.")
    else:
        messages.error(request, "You can only withdraw an application that is still in 'Applied' status.")

    return redirect('track_applications')

@login_required
def track_applications(request):
    applications = Application.objects.filter(email=request.user.email)
    return render(request, 'jobs/application_tracking.html', {'applications': applications})

# About Us View
def about_us(request):
    return render(request, 'jobs/about_us.html')

# Contact Us View
def contact_us(request):
    form_sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form_sent = True
            form = ContactForm()  # Clear the form after submission
    else:
        form = ContactForm()

    return render(request, 'jobs/contact_us.html', {'form': form, 'form_sent': form_sent})

# Logout View
def logout(request):
    return render(request, 'jobs/logout.html')

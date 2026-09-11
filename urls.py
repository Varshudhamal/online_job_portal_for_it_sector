from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # Companies & Jobs
    path('companies/', views.companies, name='companies'),
    path('company/<int:company_id>/', views.view_profile, name='company_view'),  # Assuming a separate view exists
    path('post_job/', views.post_job, name='post_job'),

    # Job Listings & Applications
    path('job_listings/', views.job_listings, name='job_listings'),
    path('job/<int:id>/', views.job_details, name='job_details'),
    path('post-job/success/', views.job_post_success, name='job_post_success'),

    # Applying for jobs
    path('job/view/<int:job_id>/', views.view_job, name='view_job'),
    path('jobs/browse/', views.browse_jobs, name='browse_jobs'),
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_for_job'),
    path('application-confirmation/', views.application_confirmation, name='application_confirmation'),
    path('my-applications/', views.track_applications, name='track_applications'),
    path('withdraw/<int:application_id>/', views.withdraw_application, name='withdraw_application'),

    # Applications for Employers
    path('applications/', views.applications, name='applications'),
    path('application/<int:id>/', views.application_details, name='application_details'),
    path('view_applications/<int:job_id>/', views.view_applications, name='view_applications'),

    # Employer Profile
    path('employer/profile/', views.view_profile, name='view_profile'),

    # Miscellaneous
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

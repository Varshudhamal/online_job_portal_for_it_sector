from django.contrib import admin
from .models import Job, Company, Application, UserProfile, JobCategory

class JobAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'company', 'category', 'location', 'salary', 'application_deadline', 'vacancies', 'is_active']
    search_fields = ['job_title', 'company__name', 'category']
    list_filter = ['category', 'is_active']
    ordering = ['posted_on']

    # Automatically associate the company with the logged-in user
    def save_model(self, request, obj, form, change):
        if not obj.company:
            try:
                # Try to get the company associated with the current logged-in user
                obj.company = request.user.company
            except Company.DoesNotExist:
                pass  # If no company is found for the logged-in user, leave it blank
        obj.save()


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'employer', 'website']
    search_fields = ['name', 'employer__username']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_employer', 'company', 'preferred_location']
    search_fields = ['user__username']

class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']




class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job', 'email', 'status', 'applied_on')
    list_filter = ('status',)
    search_fields = ('full_name', 'job__job_title')
    actions = ['mark_shortlisted', 'mark_rejected']

    def mark_shortlisted(self, request, queryset):
        queryset.update(status='Shortlisted')
        self.message_user(request, "Selected applications have been marked as Shortlisted.")
    mark_shortlisted.short_description = "Mark as Shortlisted"

    def mark_rejected(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, "Selected applications have been marked as Rejected.")
    mark_rejected.short_description = "Mark as Rejected"

admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)

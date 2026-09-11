from django import forms
from django.contrib.auth.models import User
from .models import Application, Job, UserProfile, Company
from django.core.exceptions import ValidationError

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    resume = forms.FileField(required=False)
    role = forms.ChoiceField(
        choices=[('employee', 'Employee'), ('employer', 'Employer')],
        widget=forms.Select(),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        if password1:
            if len(password1) < 4:
                raise forms.ValidationError("Password must be at least 4 characters long.")
            if len(password1) > 8:
                raise forms.ValidationError("Password cannot be longer than 8 characters.")

        return cleaned_data




class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'resume', 'preferred_job_title', 'preferred_location', 'employment_type']

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if len(bio) > 500:
            raise forms.ValidationError("Bio cannot be more than 500 characters.")
        return bio


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'})
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your message'}),
        label="Your Message"
    )


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone', 'cover_letter', 'resume']
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'category', 'location', 'description', 'salary', 'application_deadline', 'vacancies', 'is_active']
        widgets = {
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation here if needed
        return cleaned_data


# class JobForm(forms.ModelForm):
#     # Change 'company' to CharField to allow manual input
#     company = forms.CharField(max_length=255, required=True, label="Company Name")
    
#     CATEGORY_CHOICES = [
#          ('software_development', 'Software Development'),
#         ('data_science', 'Data Science & Analytics'),
#         ('web_development', 'Web Development'),
#         ('cloud_computing', 'Cloud Computing'),
#         ('cybersecurity', 'Cybersecurity'),
#         ('devops', 'DevOps'),
#         ('networking', 'Networking'),
#         ('database_management', 'Database Management'),
#         ('ai_ml', 'Artificial Intelligence & Machine Learning'),
#         ('project_management', 'Project Management & IT Consultancy'),
#         ('it_support', 'Systems & IT Support'),
#         ('quality_assurance', 'Quality Assurance & Testing'),
#         ('blockchain', 'Blockchain'),
#         ('digital_marketing', 'Digital Marketing & SEO'),
#         ('business_intelligence', 'Business Intelligence & Reporting'),
    
        
#     ]
    
#     category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False, label="Job Category")
    
#     class Meta:
#         model = Job
#         fields = ['job_title', 'company', 'category', 'location', 'description', 'salary', 'application_deadline', 'vacancies', 'is_active']
#         widgets = {
#             'application_deadline': forms.DateInput(attrs={'type': 'date'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super(JobForm, self).__init__(*args, **kwargs)
#         self.fields['category'].widget.attrs['class'] = 'form-control'
#     def clean_company(self):
#         company_name = self.cleaned_data.get('company')
#         employer = self.initial.get('employer')  # Assuming employer is passed during form initialization
        
#         if not employer:
#             raise forms.ValidationError("Employer must be provided for the company.")
        
#         # Check if company already exists in the database
#         company, created = Company.objects.get_or_create(name=company_name, employer=employer)
        
#         return company
    
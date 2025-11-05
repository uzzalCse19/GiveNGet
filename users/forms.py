from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'phone', 'profile_photo', 'address']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': 'Enter your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': '01XXXXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'rows': 3,
                'placeholder': 'Enter your complete address'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'hidden'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            pattern = r'^(?:\+?88)?01[3-9]\d{8}$'
            if not re.match(pattern, phone):
                raise forms.ValidationError("Please enter a valid Bangladeshi phone number.")
        return phone

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from Upohar.models import UpoharPost

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('receiver', 'Receiver'),
        ('exchanger', 'Exchanger'),
        ('donor', 'Donor'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.HiddenInput(),
        initial='exchanger'
    )
    
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'role', 'profile_photo', 'address', 'password1', 'password2']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'placeholder': '01XXXXXXXXX'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
                'rows': 2,
                'placeholder': 'Your address (optional)'
            }),
            'profile_photo': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'placeholder': 'Create password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email



# class UpoharPostForm(forms.ModelForm):
#     class Meta:
#         model = UpoharPost
#         fields = ['type', 'category', 'title', 'description', 'city', 'image', 
#                  'exchange_item_name', 'exchange_item_description']
#         widgets = {
#             'type': forms.Select(attrs={'class': 'form-control', 'id': 'post-type'}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'city': forms.TextInput(attrs={'class': 'form-control'}),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#             'exchange_item_name': forms.TextInput(attrs={'class': 'form-control exchange-field'}),
#             'exchange_item_description': forms.Textarea(attrs={'class': 'form-control exchange-field', 'rows': 3}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Make exchange fields not required initially
#         self.fields['exchange_item_name'].required = False
#         self.fields['exchange_item_description'].required = False
    
#     def clean(self):
#         cleaned_data = super().clean()
#         post_type = cleaned_data.get('type')
        
#         if post_type == 'exchange':
#             if not cleaned_data.get('exchange_item_name'):
#                 self.add_error('exchange_item_name', 'This field is required for exchange posts.')
#             if not cleaned_data.get('exchange_item_description'):
#                 self.add_error('exchange_item_description', 'This field is required for exchange posts.')
        
#         return cleaned_data
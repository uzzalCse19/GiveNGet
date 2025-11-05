from django import forms
from Upohar.models import UpoharPost
class UpoharPostForm(forms.ModelForm):
    class Meta:
        model = UpoharPost
        fields = ['type', 'category', 'title', 'description', 'city', 'image', 
                 'exchange_item_name', 'exchange_item_description']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'hidden'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': 'Enter a clear title for your item',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'rows': 4,
                'placeholder': 'Describe your item in detail (condition, size, brand, etc.)',
                'maxlength': '1000'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': 'Enter your city'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden'
            }),
            'exchange_item_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': 'What would you like to receive in exchange?',
                'maxlength': '200'
            }),
            'exchange_item_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'rows': 3,
                'placeholder': 'Describe what you\'re looking for',
                'maxlength': '500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make exchange fields not required initially
        self.fields['exchange_item_name'].required = False
        self.fields['exchange_item_description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        post_type = cleaned_data.get('type')
        
        if post_type == 'exchange':
            if not cleaned_data.get('exchange_item_name'):
                self.add_error('exchange_item_name', 'This field is required for exchange posts.')
            if not cleaned_data.get('exchange_item_description'):
                self.add_error('exchange_item_description', 'This field is required for exchange posts.')
        
        return cleaned_data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make exchange fields not required initially
        self.fields['exchange_item_name'].required = False
        self.fields['exchange_item_description'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        post_type = cleaned_data.get('type')
        
        if post_type == 'exchange':
            if not cleaned_data.get('exchange_item_name'):
                self.add_error('exchange_item_name', 'This field is required for exchange posts.')
            if not cleaned_data.get('exchange_item_description'):
                self.add_error('exchange_item_description', 'This field is required for exchange posts.')
        
        return cleaned_data
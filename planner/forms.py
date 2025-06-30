from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Event, RSVP


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 20:
            raise forms.ValidationError("Username cannot be more than 20 characters.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password1(self):
        pwd = self.cleaned_data.get('password1')
        if len(pwd) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return pwd
    
class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) > 20:
            raise forms.ValidationError("Username cannot be more than 20 characters.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email



# class UpdateUserForm(forms.ModelForm):
#     email = forms.EmailField(max_length=100, required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email']

#     def clean_username(self):
#         username = self.cleaned_data.get('username')
#         if len(username) > 20:
#             raise forms.ValidationError("Username cannot be more than 20 characters.")
#         return username

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if not email:
#             raise forms.ValidationError("Email is required.")
#         if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
#             raise forms.ValidationError("This email is already in use.")
#         return email



class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'guest_emails']
        widgets = {
            'title': forms.TextInput(attrs={'required': True}),
            'description': forms.Textarea(attrs={'required': True}),
            'date': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'time': forms.TimeInput(attrs={'type': 'time', 'required': True}),
            'location': forms.TextInput(attrs={'required': True}),
            'guest_emails': forms.Textarea(attrs={'required': True}),
        }

        

# class EventForm(forms.ModelForm):
#     class Meta:
#         model = Event
#         fields = ['title', 'description', 'date', 'time', 'location', 'guest_emails']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time'}),
#         }





class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['response', 'note']




class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

from django import forms
from django.contrib.auth.forms import SetPasswordForm

# class OptionalPasswordChangeForm(SetPasswordForm):
#     def __init__(self, user, *args, **kwargs):
#         super().__init__(user, *args, **kwargs)
#         # Make fields optional in frontend (HTML)
#         self.fields['new_password1'].required = False
#         self.fields['new_password1'].widget.attrs['required'] = False
#         self.fields['new_password2'].required = False
#         self.fields['new_password2'].widget.attrs['required'] = False

#     def is_valid(self):
#         password1 = self.data.get('new_password1', '').strip()
#         password2 = self.data.get('new_password2', '').strip()

#         if not password1 and not password2:
#             self.cleaned_data = {}
#             return True
#         return super().is_valid()

#     def save(self, commit=True):
#         if self.cleaned_data:
#             return super().save(commit=commit)
#         return self.user


from django.contrib.auth.forms import SetPasswordForm

class OptionalPasswordChangeForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        # Make fields optional in frontend (HTML)
        for field_name in ['new_password1', 'new_password2']:
            field = self.fields[field_name]
            field.required = False
            field.widget.attrs.update({
                'required': False,
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
            })

    def is_valid(self):
        password1 = self.data.get('new_password1', '').strip()
        password2 = self.data.get('new_password2', '').strip()

        if not password1 and not password2:
            self.cleaned_data = {}
            return True
        return super().is_valid()

    def save(self, commit=True):
        if self.cleaned_data:
            return super().save(commit=commit)
        return self.user


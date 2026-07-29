from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm, UsernameField,
    PasswordResetForm, PasswordChangeForm, SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import Customer


# ------------------ REGISTER ------------------
class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    # ✅ PASSWORD MATCH
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Passwords do not match!")

        # ✅ Django password validation
        password_validation.validate_password(password)

        return cleaned_data

    # ✅ EMAIL UNIQUE
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered!")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# ------------------ LOGIN ------------------
class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': True,
        'class': 'form-control'
    }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control'
        })
    )


# ------------------ PASSWORD CHANGE ------------------
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Old Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autofocus': True,
            'class': 'form-control'
        })
    )

    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html()
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


# ------------------ PASSWORD RESET ------------------
class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


# ------------------ SET NEW PASSWORD ------------------
class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html()
    )

    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


# ------------------ CUSTOMER PROFILE ------------------
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['f_name', 'm_name', 'l_name', 'email']

        widgets = {
            'f_name': forms.TextInput(attrs={'class': 'form-control'}),
            'm_name': forms.TextInput(attrs={'class': 'form-control'}),
            'l_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
# from django import forms
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField,PasswordResetForm, PasswordChangeForm, SetPasswordForm
# from django.utils.translation import gettext, gettext_lazy as _
# from django.contrib.auth import password_validation
# from .models import *
# from django.contrib.auth.hashers import make_password

# class RegisterUserForm(forms.ModelForm):
#     password = forms.CharField(
#         label='Password', 
#         widget=forms.PasswordInput(attrs={'class': 'form-control'})
#     )
#     password2 = forms.CharField(
#         label="Confirm Password", 
#         widget=forms.PasswordInput(attrs={'class': 'form-control'})
#     )

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']  # Include 'password' so it gets saved
#         labels = {'email': 'Email'}
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         password2 = cleaned_data.get("password2")

#         if password and password2 and password != password2:
#             raise forms.ValidationError("Passwords do not match!")

#         return cleaned_data

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.password = make_password(self.cleaned_data["password"])  # Hash the password
#         if commit:
#             user.save()
#         return user


# class LoginForm(AuthenticationForm):
#     username = UsernameField(widget=forms.TextInput(attrs={'autofocus':True,'class':'form-control'}))
#     password = forms.CharField(label=_("Password"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'class':'form-control'}))



# class MyPasswordChangeForm(PasswordChangeForm):
#     old_password = forms.CharField(label=_("Old Password"),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'current-password','class':'form-control'}))
#     new_password1 = forms.CharField(label=_("New Password"),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'new-password','class':'form-control'}),help_text=password_validation.password_validators_help_text_html())
#     new_password2 = forms.CharField(label=_("Confirm New Password"),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'new-password','class':'form-control'}))



# class MyPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(label=_("Email"), max_length=254,widget=forms.EmailInput(attrs={'class':'form-control form-control-lg'}))



# class MySetPasswordForm(SetPasswordForm):
#     new_password1 = forms.CharField(label=_("New Password"),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'new-password','class':'form-control'}),help_text=password_validation.password_validators_help_text_html())
#     new_password2 = forms.CharField(label=_("Confirm New Password"),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'new-password','class':'form-control'}))


# class CustomerProfileForm(forms.ModelForm):
#     class Meta:
#         model = Customer
#         fields = ['name', 'locality', 'city', 'state', 'zipcode' ]
#         widgets = {'name': forms.TextInput(attrs={'class':'form-control'}),'city':forms.TextInput(attrs={'class':'form-control'}),'locality':forms.TextInput(attrs={'class':'form-control'}),'state':forms.TextInput(attrs={'class':'form-control'}),'zipcode':forms.TextInput(attrs={'class':'form-control'})}
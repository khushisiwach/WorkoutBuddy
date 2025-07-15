from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']



class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)



class ProfileForm(forms.ModelForm):
    class Meta:
        fields = ['age', 'gender', 'height', 'weight', 'activity_level', 'goal']
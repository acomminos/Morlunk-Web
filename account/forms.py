from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

class RegisterForm(ModelForm):
	username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$', error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
	password = forms.CharField(label="Password", widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ["username", "password",  "email", "first_name", "last_name"]
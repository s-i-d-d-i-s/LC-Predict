from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	#github = forms.CharField(max_length=30)

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']#,'github']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['github']
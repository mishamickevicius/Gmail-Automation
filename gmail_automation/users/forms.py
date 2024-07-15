from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ('username', 'email') # Include username and email fields

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserCreationForm(SignUpForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
# accounts/forms.py
from django import forms
import secrets
import string

class CreateUserForm(forms.Form):
    email = forms.EmailField(
        label="Email de l'utilisateur",
        widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded'})
    )
    
    def generate_temp_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(12))



class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Email administrateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Mot de passe'
        })
    )
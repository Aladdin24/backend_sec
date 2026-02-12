# accounts/views.py
import threading
from documents.permissions import IsAdminUser
from .models import InvitationToken, User
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import permission_classes
from django.shortcuts import render, redirect
from accounts.models import InvitationToken, User
from django.contrib.admin.views.decorators import staff_member_required


#------------------------------ Account Activation View -----------------------------------
def activate_account_page(request):
    token = request.GET.get('token') or request.POST.get('token')
    if not token:
        return render(request, 'activation/activation_error.html', {
            'error': 'Token manquant'
        })

    try:
        invite = InvitationToken.objects.get(token=token)
        if not invite.is_valid():
            return render(request, 'activation/activation_error.html', {
                'error': 'Ce lien a expiré ou a déjà été utilisé.'
            })
    except InvitationToken.DoesNotExist:
        return render(request, 'activation/activation_error.html', {
            'error': 'Lien d’activation invalide.'
        })

    if request.method == 'GET':
        return render(request, 'activation/activate_account.html', {
            'token': token,
            'email': invite.invited_email
        })

    # POST
    password = request.POST.get('password')
    public_key = request.POST.get('public_key')

    if not password or not public_key:
        return render(request, 'activation/activate_account.html', {
            'token': token,
            'email': invite.invited_email,
            'error': 'Tous les champs sont obligatoires'
        })

    # Validation mot de passe
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    try:
        validate_password(password, user=User(email=invite.invited_email))
    except ValidationError as e:
        return render(request, 'activation/activate_account.html', {
            'token': token,
            'email': invite.invited_email,
            'error': ' '.join(e.messages)
        })

    try:
        user = User.objects.create_user(
            email=invite.invited_email,
            password=password,
            public_key=public_key,
            is_active=True,
            created_by=invite.created_by
        )
        invite.used = True
        invite.save()
    except Exception:
        return render(request, 'activation/activate_account.html', {
            'token': token,
            'email': invite.invited_email,
            'error': 'Erreur serveur. Veuillez réessayer.'
        })

    return render(request, 'activation/activation_success.html')
    

#------------------------------ Admin Dashboard Views -----------------------------------

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import User, InvitationToken
from documents.models import Category, Document
from .forms import CreateUserForm

@staff_member_required(login_url='admin_login')
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    user_count = User.objects.count()
    active_user_count = User.objects.filter(is_active=True).count()
    doc_count = Document.objects.count()
    category_count = Category.objects.count()
    return render(request, 'admin_dashboard/dashboard.html', {
        'user_count': user_count,
        'active_user_count': active_user_count,
        'doc_count': doc_count,
        'category_count': category_count,
    })

@staff_member_required(login_url='admin_login')
@permission_classes([IsAdminUser])
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_dashboard/users.html', {'users': users})

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def _send_welcome_email(email, temp_password):
    """Fonction asynchrone pour envoyer l'email de bienvenue"""
    try:
        send_mail(
            subject="Bienvenue sur SecureDoc",
            message=f"""
Bonjour,

Votre compte SecureDoc a été créé par un administrateur.

📧 Email : {email}
🔒 Mot de passe temporaire : {temp_password}

⚠️ Vous devrez changer ce mot de passe à votre première connexion.

Connectez-vous ici : https://app.secdoc.example.com/login
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email à {email}: {e}")

@staff_member_required(login_url='admin_login')
@permission_classes([IsAdminUser])
def admin_create_user(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Générer mot de passe temporaire
            temp_password = form.generate_temp_password()
            
            try:
                # Valider le mot de passe
                validate_password(temp_password, user=User(email=email))
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    email=email,
                    password=temp_password,
                    is_active=True,
                    must_change_password=True,
                    created_by=request.user
                )
                
                # ENVOI ASYNCHRONE DE L'EMAIL
                email_thread = threading.Thread(
                    target=_send_welcome_email,
                    args=(email, temp_password)
                )
                email_thread.start()
                
                messages.success(request, f"Utilisateur créé et identifiants envoyés à {email}")
                return redirect('admin_users')
                
            except ValidationError as e:
                messages.error(request, f"Erreur création : {' '.join(e.messages)}")
            except Exception as e:
                logger.error(f"Erreur création utilisateur {email}: {e}")
                messages.error(request, "Erreur serveur. Contactez l'administrateur.")
    else:
        form = CreateUserForm()
    
    return render(request, 'admin_dashboard/create_user.html', {'form': form})



@staff_member_required(login_url='admin_login')
@permission_classes([IsAdminUser])
def admin_toggle_user_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('admin_users')
    
    user.is_active = not user.is_active
    user.save()
    status = "activé" if user.is_active else "désactivé"
    messages.success(request, f"L'utilisateur {user.email} a été {status}.")
    return redirect('admin_users')



from .forms import AdminLoginForm
from django.contrib.auth import authenticate, login


def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authentifier l'utilisateur
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Vérifier que c'est un admin (is_staff = True)
                if user.is_staff:
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Accès réservé aux administrateurs.")
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = AdminLoginForm()
    
    return render(request, 'admin_dashboard/admin_login.html', {'form': form})



from django.contrib.auth import logout

def admin_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect('admin_login')  # Redirige vers la page de login admin
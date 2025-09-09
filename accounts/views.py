import os
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_protect

from smart_irrigation import settings
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .utils import send_brevo_transactional_email
from django.db import transaction
from irrigation.db_utils import acquire_connection


def home(request):
    return render(request, 'accounts/home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            with acquire_connection() as connection:
                with transaction.atomic(using=connection.alias):
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password1'])
                    user.save()
                    login(request, user)
                    messages.success(request, 'Registration successful. Welcome!')
                    return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


@login_required
def profile(request):
    if request.method == 'POST':
        # Check if this is a profile picture only upload
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'profile_picture' in request.FILES:
            return handle_profile_picture_upload(request)

        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                user = form.save()

                # Return appropriate response based on request type
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    profile_picture_url = user.get_profile_picture_url()
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Profile updated successfully',
                        'profile_picture_url': profile_picture_url,
                        'phone_number': user.phone_number
                    })

                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    }, status=400)
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Form validation failed',
                    'errors': form.errors.get_json_data()
                }, status=400)
            messages.error(request, 'Please correct the errors below.')

    else:
        form = CustomUserChangeForm(instance=request.user)

    # Get profile picture URL safely
    profile_picture_url = request.user.get_profile_picture_url()

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user,
        'profile_picture_url': profile_picture_url
    })


def handle_profile_picture_upload(request):
    """Handle AJAX profile picture uploads separately"""
    try:
        profile_picture = request.FILES['profile_picture']

        # Validate file size (10MB max)
        if profile_picture.size > 10 * 1024 * 1024:
            return JsonResponse({
                'status': 'error',
                'message': 'Image file too large ( > 10MB )'
            }, status=400)

        # Validate file type
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(profile_picture.name)[1].lower()
        if ext not in valid_extensions:
            return JsonResponse({
                'status': 'error',
                'message': 'Unsupported file extension. Please use .jpg, .jpeg, .png, or .gif'
            }, status=400)

        # Save new profile picture
        request.user.profile_picture = profile_picture
        request.user.save()

        profile_picture_url = request.user.get_profile_picture_url()

        return JsonResponse({
            'status': 'success',
            'message': 'Profile picture updated successfully',
            'profile_picture_url': profile_picture_url
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    return render(request, 'accounts/delete_account.html')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = CustomUser.objects.filter(email=email)
            if associated_users.exists():
                current_site = get_current_site(request)
                for user in associated_users:
                    subject = "Password Reset Request"
                    email_template = "accounts/password_reset_email.html"

                    context = {
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': current_site.name,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }

                    email_content = render_to_string(email_template, context)

                    # Use Brevo API to send email
                    if send_brevo_transactional_email(user.email, subject, email_content):
                        return redirect("password_reset_done")
                    else:
                        messages.error(request, "Failed to send password reset email. Please try again later.")
                        return redirect("password_reset")

            # Always return success to prevent email enumeration
            return redirect("password_reset_done")

    else:
        form = PasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form})


@login_required
def confirm_token_regeneration(request):
    return render(request, 'accounts/confirm_token_regeneration.html')


@require_POST
@csrf_protect
@login_required
def regenerate_api_key(request):
    if 'confirm' not in request.POST:
        # If not confirmed, redirect to confirmation page
        return redirect('confirm_token_regeneration')

    if request.POST['confirm'] == 'yes':
        # Delete the old token
        Token.objects.filter(user=request.user).delete()
        # Create a new token
        new_token = Token.objects.create(user=request.user)

        # If AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'API token regenerated successfully',
                'new_api_token': new_token.key
            })

        # For regular form submission
        messages.success(request, 'Your API token has been regenerated successfully.')
        return redirect('profile')

    # If confirmation was 'no'
    messages.info(request, 'Token regeneration cancelled. Your current token remains active.')
    return redirect('profile')


@require_POST
@csrf_protect
@login_required
def cleanup_broken_image(request):
    """Clean up reference to broken profile picture"""
    if request.user.is_authenticated and request.user.profile_picture:
        try:
            # Verify the image is actually broken by trying to access it
            request.user.profile_picture.url
            return JsonResponse({'status': 'info', 'message': 'Image exists'})
        except Exception as e:
            # Image is broken - remove the reference
            request.user.profile_picture = None
            request.user.save()
            return JsonResponse({'status': 'success', 'message': 'Broken image reference removed'})

    return JsonResponse({'status': 'info', 'message': 'No image to clean up'})


def default_avatar(request):
    """Serve a default avatar image"""
    if settings.IS_PRODUCTION:
        # Return a Cloudinary URL for default avatar
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        return redirect(f"https://res.cloudinary.com/{cloud_name}/image/upload/v1/default_avatar")
    else:
        # Serve local default avatar
        default_avatar_path = os.path.join(settings.BASE_DIR, 'accounts', 'static', 'default_avatar.png')
        if os.path.exists(default_avatar_path):
            with open(default_avatar_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='image/png')
        else:
            # Return a simple SVG as fallback
            svg_avatar = '''
            <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="40" r="20" fill="#ccc"/>
                <circle cx="50" cy="100" r="40" fill="#ccc"/>
            </svg>
            '''
            return HttpResponse(svg_avatar, content_type='image/svg+xml')


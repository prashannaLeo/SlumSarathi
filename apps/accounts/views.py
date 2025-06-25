from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from .models import User, Profile, PasswordResetToken, EmailVerificationToken, NewsletterSubscriber
import datetime
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if not user.is_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return render(request, 'accounts/login.html')
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 1)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
            Profile.objects.create(user=user)
            # Create email verification token (valid for 24 hours)
            expires_at = timezone.now() + datetime.timedelta(hours=24)
            token = EmailVerificationToken.objects.create(user=user, expires_at=expires_at)
            verification_link = request.build_absolute_uri(
                reverse('verify_email', args=[str(token.token)])
            )
            subject = 'Verify your email address'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]

            # Render HTML and plain text versions
            html_content = render_to_string('accounts/verify_email.html', {
                'user': user,
                'verification_link': verification_link,
            })
            text_content = f"Hi {user.get_full_name() or user.email},\n\nThank you for registering! Please verify your email by clicking the link below:\n\n{verification_link}\n\nIf you did not register, please ignore this email.\n\nBest regards,\nThe slumSarathi Team"

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, 'Registration successful! Please check your email to verify your account within 24 hours.')
            return redirect('login')
    return render(request, 'accounts/register.html')

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'profile', None)
    return render(request, 'accounts/profile.html', {'user_obj': user, 'profile': profile})

@login_required
def edit_profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user:
        return HttpResponse('Unauthorized', status=401)
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.institution = request.POST.get('institution', profile.institution)
        profile.course_of_study = request.POST.get('course_of_study', profile.course_of_study)
        profile.organization = request.POST.get('organization', profile.organization)
        profile.website = request.POST.get('website', profile.website)
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile', user_id=user.id)
    return render(request, 'accounts/edit_profile.html', {'user_obj': user, 'profile': profile})

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Create a token valid for 1 hour
            expires_at = timezone.now() + datetime.timedelta(hours=1)
            token = PasswordResetToken.objects.create(user=user, expires_at=expires_at)
            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[str(token.token)])
            )
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, 'A password reset link has been sent to your email.')
        else:
            messages.error(request, 'No user found with that email address.')
        return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def reset_password_view(request, token):
    token_obj = get_object_or_404(PasswordResetToken, token=token)
    if not token_obj.is_valid():
        messages.error(request, 'This password reset link is invalid or has expired.')
        return redirect('login')
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        if password and password == confirm:
            user = token_obj.user
            user.set_password(password)
            user.save()
            token_obj.mark_as_used()
            messages.success(request, 'Your password has been reset. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'accounts/reset_password.html', {'token': token})

def verify_email_view(request, uuid):
    try:
        token_obj = EmailVerificationToken.objects.get(token=uuid)
        if not token_obj.is_valid():
            messages.error(request, 'This verification link is invalid or has expired.')
            return redirect('login')
        user = token_obj.user
        if not user.is_verified:
            user.is_verified = True
            user.save()
            token_obj.mark_as_used()
            messages.success(request, 'Your email has been verified. You can now log in.')
        else:
            messages.info(request, 'Your email is already verified.')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('login')

def newsletter_signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please enter a valid email address.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.info(request, 'You are already subscribed to the newsletter.')
        else:
            NewsletterSubscriber.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect(request.META.get('HTTP_REFERER', '/'))

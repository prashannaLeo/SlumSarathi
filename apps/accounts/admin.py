from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, PasswordResetToken, NewsletterSubscriber

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'user_type', 'is_verified', 'verification_uuid')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'is_verified')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions',)

    actions = ['mark_as_verified', 'mark_as_unverified']

    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} user(s) marked as verified.")
    mark_as_verified.short_description = "Mark selected users as verified"

    def mark_as_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} user(s) marked as unverified.")
    mark_as_unverified.short_description = "Mark selected users as unverified"

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'institution', 'organization', 'created_at')
    search_fields = ('user__email', 'institution', 'organization')
    list_filter = ('gender', 'institution', 'organization')

class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    search_fields = ('user__email', 'token')
    list_filter = ('is_used',)

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    list_filter = ('created_at',)

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
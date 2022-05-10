from api.models import CustomUser
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import (UserAdmin as BaseUserAdmin,
                                       GroupAdmin as BaseGroupAdmin)
from api.forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin', 'first_name', 'last_name', 'phone_number', 'is_active')
    list_filter = ('is_admin', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'groups')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'patronymic', 'phone_number', 'bio', 'avatar')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'groups', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# class CustomUserInline(admin.TabularInline):
#     model =
#
#
# class CustomGroupAdmin(BaseGroupAdmin):
#     class Meta:
#
#     inlines = [
#         CustomUserInline,
#     ]
#
#     # # exclude = ('members',)


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.unregister(Group)
# admin.site.register(Group, CustomGroupAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.

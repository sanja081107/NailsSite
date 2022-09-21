from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .forms import *
from .models import *


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'client', 'service', 'date', 'is_active')
    list_display_links = ('id', 'title')
    list_editable = ('is_active',)
    list_filter = ('date',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'birthday', 'get_html_photo', 'instagram', 'mobile', 'photo']
    list_editable = ['birthday', 'photo', 'instagram', 'mobile']
    list_display_links = ['username']

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{ object.photo.url }' width=50>")

    get_html_photo.short_description = 'Миниатюра'


class ProfitForMonthAdmin(admin.ModelAdmin):
    list_display = ('title', 'profit', 'date')
    list_display_links = ('title',)


class MyWorksAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_html_photo', 'date', 'is_active')
    list_editable = ('is_active',)
    list_display_links = ('id', 'title',)

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{ object.photo.url }' width=50>")

    get_html_photo.short_description = 'Фото работы'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ProfitForMonth, ProfitForMonthAdmin)
admin.site.register(MyWorks, MyWorksAdmin)
admin.site.register(Service)


admin.site.site_title = 'DariaNailsMinsk'
admin.site.site_header = 'DariaNailsMinsk'
admin.site.index_title = 'Admin'



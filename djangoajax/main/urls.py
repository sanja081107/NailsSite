from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from .views import *

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', home, name='home'),
    path('book_manicure/', book_manicure, name='book_manicure'),
    path('confirm_book_<int:pk>/', confirm_book),
    path('create_book/', create_book, name='create_book'),
    path('edit_book_<int:pk>/', EditBookView.as_view(), name='edit_book'),
    path('is_active_<int:pk>/', is_active, name='is_active'),
    path('not_active_<int:pk>/', not_active, name='not_active'),
    path('get_answer_ajax/', answer_ajax, name='answer_ajax'),

    path('registration/', RegisterUser.as_view(), name='registration'),
    path('log_in/', LoginUser.as_view(), name='log_in'),
    path('logout/', log_out_user, name='logout'),
    path('user_edit_<int:pk>/', UserUpdateView.as_view(), name='user_edit'),
    path('user_detail_<int:pk>/', user_detail, name='user_detail'),

    path('change_password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<slug:uidb64>/<slug:token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

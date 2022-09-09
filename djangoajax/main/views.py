from django.contrib.auth import logout, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import *
from .tasks import *


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Page not found</h1>')


def home(request):
    context = {'title': 'Главная', 'title_body': 'Главная страница'}

    return render(request, 'main/index.html', context)


def create_book(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        form = PostForm()
        posts = Post.objects.all()
        if request.method == 'POST':
            form = PostForm(request.POST)
            try:
                if form.is_valid():
                    form.save()
                    return redirect('create_book')
            except:
                form.add_error(None, 'Неверные данные')  # Создается общая ошибка, если форма не связана с моделью и некорректна

        context = {'title': 'Создать запись на маникюр', 'title_body': 'Создать запись на маникюр', 'form': form, 'posts': posts}

        return render(request, 'main/create_book.html', context)


class EditBookView(PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'main/edit_book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение записи'
        context['title_body'] = 'Изменение записи'
        return context

    def get_success_url(self):
        return reverse_lazy('create_book')

    def get_permission_required(self):
        if not self.request.user.is_staff:
            return True
        else:
            return redirect('home')


def is_active(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    else:
        post = Post.objects.get(pk=pk)
        post.is_active = True
        post.save()
        return redirect('create_book')

def not_active(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    else:
        post = Post.objects.get(pk=pk)
        post.is_active = False
        post.client = None
        post.service = None
        post.save()
        return redirect('create_book')

def book_manicure(request):
    if not request.user.is_authenticated:
        return redirect('log_in')
    else:

        today = datetime.date(datetime.now())
        # year = today.year
        # month = today.month
        # day = today.day
        # days_in_month = calendar.monthrange(year, month)[1]

        access_time = []
        posts = Post.objects.filter(client=None, is_active=True)
        for el in posts:
            if el.date > today:
                access_time.append(str(el.date))
        access_time = set(access_time)
        access_time = list(access_time)

        context = {'title': 'Запись на ногти', 'title_body': 'Запись на ногти', 'access_time': access_time}

        return render(request, 'main/book_manicure.html', context)


def confirm_book(request, pk):
    post = Post.objects.get(pk=pk)
    today = datetime.date(datetime.now())
    if post.client or post.date < today:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    if not request.user.is_authenticated:
        return redirect('log_in')
    else:

        form = PostUserForm()
        if request.method == 'POST':
            form = PostUserForm(request.POST)
            try:
                service_id = request.POST['service']
                post.client = request.user
                post.service = Service.objects.get(pk=service_id)
                post.save()
                order_created.delay(post.id)
                return redirect('home')
            except:
                form.add_error(None, 'Нужно выбрать услугу')  # Создается общая ошибка, если форма не связана с моделью и некорректна

        context = {
            'title': 'Подтверждение',
            'title_body': 'Подтверждение записи',
            'form': form,
            'el': post,
        }
        return render(request, 'main/confirm_book.html', context)


def user_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('log_in')
    else:
        el = CustomUser.objects.get(pk=pk)
        if request.user != el:
            return redirect('home')
        else:
            context = {
                'el': el,
                'title': el.username,
                'title_body': el.username
            }
            return render(request, 'main/user_detail.html', context)


class RegisterUser(CreateView):
    # form_class = UserCreationForm     можно напрямую отдать форму от джанго или создать свою в forms.py
    form_class = CustomUserCreationForm
    template_name = 'main/registration.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        context['title_body'] = 'Регистрация'
        return context

    def form_valid(self, form):     # эта ф-ия вызывается после успешной обработки формы и логинит пол-ля
        user = form.save()
        login(self.request, user)
        return redirect('home')


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    template_name = 'main/registration.html'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Обновление данных'
        context['title_body'] = 'Обновление данных о пользователе'
        return context

    def get_success_url(self):
        post = CustomUser.objects.get(pk=self.kwargs['pk'])
        return post.get_absolute_url()

    def get_permission_required(self):
        us = CustomUser.objects.get(pk=self.kwargs['pk'])
        if self.request.user != us:
            return True
        else:
            return redirect('home')

def log_out_user(request):
    logout(request)             # стандартная ф-ия джанго для выхода пользователя
    return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'main/log_in_user.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в систему'
        context['title_body'] = 'Вход в систему'
        return context


def answer_ajax(request):

    if request.method == 'GET':
        date = request.GET['date']
        posts = Post.objects.filter(date=date, client=None, is_active=True)

        if posts and date != str(datetime.date(datetime.now())):
            return JsonResponse({"posts": list(posts.values())})
        elif date == str(datetime.date(datetime.now())):
            return HttpResponse('no today', content_type='text/html')
        else:
            return HttpResponse('no', content_type='text/html')
    else:
        return HttpResponse('no', content_type='text/html')

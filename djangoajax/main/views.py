import calendar
import datetime

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, UpdateView
from django_celery_beat.models import *
import json

from .forms import *
from .tasks import *


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Page not found</h1>')


def home(request):
    lorem = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Autem deserunt distinctio ducimus error' \
            ' ipsa magnam maxime, molestiae, mollitia odio quam recusandae rem, repellendus voluptas! A ad atque' \
            ' distinctio dolorem ducimus eveniet fugit illum magnam minus neque non perspiciatis possimus, quos' \
            ' repellendus rerum sed soluta temporibus totam unde vitae voluptas voluptatibus!'

    context = {'title': 'Главная', 'title_body': 'Главная страница', 'cont': lorem}

    return render(request, 'main/index.html', context)


def create_book(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        form = PostForm()

        list_post = []
        today = datetime.date(datetime.now())
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]

        first_day = today - timedelta(today.day-1)              # Первый день месяца
        last_day = first_day + timedelta(days_in_month-1)       # Последний день месяца

        posts = Post.objects.all().order_by('date')
        if posts:
            for el in posts:
                if first_day <= el.date <= last_day:
                    list_post.append(el)                        # Список записей которые мы выводим в соответствии с временным диапазоном
                posts = list_post

        if request.method == 'POST':
            form = PostForm(request.POST)
            try:
                if form.is_valid():
                    form.save()
                    return redirect('create_book')
            except:
                form.add_error(None, 'Неверные данные')         # Создается общая ошибка, если форма не связана с моделью и некорректна

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


def all_users(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        users = CustomUser.objects.all()
        context = {'title': 'Все пользователи', 'title_body': 'Все пользователи',
                   'users': users}

        return render(request, 'main/index.html', context)


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
        if post.client:
            order_canceled.delay(pk)
            task = PeriodicTask.objects.get(name='{}-{}'.format(post.title, post.id))
            task.delete()
        post.is_active = False
        post.client = None
        post.service = None
        post.save()

        return redirect('create_book')


def book_manicure(request):
    if not request.user.is_authenticated:
        return redirect('log_in')
    else:

        user = request.user
        post = Post.objects.filter(client=user)
        if post:
            today = post[0].date + timedelta(days=5)    # Если у пользователя есть текущая запись, то он не сможет сделать запись на следующие 5 дней с даты записи
        else:
            today = datetime.date(datetime.now())

        access_time = []
        posts = Post.objects.filter(client=None, is_active=True)
        for el in posts:
            if el.date >= today:
                access_time.append(str(el.date))
        access_time = set(access_time)
        access_time = list(access_time)                 # Список дат которые отдаются на календарь как доступные даты

        context = {'title': 'Запись на ногти', 'title_body': 'Запись на ногти', 'access_time': access_time}

        return render(request, 'main/book_manicure.html', context)


def confirm_book(request, pk):
    post = Post.objects.get(id=pk)

    user = request.user
    post_client = Post.objects.filter(client=user)
    if post_client:
        today = post_client[0].date + timedelta(days=5)
    else:
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
                post.service = Service.objects.get(id=service_id)
                post.save()
                # order_created.delay(post.id)
                today = datetime.now()
                PeriodicTask.objects.create(
                    name='{}-{}'.format(post.title, post.id),
                    task='order_created',
                    # crontab=CrontabSchedule.objects.create(minute=today.minute+1, hour=today.hour),   # day_of_week=today.day, day_of_month=today.month, day_of_year=today.year
                    interval=IntervalSchedule.objects.get(every=5, period='seconds'),
                    args=json.dumps([post.id]),
                    start_time=today,
                    one_off=True,
                )
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

    user = CustomUser.objects.get(pk=pk)
    if not request.user.is_staff and request.user != user:
        return redirect('home')
    else:
        context = {
            'el': user,
            'title': user.username,
            'title_body': 'Имя пользователя: ' + user.username
        }
        return render(request, 'main/user_detail.html', context)


class RegisterUser(CreateView):
    # form_class = UserCreationForm     можно напрямую отдать форму от джанго или создать свою в forms.py
    form_class = CustomUserCreationForm
    template_name = 'main/registration.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            context = super().get_context_data(**kwargs)
            context['title'] = 'Регистрация'
            context['title_body'] = 'Регистрация'
            return context

    def form_valid(self, form):     # эта ф-ия вызывается после успешной обработки формы и логинит пол-ля
        user = form.save()
        login(self.request, user)
        return redirect('home')


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    template_name = 'main/registration.html'

    def get_context_data(self, **kwargs):
        user = CustomUser.objects.get(pk=self.kwargs['pk'])
        if not self.request.user == user and not self.request.user.is_staff:
            return reverse_lazy('home')
        else:
            context = super().get_context_data(**kwargs)
            context['title'] = 'Обновление данных'
            context['title_body'] = 'Обновление данных о пользователе'
            return context

    def get_success_url(self):
        post = CustomUser.objects.get(pk=self.kwargs['pk'])
        return post.get_absolute_url()


def log_out_user(request):
    logout(request)             # стандартная ф-ия джанго для выхода пользователя
    return redirect('home')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'main/log_in_user.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
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
            return HttpResponse('today', content_type='text/html')
        else:
            return HttpResponse('no', content_type='text/html')
    else:
        return HttpResponse('no', content_type='text/html')

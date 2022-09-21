import calendar
import datetime

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator
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

        today = datetime.date(datetime.now())
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]

        first_day = today - timedelta(today.day-1)              # Первый день месяца
        last_day = first_day + timedelta(days_in_month-1)       # Последний день месяца

        list_post = []
        posts = Post.objects.all().order_by('date')
        if posts:
            for el in posts:
                if first_day <= el.date <= last_day:
                    list_post.append(el)
            len_post = len(list_post)                           # Список записей которые мы выводим в соответствии с текущим месяцем
            middle = int(len_post/2)
            list_post = []
            for el in posts:
                if el.date >= first_day:
                    list_post.append(el)

        paginator = Paginator(list_post, len_post)              # Показывает все записи на текущий месяца
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if page_number == '1' or not page_number:
            page_obj_title = 'Записи за текущий месяц:'
        else:
            page_obj_title = 'Записи за последующие месяца:'

        if request.method == 'POST':
            form = PostForm(request.POST)
            try:
                if form.is_valid():
                    form.save()
                    return redirect('create_book')
            except:
                form.add_error(None, 'Неверные данные')         # Создается общая ошибка, если форма не связана с моделью и некорректна

        context = {'title': 'Создать запись на маникюр',
                   'title_body': 'Создать запись на маникюр',
                   'page_obj_title': page_obj_title,
                   'form': form,
                   'before_middle': f":{middle}",
                   'after_middle': f"{middle}:",
                   'page_obj': page_obj,
                   'paginator': paginator,
                   }

        return render(request, 'main/create_book.html', context)


class EditBookView(UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'main/edit_book.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_staff:
            context = {'error': 'error!'}
            return context
        else:
            context = super().get_context_data(**kwargs)
            context['title'] = 'Изменение записи'
            context['title_body'] = 'Изменение записи'
            return context

    def get_success_url(self):
        return reverse_lazy('create_book')


def all_users(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        users = CustomUser.objects.all()
        paginator = Paginator(users, 10)              # Показывает все записи на текущий месяца
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'title': 'Все пользователи',
            'title_body': 'Все пользователи',
            'users': 'yes',
            'page_obj': page_obj,
            'paginator': paginator,
        }

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
    post = Post.objects.get(pk=pk)
    user = request.user

    if user.is_staff:
        if post.client:
            order_canceled.delay(pk)
            task = PeriodicTask.objects.filter(name='{}-{}'.format(post.title, post.id))
            if task.exists():
                task[0].delete()
        post.is_active = False
        post.client = None
        post.service = None
        post.save()

        return redirect('create_book')

    elif post.client == user:
        order_canceled.delay(pk)
        task = PeriodicTask.objects.filter(name='{}-{}'.format(post.title, post.id))
        if task.exists():
            task[0].delete()

        post.client = None
        post.service = None
        post.save()
        return redirect('my_book')
    else:
        return redirect('home')


def book_manicure(request):
    if not request.user.is_authenticated:
        return redirect('log_in')
    else:

        posts = Post.objects.filter(client=None, is_active=True)
        user = request.user
        post = Post.objects.filter(client=user)
        n = 3                                                          # количество неактивных дней за и после записи
        if post:                                                       # Условие если у текущего пользователя есть записи
            no_access_time = []
            for el in post:
                if el.date > datetime.date(datetime.now()):
                    today_in = el.date - timedelta(days=n)
                    today_end = el.date + timedelta(days=n)            # Если у пользователя есть запись, то он не сможет сделать запись за и после n дней с даты записи
                    print(today_in, today_end)
                    date = el.date - timedelta(days=n+1)
                    for i in range(n*2+1):
                        date = date + timedelta(days=1)
                        if today_in <= date <= today_end:
                            no_access_time.append(str(date))
            no_access_time = set(no_access_time)
            no_access_time = list(no_access_time)
            today = datetime.date(datetime.now())
            access_time = []
            for el in posts:
                if el.date >= today:
                    access_time.append(str(el.date))
            access_time = set(access_time)
            access_time = list(access_time)
            access = set(access_time) - set(no_access_time)
            access = list(access)
        else:                                                       # Условие если у текущего пользователя нет записей
            access_time = []
            today = datetime.date(datetime.now())
            for el in posts:
                if el.date >= today:
                    access_time.append(str(el.date))
            access_time = set(access_time)
            access_time = list(access_time)
            access = access_time                                    # Список дат которые отдаются на календарь как доступные даты

        context = {'title': 'Запись на ногти', 'title_body': 'Запись на ногти', 'access_time': access, 'n': n}

        return render(request, 'main/book_manicure.html', context)


def confirm_book(request, pk):

    if not request.user.is_authenticated:
        return redirect('log_in')
    else:
        select_post = Post.objects.get(pk=pk)

        user = request.user
        posts = Post.objects.filter(client=None, is_active=True)
        post = Post.objects.filter(client=user)
        n = 3                                                   # количество неактивных дней за и после записи
        if post:                                                # Условие если у текущего пользователя есть записи
            no_access_time = []
            for el in post:
                if el.date > datetime.date(datetime.now()):
                    today_in = el.date - timedelta(days=n)
                    today_end = el.date + timedelta(days=n)     # Если у пользователя есть запись, то он не сможет сделать запись за и после n дней с даты записи
                    date = el.date - timedelta(days=n+1)
                    for i in range(n*2+1):
                        date = date + timedelta(days=1)
                        if today_in <= date <= today_end:
                            no_access_time.append(str(date))
            no_access_time = set(no_access_time)
            no_access_time = list(no_access_time)
            today = datetime.date(datetime.now())
            access_time = []
            for el in posts:
                if el.date > today:                             # отсчет идет с завтрашнего дня, если с сегодняшнего то исп. >=
                    access_time.append(str(el.date))
            access_time = set(access_time)
            access_time = list(access_time)
            access = set(access_time) - set(no_access_time)
        else:                                                   # Условие если у текущего пользователя нет записей
            access_time = []
            today = datetime.date(datetime.now())
            for el in posts:
                if el.date > today:                             # отсчет идет с завтрашнего дня, если с сегодняшнего то исп. >=
                    access_time.append(str(el.date))
            access_time = set(access_time)
            access_time = list(access_time)
            access = access_time                                # Список дат которые отдаются на календарь как доступные даты

        i = 0
        for dt in access:
            if str(select_post.date) == dt and not select_post.client:
                i += 1
        if i != 1:
            return HttpResponseNotFound('<h1>Page not found</h1>')

        form = PostServiceForm()
        if request.method == 'POST':
            form = PostServiceForm(request.POST)
            try:
                service_id = request.POST['service']
                select_post.client = request.user
                select_post.service = Service.objects.get(id=service_id)
                select_post.save()
                # order_created.delay(post.id)
                today = datetime.now()
                PeriodicTask.objects.create(
                    name='{}-{}'.format(select_post.title, select_post.id),
                    task='order_created',
                    # crontab=CrontabSchedule.objects.create(minute=today.minute+1, hour=today.hour),   # day_of_week=today.day, day_of_month=today.month, day_of_year=today.year
                    interval=IntervalSchedule.objects.get(every=5, period='seconds'),
                    args=json.dumps([select_post.id]),
                    start_time=today,
                    one_off=True,
                )
                return redirect('my_book')
            except:
                form.add_error(None, 'Нужно выбрать услугу')  # Создается общая ошибка, если форма не связана с моделью и некорректна
        time = select_post.title.split()
        context = {
            'title': 'Подтверждение',
            'title_body': 'Подтверждение записи',
            'form': form,
            'el': select_post,
            'time': time[1],
        }
        return render(request, 'main/confirm_book.html', context)


def statistic(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        today = datetime.date(datetime.now())
        year = today.year
        month = today.month
        days_in_month = calendar.monthrange(year, month)[1]

        first_day = today - timedelta(today.day-1)              # Первый день месяца
        last_day = first_day + timedelta(days_in_month-1)       # Последний день месяца

        print(first_day, last_day)

        posts_all = Post.objects.all().order_by('date')
        posts_clients = []
        for el in posts_all:
            if el.client:
                posts_clients.append(el)                        # Список записей где есть клиент

        current_profit_for_this_month_to_now = [0]
        expected_profit_for_this_remaining_month = [0]
        current_profit_to_now = [0]
        expected_profit_for_all_next_months = [0]

        list_for_this_month_to_now = []
        list_for_this_remaining_month = []
        list_to_now = []
        list_for_all_other_months = []

        if posts_clients:
            for el in posts_clients:
                if first_day <= el.date <= today:
                    list_for_this_month_to_now.append(el)
                    current_profit_for_this_month_to_now.append(el.service.price)

            for el in posts_clients:
                if today < el.date <= last_day:
                    list_for_this_remaining_month.append(el)
                    expected_profit_for_this_remaining_month.append(el.service.price)

            for el in posts_clients:
                if el.date <= today:
                    list_to_now.append(el)
                    current_profit_to_now.append(el.service.price)

            for el in posts_clients:
                if el.date > last_day:
                    list_for_all_other_months.append(el)
                    expected_profit_for_all_next_months.append(el.service.price)

        profit_all = ProfitForMonth.objects.all()
        profit = 0
        for el in profit_all:
            profit += el.profit

        current_profit_for_this_month_to_now = sum(current_profit_for_this_month_to_now)
        expected_profit_for_this_remaining_month = sum(expected_profit_for_this_remaining_month)
        current_profit_to_now = sum(current_profit_to_now)
        expected_profit_for_all_next_months = sum(expected_profit_for_all_next_months)

        context = {
            'title': 'Статистика',
            'title_body': 'Статистика записей',
            'statistic': 'yes',
            'profit_all': profit_all,
            'profit': profit,

            'list_for_this_month_to_now': list_for_this_month_to_now,
            'current_profit_for_this_month_to_now': current_profit_for_this_month_to_now,

            'list_for_this_remaining_month': list_for_this_remaining_month,
            'expected_profit_for_this_remaining_month': expected_profit_for_this_remaining_month,

            'list_to_now': list_to_now,
            'current_profit_to_now': current_profit_to_now,

            'list_for_all_other_months': list_for_all_other_months,
            'expected_profit_for_all_next_months': expected_profit_for_all_next_months,

        }
        return render(request, 'main/index.html', context)


class MyWorksCreateView(CreateView):
    form_class = MyWorksCreateForm
    template_name = 'main/my_works.html'
    success_url = reverse_lazy('my_works')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои работы'
        context['title_body'] = 'Мои работы'
        context['title_block'] = 'Создать новую работу\n(Эту форму не видят пользователи)'
        context['posts'] = MyWorks.objects.filter(is_active=True)
        return context

class MyWorksUpdateView(UpdateView):
    model = MyWorks
    form_class = MyWorksCreateForm
    template_name = 'main/my_works.html'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_staff:
            context = {'error': 'error!'}
            return context
        else:
            post = MyWorks.objects.get(pk=self.kwargs['pk'])
            context = super().get_context_data(**kwargs)
            context['title'] = 'Мои работы'
            context['title_body'] = 'Изменение данных о работе'
            context['title_block'] = 'Изменить работу'
            context['post'] = post
            context['delete'] = 'yes'
            return context

    def get_success_url(self):
        return redirect('my_works')


def delete_work(request, pk):
    if not request.user.is_staff:
        context = {
            'error': 'error!',
        }
        return render(request, 'main/my_works.html', context)
    else:
        post = MyWorks.objects.get(pk=pk)
        if post:
            post.delete()
        return redirect('my_works')


def my_book(request):
    if not request.user.is_authenticated:
        return redirect('log_in')
    else:
        user = request.user
        posts = Post.objects.filter(client=user).order_by('date')
        today = datetime.date(datetime.now())
        book = ''
        old_book = ''

        books = []
        for el in posts:
            if el.date >= today:
                books.append(el)
        if len(books) == 0:
            book = '0'                              # Если записей нет то выводим текст записей нет

        old_books = []
        for el in posts:
            if el.date <= today:
                old_books.append(el)
        if len(old_books) == 0:
            old_book = '0'

        context = {
            'title': 'Мои записи',
            'title_body': 'Мои записи',
            'books_page': 'yes',
            'books': books,
            'book': book,
            'old_books': old_books,
            'old_book': old_book,
        }
        return render(request, 'main/index.html', context)


def user_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('log_in')

    user = CustomUser.objects.get(pk=pk)
    if not request.user.is_staff and request.user != user:
        context = {'error': 'error'}
        return render(request, 'main/registration.html', context)
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
            context = {'error': 'error!'}
            return context
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


def certificates(request):
    context = {
        'certificates': 'yes',
        'title': 'Сертификаты',
        'title_body': 'Сертификаты',
    }
    return render(request, 'main/index.html', context)


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

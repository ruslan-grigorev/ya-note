from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='first'
        )
        cls.reader = User.objects.create(username='Читатель простой')

    def test_pages_availability_for_anonymous_client(self):
        url = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )

        for name in url:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_reader_client(self):
        url = (
            'notes:add',
            'notes:success',
            'notes:list',
        )
        self.client.force_login(self.reader)

        for name in url:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        url = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
            'notes:add',
            'notes:success',
            'notes:list',
        )
        for name in url:
            with self.subTest(name=name):
                if name in ('notes:delete', 'notes:edit', 'notes:detail'):
                    url = reverse(name, args=(self.note.slug,))
                if name in ('notes:add', 'notes:success', 'notes:list'):
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

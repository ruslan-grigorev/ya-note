from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestHomePage(TestCase):
    NOTES_LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')

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
        cls.note_reader = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            author=cls.reader,
            slug='second'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_visibility_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['object_list']

        with self.subTest("Заметка текущего пользователя видна"):
            self.assertIn(self.note, object_list)

        with self.subTest("Заметка другого пользователя не видна"):
            self.assertNotIn(self.note_reader, object_list)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for name, url in [('add', self.ADD_URL), ('edit', self.edit_url)]:
            with self.subTest(page=name):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

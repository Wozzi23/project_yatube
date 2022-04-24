from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse_lazy


class StaticAboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.url_author = reverse_lazy('about:author')
        cls.url_tech = reverse_lazy('about:tech')

    def test_url_status(self):
        """Страницы author, tech
                доступны любому пользователю."""
        list_url = [
            self.url_author, self.url_tech]
        for url in list_url:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            self.url_author: 'about/author.html',
            self.url_tech: 'about/tech.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

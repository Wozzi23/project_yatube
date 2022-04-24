from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse_lazy

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание',
            )
        )
        cls.url_index = reverse_lazy('posts:index')
        cls.url_group_list = reverse_lazy(
            'posts:group_list', kwargs={'slug': cls.post.group.slug})
        cls.url_profile = reverse_lazy(
            'posts:profile', kwargs={'username': cls.post.author})
        cls.url_post_detail = reverse_lazy(
            'posts:post_detail', kwargs={'post_id': cls.post.pk})
        cls.url_create = reverse_lazy('posts:post_create')
        cls.url_post_edit = reverse_lazy(
            'posts:post_edit', kwargs={'post_id': cls.post.pk})
        cls.url_add_comment = reverse_lazy(
            'posts:add_comment', kwargs={'post_id': cls.post.pk})
        cls.url_follow = reverse_lazy('posts:follow_index')
        cls.url_profile_follow = reverse_lazy(
            'posts:profile_follow', kwargs={'username': cls.post.author})
        cls.url_profile_unfollow = reverse_lazy(
            'posts:profile_unfollow', kwargs={'username': cls.post.author})

    def setUp(self):
        self.guest_client = Client()
        self.user = StaticURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_status(self):
        """Страницы index, group_list, url_profile, post_detail
        доступны любому пользователю."""

        list_url = [
            self.url_index, self.url_group_list,
            self.url_profile, self.url_post_detail
        ]
        for url in list_url:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404(self):
        """Тест несуществующей страницы."""

        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_url_create_and_adit_authorized(self):
        """Страницы create,post_edit,follow_index доступны авторизованному
        пользователю."""

        list_url = [self.url_create, self.url_post_edit, self.url_follow]
        for url in list_url:
            with self.subTest():
                response = (self.authorized_client.get(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_add_comment_authorized(self):
        """Добавление комментария доступно авторизованному
            пользователю."""
        form = {
            'post': self.post,
            'author': self.user,
            'text': 'Tests comment'
        }
        response = self.authorized_client.post(
            self.url_add_comment,
            data=form,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_and_adit_post_anonim(self):
        """Страницы по адресу create, post_edit, add_comment, follow_index
        перенаправят анонимного пользователя на страницу логина.
        """

        redirect_url = {
            self.url_create: '/auth/login/?next=' + str(self.url_create),
            self.url_post_edit:
                ('/auth/login/?next=' + str(self.url_post_edit)),
            self.url_add_comment:
                ('/auth/login/?next=' + str(self.url_add_comment)),
            self.url_follow:
                ('/auth/login/?next=' + str(self.url_follow)),
            self.url_profile_follow:
                ('/auth/login/?next=' + str(self.url_profile_follow)),
            self.url_profile_unfollow:
                ('/auth/login/?next=' + str(self.url_profile_unfollow)),
        }
        for url, address in redirect_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, address)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            self.url_index: 'posts/index.html',
            self.url_group_list: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_create: 'posts/create_post.html',
            self.url_post_edit: 'posts/create_post.html',
            self.url_follow: 'posts/follow.html'
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

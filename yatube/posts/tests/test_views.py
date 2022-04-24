import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse, reverse_lazy
from ..models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Тестирование views функций"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.user_follow = User.objects.create_user(username='follow')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание',
            ),
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент',
        )
        cls.group_test = Group.objects.create(
            title='Тестовая группа1',
            slug='testslug1',
            description='Тестовое описание1',
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
        cls.url_follow = reverse_lazy('posts:follow_index')
        cls.url_profile_follow = reverse_lazy(
            'posts:profile_follow', kwargs={'username': cls.post.author})
        cls.url_profile_unfollow = reverse_lazy(
            'posts:profile_unfollow', kwargs={'username': cls.post.author})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostsPagesTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_index)
        first_object = response.context['posts'][0]
        task_text_0 = first_object.text
        task_title_0 = first_object.group.title
        task_slug_0 = first_object.group.slug
        task_image_0 = first_object.image
        self.assertEqual(task_title_0, self.post.group.title)
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_slug_0, self.post.group.slug)
        self.assertEqual(task_image_0, self.post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = (self.authorized_client.
                    get(self.url_group_list))
        first_object = response.context['posts'][0]
        task_text_0 = first_object.text
        task_title_0 = first_object.group.title
        task_slug_0 = first_object.group.slug
        task_image_0 = first_object.image
        self.assertEqual(task_title_0, self.post.group.title)
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_slug_0, self.post.group.slug)
        self.assertEqual(task_image_0, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = (self.authorized_client.
                    get(self.url_profile))
        first_object = response.context['posts'][0]
        task_text_0 = first_object.text
        task_title_0 = first_object.group.title
        task_slug_0 = first_object.group.slug
        task_image_0 = first_object.image
        self.assertEqual(task_title_0, self.post.group.title)
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_slug_0, self.post.group.slug)
        self.assertEqual(task_image_0, self.post.image)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = (self.authorized_client.
                    get(self.url_post_detail))
        comments = Comment.objects.first()
        self.assertEqual(response.context.
                         get('post_id').group.title, self.post.group.title)
        self.assertEqual(response.context.
                         get('post_id').text, self.post.text)
        self.assertEqual(response.context.
                         get('post_id').group.slug, self.post.group.slug)
        self.assertEqual(response.context.
                         get('post_id').image, self.post.image)
        self.assertEqual(comments.text, self.comment.text)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_post_edit)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""

        response = self.authorized_client.get(self.url_create)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_list_is_1(self):
        """Проверка отображения поста в index """

        response = self.authorized_client.get(self.url_index)
        self.assertEqual(response.context['posts'].count(), 1)

    def test_profile_page_list_is_1(self):
        """Проверка отображения поста в profile """

        response = (self.authorized_client.
                    get(self.url_profile))
        self.assertEqual(response.context['posts'].count(), 1)

    def test_group_list_page_list_is_1(self):
        """Проверка отображения поста в group_list """

        response = (self.authorized_client.
                    get(self.url_group_list))
        self.assertEqual(response.context['posts'].count(), 1)

    def test_post_in_the_right_group(self):
        """ Проверяем что пост не попал в другую группу """

        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_test.slug}
                    )
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cashe_index(self):
        """ Проверяем кэширование главной страницы"""

        response = self.authorized_client.get(self.url_index).content
        self.post.delete()
        response_cache = self.authorized_client.get(self.url_index).content
        self.assertEqual(response, response_cache)
        cache.clear()
        response_clear = self.authorized_client.get(self.url_index).content
        self.assertNotEqual(response, response_clear)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    """Класс проверки работы паджинатора во views
    index, group_list, profile
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.bulk_create([
            Post(
                author=cls.user,
                text=f'Тестовая пост{i}',
                group=cls.group
            ) for i in range(14)
        ])
        cls.url_index = reverse_lazy('posts:index')
        cls.url_group_list = reverse_lazy(
            'posts:group_list', kwargs={'slug': 'test-slug'})
        cls.url_profile = reverse_lazy(
            'posts:profile', kwargs={'username': 'auth'})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Тест паджинации 10 постов на первой странице"""

        reverse_name = [
            self.url_index,
            self.url_group_list,
            self.url_profile,
        ]
        for rev in reverse_name:
            with self.subTest(rev=rev):
                response = self.client.get(rev)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Тест паджинации 3 постов на второй странице"""

        reverse_name = [
            self.url_index,
            self.url_group_list,
            self.url_profile,
        ]
        for rev in reverse_name:
            with self.subTest(rev=rev):
                response = self.client.get(rev + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 4)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowViewTest(TestCase):
    """Класс проверки подписки на авторов"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_follow = User.objects.create_user(username='follow')
        cls.user_follow_2 = User.objects.create_user(username='follow2')
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_follow_2
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test-slug',
                description='Тестовое описание',
            )
        )
        cls.url_profile = reverse_lazy(
            'posts:profile', kwargs={'username': cls.post.author})
        cls.url_follow = reverse_lazy('posts:follow_index')
        cls.url_profile_follow = reverse_lazy(
            'posts:profile_follow', kwargs={'username': cls.post.author})
        cls.url_profile_unfollow = reverse_lazy(
            'posts:profile_unfollow', kwargs={'username': cls.post.author})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_3 = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2.force_login(self.user_follow)
        self.authorized_client_3.force_login(self.user_follow_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_profile_follow(self):
        """Тест работы подписки на автора"""

        follow_count = Follow.objects.count()
        response = self.authorized_client_2.post(
            self.url_profile_follow, follow=True
        )
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_follow,
                author=self.user
            ).exists()
        )

    def test_profile_unfollow(self):
        """Тест работы отписки на автора"""

        response = self.authorized_client_3.post(
            self.url_profile_unfollow, follow=True
        )
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Follow.objects.count(), 0)

    def test_profile_index(self):
        """Тест отображения нового поста на странице /follow"""

        new_post = Post.objects.create(
            author=self.user,
            text='Тестовая пост для подписчика'
        )
        response = self.authorized_client_3.get(self.url_follow)

        first_object = response.context['post'][0]
        post_text_0 = first_object.text
        self.assertEqual(post_text_0, new_post.text)

    def test_profile_index_nofollower(self):
        """Тест отсутствия нового поста на странице /follow не подписчика"""

        Post.objects.create(
            author=self.user,
            text='Тестовая пост для подписчика'
        )
        response = self.authorized_client_2.get(self.url_follow)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_duble_follow(self):
        """Тест отсутствия задвоения подписки"""

        response = self.authorized_client_3.post(
            self.url_profile_follow, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.user_follow_2.follower.count(), 1)

import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse_lazy, reverse
from ..forms import PostForm
from ..models import Post, Group, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    """Класс проверки формы модели Post"""

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
        cls.form = PostForm

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostsFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        """Тест формы создания поста"""

        post_count = Post.objects.count()

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
        form_data = {
            'text': self.post.text,
            'group': self.post.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.url_create,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.post.group.pk,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit_form(self):
        """Тест формы редактированиия поста"""

        new_text = 'Новый тестовый пост'
        form_data = dict(
            text=new_text
        )
        response = self.authorized_client.post(
            self.url_post_edit,
            data=form_data
        )
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.post.text, new_text)

    def test_add_comment_form(self):
        """Тест формы комментариев поста"""

        text = 'Test comment'
        com_count = Comment.objects.count()
        form = {
            'post': self.post,
            'author': self.user,
            'text': text
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), com_count + 1)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.text, form['text'])
        self.assertEqual(comment.author, self.post.author)

from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class BaseModelTest(TestCase):
    """Базовый класс для проверки моделей"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинна которого превышает 15 символов',
        )


class PostModelTest(BaseModelTest):
    """Класс проверки модели Post"""

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""

        post = PostModelTest.post
        expect_str_post = post.text
        self.assertEqual(str(post), expect_str_post[:15])


class GroupModelTest(BaseModelTest):
    """Класс проверки модели Group"""

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""

        group = GroupModelTest.group
        expect_str_group = group.title
        self.assertEqual(str(group), expect_str_group)

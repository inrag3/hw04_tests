from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
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
            text='Тестовый пост',
        )

    def test_posts_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        object_names = {
            post.text[:15]: str(post),
            group.title: str(group),
        }
        for value, expected_value in object_names.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected_value)

    def test_posts_post_has_correct_verbose_name(self):
        post = PostModelTest.post
        verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(field=field):
                verbose = post._meta.get_field(field).verbose_name
                self.assertEqual(verbose, verbose_name)

    def test_posts_post_has_correct_help_text(self):
        post = PostModelTest.post
        help_texts = {
            'text': 'Введите текст поста',
            'author': 'Укажите автора поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, help_text in help_texts.items():
            with self.subTest(field=field):
                verbose = post._meta.get_field(field).help_text
                self.assertEqual(verbose, help_text)

    def test_posts_group_has_correct_verbose_name(self):
        group = PostModelTest.group
        verbose_names = {
            'title': 'Заголовок статьи',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(field=field):
                verbose = group._meta.get_field(field).verbose_name
                self.assertEqual(verbose, verbose_name)

    def test_posts_group_has_correct_help_text(self):
        group = PostModelTest.group
        help_texts = {
            'title': 'Введите заголовок статьи',
            'slug': 'Введите уникальный адрес группы',
            'description': 'Укажите информацию о группе',
        }
        for field, help_text in help_texts.items():
            with self.subTest(field=field):
                verbose = group._meta.get_field(field).help_text
                self.assertEqual(verbose, help_text)

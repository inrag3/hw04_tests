from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_post_create_successfully(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_posts_post_edit_successfully(self):
        form_data = {
            'text': 'Изменённый тестовый пост',
        }
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(str(Post.objects.get(id=PostFormTests.post.id)),
                         form_data['text'][:15])

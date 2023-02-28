import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_post_create_successfully(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'image': PostFormTests.uploaded,
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

    def test_posts_unauthorized_user_cannot_create_comment(self):
        post = PostFormTests.post
        form_data = {
            'post': post,
            'text': 'Тестовый комментарий'
        }
        count = Comment.objects.count()
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(count + 1, Comment.objects.count())
        self.assertIn(Comment.objects.get(pk=1), post.comments.all())

    def test_posts_authorized_user_cannot_create_comment(self):
        post = PostFormTests.post
        form_data = {
            'post': post,
            'text': 'Тестовый комментарий'
        }
        count = Comment.objects.count()
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(count, Comment.objects.count())
        self.assertFalse(len(post.comments.all()))

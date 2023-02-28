from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Group, Post, Follow
from django.urls import reverse
from ..forms import PostForm
from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.empty_group = Group.objects.create(
            title='Тестовая пустая группа',
            slug='empty',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostViewTest.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTest.user)

    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostViewTest.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostViewTest.author.username}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostViewTest.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostViewTest.post.id}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_pages_show_correct_context(self):
        routes = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                    'slug': PostViewTest.group.slug}),
            reverse('posts:profile', kwargs={
                    'username': PostViewTest.author.username}),
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.authorized_author_client.get(route)
                posts = response.context['page_obj']
                self.assertIn(PostViewTest.post, posts)

    def test_posts_post_detail_show_correct_context(self):
        route = reverse('posts:post_detail', kwargs={
                        'post_id': PostViewTest.post.id})
        response = self.authorized_author_client.get(route)
        post = response.context['post']
        self.assertEqual(PostViewTest.post, post)

    def test_posts_with_form_correct_context(self):
        routes = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={
                'post_id': PostViewTest.post.id}),
        ]
        for route in routes:
            response = self.authorized_author_client.get(route)
            self.assertIsInstance(response.context['form'], PostForm)

    def test_posts_not_in_unintended_group(self):
        route = reverse('posts:group_list',
                        kwargs={'slug': PostViewTest.empty_group.slug})
        response = self.authorized_author_client.get(route)
        self.assertNotIn(PostViewTest.post, response.context['page_obj'])

    def test_posts_user_can_follow(self):
        count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostViewTest.author.username})
        )
        self.assertRedirects(response, reverse('posts:follow_index'))
        self.assertEqual(count + 1, Follow.objects.count())

    def test_posts_user_can_unfollow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostViewTest.author.username})
        )
        count = Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': PostViewTest.author.username})
        )
        self.assertRedirects(response, reverse('posts:follow_index'))
        self.assertEqual(count - 1, Follow.objects.count())

    def test_posts_followed_user_has_correct_feed(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostViewTest.author.username})
        )
        post = Post.objects.create(
            author=PostViewTest.author,
            text='Тестовый пост',
            group=PostViewTest.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(PostViewTest.post, response.context['page_obj'])
        self.assertIn(post, response.context['page_obj'])

    def test_posts_unfollowed_user_has_correct_feed(self):
        self.assertFalse(Follow.objects.filter(
            author__following__user=PostViewTest.user
        ).exists())
        post = Post.objects.create(
            author=PostViewTest.author,
            text='Тестовый пост',
            group=PostViewTest.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(PostViewTest.post, response.context['page_obj'])
        self.assertNotIn(post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        posts = [
            Post(text='Тестовый пост',
                 author=PaginatorViewsTest.user,
                 group=PaginatorViewsTest.group)
            for _ in range(13)
        ]
        cls.post = Post.objects.bulk_create(posts)

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.user)

    def test_posts_pages_contains_necessary_records(self):
        first_page = POSTS_PER_PAGE
        second_page = Post.objects.count() - first_page
        pages_len = {
            reverse('posts:index'): first_page,
            reverse('posts:index') + '?page=2': second_page,
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}):
            first_page,
            reverse('posts:group_list', kwargs={
                    'slug': PaginatorViewsTest.group.slug}) + '?page=2':
            second_page,
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user.username}):
            first_page,
            reverse('posts:profile', kwargs={
                    'username': PaginatorViewsTest.user.username}) + '?page=2':
            second_page,
        }
        for reverse_page, posts_len in pages_len.items():
            response = self.authorized_author_client.get(reverse_page)
            with self.subTest(reverse_page=reverse_page):
                self.assertEqual(len(response.context['page_obj']), posts_len)

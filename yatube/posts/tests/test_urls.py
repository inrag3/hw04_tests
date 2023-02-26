from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Group, Post
from http import HTTPStatus

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.routes = [
            '/',
            '/group/' + f'{ cls.group.slug }' + '/',
            '/profile/' + f'{ cls.user.username }' + '/',
            '/posts/' + f'{ cls.post.id }' + '/',
            '/posts/' + f'{ cls.post.id }' + '/edit/',
            '/create/',
            '/unexisting_page/',
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostURLTests.user_2)

    def test_posts_urls_exists_at_desired_location_authorized(self):
        """Проверяем доступность страниц для авторизованного пользователя"""
        status_code_list = [
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.NOT_FOUND.value,
        ]
        results = dict(zip(PostURLTests.routes, status_code_list))
        for route, status_code in results.items():
            with self.subTest(status_code=status_code):
                response = self.authorized_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_exists_at_desired_location_authorized(self):
        """Проверяем доступность страниц для неавторизованного пользователя"""
        status_code_list = [
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.OK.value,
            HTTPStatus.FOUND.value,
            HTTPStatus.FOUND.value,
            HTTPStatus.NOT_FOUND.value,
        ]
        results = dict(zip(PostURLTests.routes, status_code_list))
        for route, status_code in results.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(route)
                self.assertEqual(response.status_code, status_code)

    def test_posts_urls_uses_correct_template(self):
        """Проверяет использует ли URL-адрес соответствующий шаблон."""
        templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        ]
        results = dict(zip(PostURLTests.routes[:-1], templates))
        for route, template in results.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(route)
                self.assertTemplateUsed(response, template)

    def test_posts_edit_access_only_for_author(self):
        response = self.authorized_client_2.get(PostURLTests.routes[4],
                                                follow=True)
        self.assertRedirects(response, PostURLTests.routes[3])

    def test_posts_urls_redirect_anonymous(self):
        results = {}
        for route in PostURLTests.routes[4:6]:
            results[route] = f'/auth/login/?next={route}'
        for route, redirect_page in results.items():
            with self.subTest(redirect_page=redirect_page):
                response = self.guest_client.get(route, follow=True)
                self.assertRedirects(response, redirect_page)

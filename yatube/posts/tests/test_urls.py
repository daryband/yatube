from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, Comment

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        author_user = User.objects.create_user(username='authoruser')
        Post.objects.create(
            text='Test text',
            author=author_user,
        )
        Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(User.objects.get(username='testuser'))
        self.author_client = Client()
        self.author_client.force_login(User.objects.get(username='authoruser'))
        self.urls_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username':'testuser'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }

    def test_urls_uses_correct_template(self):
        """Check that correct templates are used."""
        for address, template in self.urls_templates.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_returns_404(self):
        """Check that request to unexisting page returns status 404"""
        response = self.auth_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, 404)

    def test_post_edit_only_for_author(self):
        """Check that guest can't edit the post"""
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_user_can_not_edit_post(self):
        """Check that user can't edit the post"""
        response = self.auth_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}), follow=True)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': '1'}))

    def test_author_can_edit_post(self):
        """Check that author of the post can edit it"""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        self.assertEqual(response.status_code, 200)

    def test_pages_are_available_for_guest(self):
        """Check that certain pages are available without logging in"""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'testuser'}),
            reverse('posts:post_detail', kwargs={'post_id': '1'}),
        ]
        for url in urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_create_page_unavailable_for_guest(self):
        """Check that guest user can't create post"""
        response = self.guest_client.get(
            reverse('posts:post_create'), follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/create/')

    def test_create_page_is_available_for_user(self):
        """Check that post create page is available for user"""
        response = self.auth_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_guest_user_cannot_comment(self):
        """Check that guest user can't comment posts"""
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_user_can_comment(self):
        """Check that authorized user can comment posts"""
        response = self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': '1'}))

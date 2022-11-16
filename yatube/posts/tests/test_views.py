from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        user2 = User.objects.create_user(username='testuser2')
        author_user = User.objects.create_user(username='authoruser')
        group_empty = Group.objects.create(
            title='Test group',
            slug='test-empty-slug',
            description='Test description for empty group',
        )
        group_with_post = Group.objects.create(
            title='Test group for posting',
            slug='test-slug',
            description='Test description for group with posts',
        )
        post = Post.objects.create(
            text='Test text',
            author=author_user,
        )
        post_in_group = Post.objects.create(
            text='Test text for group post',
            author=author_user,
            group=group_with_post,
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
            reverse('posts:profile', kwargs={'username': 'testuser'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}):
                'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }

    def test_views_use_correct_template(self):
        """Check that correct templates are used."""
        for address, template in self.urls_templates.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_context(self):
        response = self.auth_client.get(reverse('posts:index'))
        post = response.context['page_obj'][1]
        post_in_group = response.context['page_obj'][0]
        self.assertEqual(post.text, 'Test text')
        self.assertEqual(post.author, User.objects.get(username='authoruser'))
        self.assertEqual(post_in_group.group,
                         Group.objects.get(title='Test group for posting'))

    def test_single_post_page_correct_context(self):
        response = self.auth_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        self.assertEqual(response.context['post'], Post.objects.get(id=1))
        self.assertEqual(response.context['author'],
                         User.objects.get(username='authoruser'))
        self.assertEqual(response.context['posts_count'], 2)

    def test_group_page_correct_context(self):
        response = self.auth_client.get(reverse('posts:group_list',
                                                kwargs={'slug': 'test-slug'}))
        post_in_group = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(post_in_group, Post.objects.get(id=2))
        self.assertEqual(group,
                         Group.objects.get(title='Test group for posting'))

    def test_profile_page_correct_context(self):
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': 'authoruser'}))
        post = response.context['page_obj'][1]
        post_with_group = response.context['page_obj'][0]
        full_name = response.context['full_name']
        posts_count = response.context['posts_count']
        self.assertEqual(post, Post.objects.get(id=1))
        self.assertEqual(post_with_group, Post.objects.get(id=2))
        author = User.objects.get(username='authoruser')
        author_full_name = f'{author.first_name} {author.last_name}'
        self.assertEqual(full_name, author_full_name)
        self.assertEqual(posts_count, 2)

    def test_create_post_page_correct_context(self):
        response = self.auth_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_correct_context(self):
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        post = response.context['post']
        self.assertEqual(post, Post.objects.get(id=1))

    def test_post_is_in_one_group(self):
        response = self.auth_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-empty-slug'}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_cache_index_page(self):
        response = self.auth_client.get(reverse('posts:index'))
        author_user = User.objects.get(username='authoruser')
        Post.objects.create(text='test cache', author=author_user)
        self.assertNotContains(response, 'test cache')
        cache.clear()
        response = self.auth_client.get(reverse('posts:index'))
        self.assertContains(response, 'test cache')

    def test_auth_user_can_follow_unfollow(self):
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': 'authoruser'}))
        self.assertFalse(response.context['following'])
        self.auth_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'authoruser'})
        )
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': 'authoruser'}))
        self.assertTrue(response.context['following'])
        self.auth_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': 'authoruser'})
        )
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': 'authoruser'}))
        self.assertFalse(response.context['following'])

    def test_following_page(self):
        self.auth_client2 = Client()
        self.auth_client2.force_login(User.objects.get(username='testuser2'))
        self.auth_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'authoruser'})
        )
        response = self.auth_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 2)
        response = self.auth_client2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        author_user = User.objects.create_user(username='authoruser')
        group_with_posts = Group.objects.create(
            title='Test group for posting',
            slug='test-slug',
            description='Test description for group with posts',
        )
        for i in range(17):
            if i < 13:
                post_in_group = Post.objects.create(
                    text='Test text for group post',
                    author=author_user,
                    group=group_with_posts,
                )
            else:
                post = Post.objects.create(
                    text='Test text',
                    author=user,
                )

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_seven_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 7)

    def test_group_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:group_list',
                                                 kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_user_first_page_contains_ten_records(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'authoruser'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_user_second_page_contains_three_records(self):
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'authoruser'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

import shutil
import tempfile

from posts.models import Post
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        post = Post.objects.create(text='Post to comment',
                                   author=user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(User.objects.get(username='testuser'))

    def test_create_post_form(self):
        """Valid form create post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text',
            'image': uploaded,
        }
        response = self.auth_client.post(reverse('posts:post_create'),
                                         data=form_data,
                                         follow=True)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'testuser'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='Test text',
                                            image='posts/small.gif').exists())

    def test_edit_post_form(self):
        """Valid form edits post."""
        self.assertFalse(
            Post.objects.filter(text='Test text', ).exists())
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text',
            'image': uploaded,
        }
        self.auth_client.post(reverse('posts:post_create'),
                              data=form_data,
                              follow=True)
        self.assertTrue(Post.objects.filter(text='Test text',
                                            image='posts/small1.gif').exists())
        posts_count = Post.objects.count()
        post_id = Post.objects.get(text='Test text').id
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        edited_data = {
            'text': 'Edited test text',
            'image': uploaded,
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=edited_data,
            follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': post_id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(text='Edited test text',
                                image='posts/small2.gif').exists())
        self.assertFalse(
            Post.objects.filter(text='Test text', ).exists())

    def test_comment_post_form(self):
        """Valid comment is posted on page with the post"""
        comment_data = {
            'text': 'Comment text'
        }
        post = Post.objects.get(text='Post to comment')
        comments_count = post.comments.count()
        self.assertFalse(post.comments.filter(text='Comment text').exists())
        self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=comment_data,
            follow=True)
        self.assertEqual(post.comments.count(), comments_count + 1)
        self.assertTrue(post.comments.filter(text='Comment text').exists())

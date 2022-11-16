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
            title='Group'*15,
            description='Test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text for a test post that exceed 15 symbols',
        )

    def test_models_have_correct_object_names(self):
        """Check that __str__ of models works."""
        group = PostModelTest.group
        post = PostModelTest.post
        expected_group_name = group.title
        expected_post_name = post.text[:15]
        self.assertEqual(expected_group_name, str(group))
        self.assertEqual(expected_post_name, str(post))

    def test_group_title_convert_to_slug(self):
        """Title is converted into slug."""
        group = PostModelTest.group
        slug = group.slug
        self.assertEqual(slug, 'group' * 10)

    def test_group_slug_max_length_not_exceed(self):
        """Slug that is too long is sliced and do not exceed max_length."""
        group = PostModelTest.group
        max_length_slug = group._meta.get_field('slug').max_length
        length_slug = len(group.slug)
        self.assertEqual(max_length_slug, length_slug)

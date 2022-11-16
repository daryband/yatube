from django.db import models
from django.contrib.auth import get_user_model
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Group title',
                             max_length=100,
                             help_text='Title of the group, 100 characters max'
                             )
    slug = models.SlugField(verbose_name='Group slug',
                            max_length=50,
                            unique=True,
                            blank=True,
                            help_text=('Slug of the group, will be used in '
                                       'URL. Use latin characters, numbers, '
                                       'hyphen and underscores only.')
                            )
    description = models.TextField(verbose_name='Group description',
                                   max_length=300,
                                   help_text=('Group description, 300 '
                                              'characters max')
                                   )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)


class Post(models.Model):
    text = models.TextField(verbose_name='Text',
                            help_text='Write post here',
                            )
    pub_date = models.DateTimeField(verbose_name='Publication date',
                                    auto_now_add=True,
                                    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Author',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Group',
        help_text='Related group',
    )

    image = models.ImageField(verbose_name='Image',
                              upload_to='posts/',
                              blank=True
                              )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Post',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Author'
                               )
    text = models.TextField(verbose_name='Comment text',
                            help_text='Write comment here',
                            )
    created = models.DateTimeField(verbose_name='Comment date',
                                   auto_now_add=True,
                                   )


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Author'
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Author'
                               )

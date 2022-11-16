# Generated by Django 2.2.19 on 2022-07-18 15:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220616_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Group description, 300 characters max', max_length=300, verbose_name='Group description'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(blank=True, help_text='Slug of the group, will be used in URL. Use latin characters, numbers, hyphen and underscores only.', unique=True, verbose_name='Group slug'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Title of the group, 100 characters max', max_length=100, verbose_name='Group title'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Related group', null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.Group', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Publication date'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Write post here', verbose_name='Text'),
        ),
    ]

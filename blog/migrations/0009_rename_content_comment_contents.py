# Generated by Django 5.0.2 on 2024-02-12 02:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_post_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='content',
            new_name='contents',
        ),
    ]

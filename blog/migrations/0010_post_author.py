# Generated by Django 5.0.2 on 2024-02-24 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_rename_content_comment_contents'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.CharField(default='Sensei Panda', max_length=255),
        ),
    ]
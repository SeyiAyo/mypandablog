# Generated by Django 5.0.2 on 2024-07-02 16:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_alter_post_intro'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='sentiment',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended_from', to='blog.post')),
                ('recommended_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recommended_to', to='blog.post')),
            ],
            options={
                'unique_together': {('post', 'recommended_post')},
            },
        ),
    ]

# Generated by Django 3.2.23 on 2024-03-08 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_auto_20240308_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, default=True, to='course.Tag'),
        ),
    ]
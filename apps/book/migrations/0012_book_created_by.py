# Generated by Django 3.2.11 on 2022-02-06 05:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('book', '0011_merge_0009_auto_20220128_1303_0010_alter_book_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='book_creator', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]

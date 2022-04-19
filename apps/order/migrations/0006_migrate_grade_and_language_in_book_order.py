# Generated by Django 3.1.5 on 2021-10-08 05:38

from django.db import migrations


def migrate_book_orders(apps, schema_editor):

    # New model
    Book = apps.get_model("book", "Book")
    BookOrder = apps.get_model("order", "BookOrder")
    for book_order in BookOrder.objects.all():
        book_order.language = book_order.book.language
        book_order.grade = book_order.book.grade
        book_order.save()

class Migration(migrations.Migration):

    dependencies = [("order", "0005_auto_20220419_1228")]

    operations = [migrations.RunPython(migrate_book_orders)]

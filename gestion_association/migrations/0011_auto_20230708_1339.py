# Generated by Django 3.1.4 on 2023-07-08 13:39

from django.db import migrations


def migrate_preference(apps, schema_editor):
    Famille = apps.get_model("gestion_association", "Famille")
    for row in Famille.objects.all():
        row.chats = row.preference.chats
        row.congeneres = row.preference.congeneres
        row.save(update_fields=["chats","congeneres"])

class Migration(migrations.Migration):

    dependencies = [
        ('gestion_association', '0010_auto_20230708_1337'),
    ]

    operations = [
        migrations.RunPython(migrate_preference),
    ]
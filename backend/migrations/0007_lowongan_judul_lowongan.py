# Generated by Django 5.2.1 on 2025-05-30 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_kampus'),
    ]

    operations = [
        migrations.AddField(
            model_name='lowongan',
            name='judul_lowongan',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

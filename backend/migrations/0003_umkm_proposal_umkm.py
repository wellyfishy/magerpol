# Generated by Django 5.2.1 on 2025-05-30 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_umkm_has_sent_umkm_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='umkm',
            name='proposal_umkm',
            field=models.FileField(blank=True, null=True, upload_to='proposal/'),
        ),
    ]

# Generated by Django 4.1.12 on 2024-04-03 10:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0011_alter_admin_escola_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Professor_User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ID_Professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.professor')),
                ('professor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

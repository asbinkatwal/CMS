# Generated by Django 5.2.1 on 2025-05-08 10:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0003_rename_smax_capacity_menu_max_capacity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='max_capacity',
            field=models.PositiveIntegerField(),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('will_attend', models.BooleanField()),
                ('voted_at', models.DateTimeField(auto_now_add=True)),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canteen.menu')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'menu')},
            },
        ),
    ]

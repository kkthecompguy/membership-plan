# Generated by Django 3.0.5 on 2020-04-05 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='membership_type',
            field=models.CharField(choices=[('Enterprize', 'Enterprize'), ('Professional', 'Professional'), ('Free', 'Free')], default='Free', max_length=30),
        ),
    ]

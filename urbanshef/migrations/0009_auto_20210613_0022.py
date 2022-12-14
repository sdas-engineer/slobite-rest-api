# Generated by Django 3.1.7 on 2021-06-12 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('urbanshef', '0008_auto_20210524_0100'),
    ]

    operations = [
        migrations.AddField(
            model_name='chef',
            name='delivery_time',
            field=models.CharField(blank=True, choices=[('Pre-order', 'Pre-order'), ('30-60 min', '30-60 min'), ('60-120 min', '60-120 min')], default='Pre-order', max_length=255),
        ),
        migrations.AddField(
            model_name='meal',
            name='diet',
            field=models.CharField(blank=True, choices=[('Vegan', 'Vegan'), ('Vegetarian', 'Vegetarian')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='meal',
            name='spicy',
            field=models.CharField(blank=True, choices=[('Mild', 'Mild'), ('Medium', 'Medium'), ('Hot', 'Hot'), ('Extreme', 'Extreme')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='pre_order',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='meal',
            name='food_type',
            field=models.CharField(choices=[('Appetizer', 'Appetizer'), ('Main', 'Main'), ('Side', 'Side'), ('Dessert', 'Dessert')], default=0, max_length=255),
        ),
    ]

# Generated by Django 5.1.5 on 2025-01-17 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("air_service", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="airplane",
            old_name="name",
            new_name="airplane_name",
        ),
        migrations.RenameField(
            model_name="airplanetype",
            old_name="name",
            new_name="type_name",
        ),
        migrations.RenameField(
            model_name="airport",
            old_name="name",
            new_name="airport_name",
        ),
        migrations.RenameField(
            model_name="city",
            old_name="name",
            new_name="city_name",
        ),
        migrations.RenameField(
            model_name="country",
            old_name="name",
            new_name="country_name",
        ),
        migrations.RenameField(
            model_name="flight",
            old_name="arrival_time",
            new_name="arrival_datetime",
        ),
        migrations.RenameField(
            model_name="flight",
            old_name="departure_time",
            new_name="departure_datetime",
        ),
        migrations.RenameField(
            model_name="order",
            old_name="created_at",
            new_name="order_created_at",
        ),
        migrations.RenameField(
            model_name="ticket",
            old_name="row",
            new_name="seat_number",
        ),
        migrations.RenameField(
            model_name="ticket",
            old_name="seat",
            new_name="seat_row",
        ),
    ]

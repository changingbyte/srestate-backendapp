from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FamilyMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
                ("mobile", models.CharField(max_length=10, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="WhatsappEstateMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("raw_body", models.TextField()),
                ("sender_mobile", models.CharField(db_index=True, max_length=10)),
                ("twilio_sid", models.CharField(blank=True, default="", max_length=64)),
                ("message_kind", models.CharField(default="save", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("estate_status", models.CharField(blank=True, db_index=True, default="", max_length=32)),
                ("estate_type", models.CharField(blank=True, db_index=True, default="", max_length=32)),
                ("area", models.CharField(blank=True, db_index=True, default="", max_length=128)),
                ("budget", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("number_of_bedrooms", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("apartment", models.CharField(blank=True, default="", max_length=128)),
                ("broker_mobile", models.CharField(blank=True, default="", max_length=10)),
                ("extracted_json", models.JSONField(default=dict)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
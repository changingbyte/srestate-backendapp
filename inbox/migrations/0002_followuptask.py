import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FollowUpTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("owner_mobile", models.CharField(db_index=True, max_length=10)),
                ("note", models.TextField()),
                ("due_at", models.DateTimeField(db_index=True)),
                ("status", models.CharField(db_index=True, default="pending", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reminded_at", models.DateTimeField(blank=True, null=True)),
                (
                    "listing",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="followups",
                        to="inbox.whatsappestatemessage",
                    ),
                ),
            ],
            options={
                "ordering": ("due_at",),
            },
        ),
    ]
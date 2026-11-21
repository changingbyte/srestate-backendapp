import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0003_leadrecord_followuptask_lead"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConversationState",
            fields=[
                ("mobile", models.CharField(max_length=10, primary_key=True, serialize=False)),
                ("last_lead_id", models.PositiveIntegerField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="LeadEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(db_index=True, max_length=32)),
                ("actor_mobile", models.CharField(blank=True, default="", max_length=10)),
                ("detail", models.CharField(blank=True, default="", max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="inbox.leadrecord",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0002_followuptask"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeadRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("shared_by_mobile", models.CharField(db_index=True, max_length=10)),
                ("assignee_mobile", models.CharField(db_index=True, max_length=10)),
                ("contact_mobile", models.CharField(blank=True, db_index=True, default="", max_length=10)),
                ("summary", models.CharField(blank=True, default="", max_length=255)),
                ("status", models.CharField(db_index=True, default="open", max_length=16)),
                ("next_action_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("action_note", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("last_nudge", models.CharField(blank=True, default="", max_length=16)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leads",
                        to="inbox.whatsappestatemessage",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddField(
            model_name="followuptask",
            name="lead",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="followups",
                to="inbox.leadrecord",
            ),
        ),
    ]
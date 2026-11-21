from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inbox", "0004_conversationstate_leadevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="familymember",
            name="role",
            field=models.CharField(
                choices=[
                    ("super_admin", "Super admin"),
                    ("operator", "Operator"),
                    ("tester", "Tester"),
                ],
                default="tester",
                max_length=16,
            ),
        ),
    ]
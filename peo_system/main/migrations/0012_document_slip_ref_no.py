from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_document_contractor_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="slip_ref_no",
            field=models.CharField(blank=True, max_length=80),
        ),
    ]

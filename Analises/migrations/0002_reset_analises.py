from django.db import migrations

def reset_analises(apps, schema_editor):
    Analise = apps.get_model('Analises', 'Analise')
    Analise.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('Analises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reset_analises),
    ]

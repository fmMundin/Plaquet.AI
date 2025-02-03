# Generated by Django 5.1.5 on 2025-02-03 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Analise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('paciente', models.CharField(max_length=200)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_analise', models.DateTimeField(blank=True, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='analises/')),
                ('img_resultado', models.ImageField(blank=True, null=True, upload_to='resultados/')),
                ('n_plaquetas', models.IntegerField(blank=True, null=True)),
                ('n_celulas_brancas', models.IntegerField(blank=True, null=True)),
                ('n_celulas_vermelhas', models.IntegerField(blank=True, null=True)),
                ('acuracia', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('processando', 'Processando'), ('concluido', 'Concluído'), ('erro', 'Erro')], default='pendente', max_length=20)),
                ('erro_msg', models.TextField(blank=True, null=True)),
                ('tempo_processamento', models.FloatField(blank=True, null=True)),
                ('ultima_modificacao', models.DateTimeField(blank=True, null=True)),
                ('modificado_por', models.CharField(blank=True, max_length=100, null=True)),
                ('historico_modificacoes', models.TextField(blank=True, null=True)),
                ('detalhes_processamento', models.JSONField(blank=True, null=True)),
                ('confianca_deteccao', models.FloatField(blank=True, null=True)),
                ('metadados_modelo', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Análise',
                'verbose_name_plural': 'Análises',
                'ordering': ['-data_criacao'],
            },
        ),
    ]

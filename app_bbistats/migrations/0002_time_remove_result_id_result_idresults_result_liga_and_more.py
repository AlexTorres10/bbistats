# Generated by Django 4.2.5 on 2023-10-04 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bbistats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Time',
            fields=[
                ('idtimes', models.AutoField(primary_key=True, serialize=False)),
                ('time', models.CharField(max_length=100)),
                ('divisao', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'times',
                'ordering': ['idtimes'],
            },
        ),
        migrations.RemoveField(
            model_name='result',
            name='id',
        ),
        migrations.AddField(
            model_name='result',
            name='idresults',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='liga',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterModelTable(
            name='result',
            table='results',
        ),
    ]

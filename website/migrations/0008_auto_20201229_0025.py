# Generated by Django 3.1.4 on 2020-12-28 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_remove_achat_qtachat'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligneachat',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.ingredient'),
        ),
        migrations.AlterField(
            model_name='ligneachat',
            name='achat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.achat'),
        ),
    ]

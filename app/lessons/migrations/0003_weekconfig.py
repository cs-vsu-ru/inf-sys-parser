from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_alter_lesson_groups_alter_lesson_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeekConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_date', models.DateField()),
                ('is_denominator', models.BooleanField()),
            ],
            options={
                'verbose_name': 'week config',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]

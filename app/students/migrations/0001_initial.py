from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('full_name', models.TextField(db_index=True)),
                ('login', models.TextField(unique=True, db_index=True)),
                ('email', models.EmailField()),
                ('course', models.PositiveSmallIntegerField()),
                ('group', models.TextField(db_index=True)),
                ('subgroup', models.TextField()),
                ('education_profile', models.TextField()),
                (
                    'activity_type',
                    models.TextField(
                        blank=True,
                        null=True,
                        choices=[
                            ('student', 'студент'),
                            ('master', 'магистрант'),
                            ('phd', 'аспирант'),
                        ],
                    ),
                ),
            ],
            options={
                'ordering': ['login'],
                'abstract': False,
            },
        ),
    ]

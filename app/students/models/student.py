from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.TextField(db_column='first_name', blank=True, null=True)
    last_name = models.TextField(db_column='last_name', blank=True, null=True)
    login = models.TextField(unique=True)
    password = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Student(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        db_column='user_id',
        on_delete=models.DO_NOTHING,
        related_name='students',
    )

    patronymic = models.TextField(blank=True, null=True)
    course = models.IntegerField(blank=True, null=True)

    group = models.TextField(
        db_column='group_nm',
        blank=True,
        null=True,
    )

    start_year = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)

    supervisor = models.ForeignKey(
        User,
        db_column='supervisor',
        on_delete=models.DO_NOTHING,
        related_name='supervised_students',
        blank=True,
        null=True,
    )

    image_url = models.TextField(db_column='image_url', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'
        ordering = ['user__login']

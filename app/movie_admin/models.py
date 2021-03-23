import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class Genre(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('название'), max_length=255, unique=True)
    description = models.TextField(_('описание'), blank=True, default='')

    class Meta:
        ordering = ['-id']
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name


class Person(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_('имя'), max_length=255)
    last_name = models.CharField(_('фамилия'), max_length=255, blank=False)
    birth_date = models.DateField(_('дата рождения'), null=True)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['first_name', 'last_name', 'birth_date'], name='person_name_uq')
        ]
        verbose_name = _('человек')
        verbose_name_plural = _('люди')

    def _get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self._get_full_name()

    full_name = property(_get_full_name)


class PersonRoleType(models.TextChoices):
    ACTOR = 'actor', _('актёр')
    WRITER = 'writer', _('сценарист')
    DIRECTOR = 'director', _('режиссёр')


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')
    SERIAL = 'serial', _('сериал')


class Filmwork(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    old_id = models.CharField(_('старый id'), max_length=27, unique=True, default='')
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True, default='')
    creation_date = models.DateField(_('дата создания фильма'), blank=True)
    restricted = models.PositiveIntegerField(_('возрастной ценз'), validators=[
        MaxValueValidator(21)], blank=True, null=True)
    file_path = models.FileField(
        _('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[
                               MinValueValidator(0), MaxValueValidator(100)], blank=True, null=True)
    type = models.CharField(_('тип'), max_length=20,
                            choices=FilmworkType.choices)
    genres = models.ManyToManyField(Genre)
    persons = models.ManyToManyField(
        Person,
        through='FilmworkPerson'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title


class FilmworkPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filmwork = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name=_('персона'))
    role = models.CharField(_('роль'), max_length=20,
                            choices=PersonRoleType.choices)

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['filmwork', 'person', 'role'], name='person_film_work_uq')
        ]
        verbose_name = _('участники кинопроизведения')
        verbose_name_plural = _('участники кинопроизведений')

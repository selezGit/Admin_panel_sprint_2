from django.contrib import admin
from .models import Filmwork, Genre, Person, FilmworkPerson


class PersonRoleInline(admin.TabularInline):
    fields = (
        'person', 'role'
    )
    model = FilmworkPerson
    extra = 0
    ordering = ('person',)


class FilmPersonInline(admin.TabularInline):
    model = FilmworkPerson
    extra = 0


@admin.register(Genre)
class FilmworkAdminGenre(admin.ModelAdmin):
    fields = (
        'name', 'description'
    )
    list_display = ('name', )


@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    fields = (
        'first_name', 'last_name', 'birth_date'
    )
    list_display = ('full_name', 'birth_date')
    list_display_links = ('full_name')

    inlines = [
        FilmPersonInline
    ]


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date',
                    'rating', 'created', 'modified')

    list_filter = ('type', 'creation_date')

    ordering = ('title',)

    filter_horizontal = ('genres',)

    fieldsets = (
        (None, {
            'fields': (
                'title', 'type', 'description', 'creation_date',
                'file_path')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (('rating', 'restricted'), 'genres'),
        }),
    )

    search_fields = ('title', 'description', 'id')

    inlines = [
        PersonRoleInline
    ]

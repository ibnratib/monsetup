from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    City = apps.get_model('core', 'City')
    for city in City.objects.all():
        if not city.slug:
            base_slug = slugify(city.name)
            slug = base_slug
            counter = 1
            while City.objects.filter(slug=slug).exclude(pk=city.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            city.slug = slug
            city.save(update_fields=['slug'])


def reverse_slugs(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_slug_to_city'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_slugs),
    ]

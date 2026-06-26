import io

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image


def compress_image(image_field):
    """
    Compresse une image si elle dépasse MAX_IMAGE_SIZE_MB.
    Redimensionne à max 1920px côté le plus long et sauvegarde en JPEG qualité 85%.
    Fonctionne avec tout backend de stockage (local ou cloud).
    """
    max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024

    if not image_field or not image_field.name:
        return

    if image_field.size <= max_size_bytes:
        return

    image_field.open('rb')
    with Image.open(image_field) as img:
        img = img.convert('RGB')

        max_dimension = 1920
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, 'JPEG', quality=85)
        buffer.seek(0)

    image_field.save(image_field.name, ContentFile(buffer.read()), save=False)
    image_field.close()

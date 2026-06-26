from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Nom")
    slug = models.SlugField(unique=True, max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Catégorie parente",
    )
    icon = models.CharField(max_length=100, blank=True, verbose_name="Icône")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent and self.parent.parent is not None:
            raise ValidationError(
                "Une catégorie ne peut avoir qu'un seul niveau de parent."
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        self.full_clean()
        super().save(*args, **kwargs)

    def get_inherited_attributes(self):
        """
        Retourne tous les AttributeDefinition applicables à cette catégorie :
        - Si c'est une sous-catégorie : attributs du parent + attributs propres
        - Si c'est une catégorie racine : uniquement ses attributs propres
        - Pas de doublons, triés par `order`
        """
        if self.parent is not None:
            parent_attrs = list(self.parent.attributes.all())
            own_attrs = list(self.attributes.all())
            parent_names = {a.name for a in parent_attrs}
            merged = parent_attrs + [a for a in own_attrs if a.name not in parent_names]
            return sorted(merged, key=lambda a: a.order)
        return list(self.attributes.order_by('order'))


class AttributeDefinition(TimeStampedModel):
    ATTRIBUTE_TYPES = [
        ('INT', 'Entier'),
        ('DECIMAL', 'Décimal'),
        ('CHOICE', 'Choix unique'),
        ('MULTI_CHOICE', 'Choix multiple'),
        ('BOOLEAN', 'Booléen'),
        ('TEXT_SHORT', 'Texte court'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='attributes',
        verbose_name="Catégorie",
    )
    name = models.CharField(max_length=255, verbose_name="Nom")
    label_fr = models.CharField(max_length=255, verbose_name="Label (FR)")
    attribute_type = models.CharField(
        max_length=20,
        choices=ATTRIBUTE_TYPES,
        verbose_name="Type",
    )
    required = models.BooleanField(default=False, verbose_name="Obligatoire")
    filterable = models.BooleanField(default=False, verbose_name="Filtrable")
    min_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valeur min",
    )
    max_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valeur max",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Unité")
    depends_on_choice = models.ForeignKey(
        'AttributeChoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dependent_attributes',
        verbose_name="Dépend du choix",
        help_text="Si renseigné, cet attribut n'apparaît que quand ce choix est sélectionné",
    )

    class Meta:
        verbose_name = "Définition d'attribut"
        verbose_name_plural = "Définitions d'attributs"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"

    def clean(self):
        if self.attribute_type not in ('INT', 'DECIMAL'):
            if self.min_value is not None or self.max_value is not None:
                raise ValidationError(
                    "min_value et max_value ne sont pertinents que pour les types INT et DECIMAL."
                )
        if self.depends_on_choice is not None:
            parent_attr = self.depends_on_choice.attribute
            if parent_attr.category != self.category and (
                self.category.parent is None or parent_attr.category != self.category.parent
            ):
                raise ValidationError(
                    "L'attribut parent doit appartenir à la même catégorie ou à la catégorie parente."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AttributeChoice(TimeStampedModel):
    attribute = models.ForeignKey(
        AttributeDefinition,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Attribut",
    )
    value = models.CharField(max_length=255, verbose_name="Valeur")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Choix d'attribut"
        verbose_name_plural = "Choix d'attributs"
        ordering = ['order']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    def clean(self):
        if self.attribute.attribute_type not in ('CHOICE', 'MULTI_CHOICE'):
            raise ValidationError(
                "Les choix ne sont autorisés que pour les types CHOICE et MULTI_CHOICE."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

from django import template

register = template.Library()


@register.filter
def format_price(value):
    """Formate un prix en DH avec séparateur de milliers."""
    try:
        formatted = f"{int(value):,}".replace(",", " ")
        return f"{formatted} DH"
    except (ValueError, TypeError):
        return f"{value} DH"


@register.filter
def time_since_fr(value):
    """Affiche le temps écoulé en français."""
    from django.utils import timezone

    try:
        now = timezone.now()
        diff = now - value

        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"Il y a {minutes} min" if minutes > 0 else "À l'instant"
            return f"Il y a {hours}h"
        elif diff.days == 1:
            return "Hier"
        elif diff.days < 7:
            return f"Il y a {diff.days} jours"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"Il y a {weeks} sem."
        else:
            return value.strftime("%d %b %Y")
    except Exception:
        return str(value)

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_school_custom_css_school_nav_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='custom_css',
        ),
        migrations.RemoveField(
            model_name='school',
            name='nav_order',
        ),
        migrations.RemoveField(
            model_name='school',
            name='sidebar_width',
        ),
    ]


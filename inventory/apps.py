from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    # Fix for environments (e.g. PythonAnywhere) where the same app folder can be
    # discovered via multiple paths (e.g. './inventory' vs 'inventory'), causing:
    # "multiple filesystem locations ... you must configure this app with an AppConfig
    # subclass with a 'path' class attribute."
    #
    # Using an absolute path prevents Django from treating the module as a namespace
    # package and eliminates the multi-location error.
    import os
    path = os.path.dirname(os.path.abspath(__file__))


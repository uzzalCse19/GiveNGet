# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    
    def ready(self):
        # Import signals to ensure they are registered
        try:
            import users.signals
            print("✅ Signals imported successfully")
        except Exception as e:
            print(f"❌ Error importing signals: {e}")
from database.settings_repository import SettingsRepository

settings = SettingsRepository()

settings.update_setting("short_black_white", 2.00)
settings.update_setting("short_color", 4.00)

print("Short paper prices updated successfully!")

from database.settings_repository import SettingsRepository

settings = SettingsRepository()

settings.update_setting("short_black_white", 2.00)
settings.update_setting("short_color", 4.00)

settings.update_setting("a4_black_white", 2.00)
settings.update_setting("a4_color", 4.00)

settings.update_setting("long_black_white", 3.00)
settings.update_setting("long_color", 6.00)

settings.update_setting("handling_fee", 2.50)
settings.update_setting("delivery_fee", 2.50)
settings.update_setting("pickup_fee", 0.00)

print("PasaPrint final prices updated successfully!")

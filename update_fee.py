from database.settings_repository import SettingsRepository

settings = SettingsRepository()
settings.update_setting("delivery_fee", 2.50)

print("Delivery fee successfully updated to ₱2.50!")

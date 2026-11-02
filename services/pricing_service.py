
from decimal import Decimal, InvalidOperation

from database.settings_repository import SettingsRepository


class PricingService:
    def __init__(self):
        self.settings = SettingsRepository()

    def get_price(self, color_mode):
        setting_keys = {
            "black_white": "black_white_price",
            "color": "color_price",
        }

        if color_mode not in setting_keys:
            raise ValueError("Invalid printing color mode.")

        value = self.settings.get_setting(setting_keys[color_mode])

        if value is None:
            raise ValueError("Printing price is not configured.")

        return self._to_money(value)

    def get_delivery_fee(self, fulfillment_method):
        if fulfillment_method == "pickup":
            value = self.settings.get_setting("pickup_fee", "0.00")
        elif fulfillment_method == "delivery":
            value = self.settings.get_setting("delivery_fee")
        else:
            raise ValueError("Invalid fulfillment method.")

        if value is None:
            raise ValueError("Fulfillment fee is not configured.")

        return self._to_money(value)

    def calculate_total(
        self,
        total_pages,
        copies,
        color_mode,
        fulfillment_method,
    ):
        if not isinstance(total_pages, int) or total_pages <= 0:
            raise ValueError("Total pages must be a positive integer.")

        if not isinstance(copies, int) or copies <= 0:
            raise ValueError("Copies must be a positive integer.")

        price_per_page = self.get_price(color_mode)
        delivery_fee = self.get_delivery_fee(fulfillment_method)

        printing_cost = price_per_page * total_pages * copies
        total_cost = printing_cost + delivery_fee

        return {
            "price_per_page": price_per_page,
            "printing_cost": printing_cost,
            "delivery_fee": delivery_fee,
            "total_cost": total_cost,
        }

    def _to_money(self, value):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid price configuration.")

        if not amount.is_finite() or amount < 0:
            raise ValueError("Price must be a valid non-negative amount.")

        return amount.quantize(Decimal("0.01"))

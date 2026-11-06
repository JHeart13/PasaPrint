
class Order:
    def __init__(
        self,
        order_number,
        customer_id,
        total_pages,
        copies,
        color_mode,
        paper_size="A4",
        print_sides="single",
        fulfillment_method="pickup",
    ):
        if total_pages <= 0:
            raise ValueError("Total pages must be greater than zero.")

        if copies <= 0:
            raise ValueError("Copies must be greater than zero.")

        if color_mode not in ("black_white", "color"):
            raise ValueError("Invalid color mode.")

        if print_sides not in ("single", "double"):
            raise ValueError("Invalid printing side option.")

        if fulfillment_method not in ("pickup", "delivery"):
            raise ValueError("Invalid fulfillment method.")

        self.order_number = order_number
        self.customer_id = customer_id
        self.total_pages = total_pages
        self.copies = copies
        self.color_mode = color_mode
        self.paper_size = paper_size
        self.print_sides = print_sides
        self.fulfillment_method = fulfillment_method

    def calculate_printing_cost(self, price_per_page):
        if price_per_page < 0:
            raise ValueError("Price cannot be negative.")

        return self.total_pages * self.copies * price_per_page

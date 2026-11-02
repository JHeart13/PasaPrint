
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    student_number TEXT UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (
        role IN ('customer', 'staff', 'manager')
    ),
    account_status TEXT NOT NULL DEFAULT 'active'
        CHECK (account_status IN ('pending', 'active', 'inactive')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL,
    assigned_staff_id INTEGER,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN (
            'pending',
            'confirmed',
            'printing',
            'awaiting_review',
            'correction_requested',
            'ready_for_pickup',
            'out_for_delivery',
            'completed',
            'rejected',
            'cancelled'
        )),
    fulfillment_method TEXT NOT NULL
        CHECK (fulfillment_method IN ('pickup', 'delivery')),
    campus TEXT,
    pickup_location TEXT,
    building TEXT,
    floor TEXT,
    room TEXT,
    delivery_notes TEXT,
    color_mode TEXT NOT NULL
        CHECK (color_mode IN ('black_white', 'color')),
    paper_size TEXT NOT NULL DEFAULT 'A4',
    print_sides TEXT NOT NULL DEFAULT 'single'
        CHECK (print_sides IN ('single', 'double')),
    copies INTEGER NOT NULL CHECK (copies > 0),
    total_pages INTEGER NOT NULL CHECK (total_pages > 0),
    price_per_page REAL NOT NULL CHECK (price_per_page >= 0),
    printing_cost REAL NOT NULL CHECK (printing_cost >= 0),
    delivery_fee REAL NOT NULL DEFAULT 0 CHECK (delivery_fee >= 0),
    total_cost REAL NOT NULL CHECK (total_cost >= 0),
    customer_notes TEXT,
    rejection_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_staff_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS order_files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    uploaded_by INTEGER NOT NULL,
    file_type TEXT NOT NULL
        CHECK (file_type IN ('document', 'proof')),
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    page_count INTEGER,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS order_status_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    changed_by INTEGER,
    old_status TEXT,
    new_status TEXT NOT NULL,
    notes TEXT,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS staff_authorization_codes (
    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    intended_email TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_customer
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_status
ON orders(status);

CREATE INDEX IF NOT EXISTS idx_order_files_order
ON order_files(order_id);

CREATE INDEX IF NOT EXISTS idx_order_history_order
ON order_status_history(order_id);


CREATE TABLE IF NOT EXISTS password_reset_codes (
    reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    used_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_password_reset_email
ON password_reset_codes(email);

# FreshWave Laundry System

FreshWave Laundry System is a Django-based laundry shop management system designed for staff/admin operations. It manages customers, laundry orders, services, payments, notifications, and order tracking in one clean web interface.

The current project uses a modular Django structure with a `config` project folder and a main app located at `apps/laundry`.

---

## ✅ Current Features

### Dashboard
- Shows total customers, active orders, completed orders, and revenue summary.
- Displays recent orders and operational statistics.
- Uses a clean dashboard layout with reusable CSS files.

### Customer Management
- Add, edit, view, search, and delete customers.
- Auto-generates a unique `customer_number` for each customer.
- Stores customer name, phone number, address, and email.
- Shows customer order history and active order count.

### Order Management
- Create laundry orders for existing customers.
- Auto-generates order numbers.
- Auto-generates tracking IDs in this format: `FW-XXXXXXXX`.
- Supports multiple services per order through `OrderItem`.
- Tracks weight in kilograms.
- Supports notes and pickup date.
- Search orders by customer name or order number.
- Filter orders by status.

### Order Status Flow
The system currently supports these order statuses:

1. Received
2. Washing
3. Drying
4. Folding
5. Ready for Pickup
6. Completed
7. Cancelled

### Payment Management
- Record payments per order.
- Supports partial and full payment tracking.
- Calculates:
  - Total amount
  - Amount paid
  - Remaining balance
  - Paid/unpaid state
- Payment methods supported:
  - Cash
  - GCash
  - Maya
- Payment statuses supported:
  - Paid
  - Partial
  - Pending
  - Refunded

### Services Management
- Manage laundry services such as washing, drying, folding, ironing, and bleaching.
- Each service has a name, price, description, and active/inactive status.
- Service prices are used when calculating order totals.

### Notifications
- In-app notifications for order and payment events.
- Mark one notification as read.
- Mark all notifications as read.
- Delete one notification.
- Delete all notifications.

### Email and SMS Notifications
- Email notifications are sent through Django SMTP settings.
- SMS sending is integrated through UNISMS configuration.
- Customer phone numbers are normalized for Philippine numbers.
- Notification events include:
  - Order received
  - Order ready for pickup
  - Order completed
  - Payment received

### API Support
The project includes Django REST Framework endpoints for customers, orders, payments, services, and dashboard stats.

---

## 🧱 Tech Stack

| Area | Technology |
|---|---|
| Backend | Python, Django 6.0.3 |
| API | Django REST Framework |
| Database | SQLite for local development |
| Frontend | HTML, CSS, Bootstrap-style components, JavaScript |
| Email | Django SMTP Email Backend |
| SMS | UNISMS API integration |
| Timezone | Asia/Manila |

---

## 📁 Current Project Structure

```text
freshwave_laundry_system/
├── README.md
├── requirements.txt
├── .gitignore
├── .env                      # local environment variables only; do not commit
├── venv/                     # local virtual environment; do not commit
└── laundry_system/
    ├── manage.py
    ├── db.sqlite3             # local database; do not commit for production
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── scripts/
    │   └── setup_data.py
    └── apps/
        ├── __init__.py
        └── laundry/
            ├── __init__.py
            ├── admin.py
            ├── api_views.py
            ├── apps.py
            ├── context_processors.py
            ├── forms.py
            ├── models.py
            ├── notifications.py
            ├── serializers.py
            ├── urls.py
            ├── migrations/
            ├── selectors/
            │   ├── customer_selectors.py
            │   ├── dashboard_selectors.py
            │   ├── order_selectors.py
            │   └── payment_selectors.py
            ├── services/
            │   ├── dashboard_service.py
            │   ├── notification_service.py
            │   ├── order_service.py
            │   └── payment_service.py
            ├── static/laundry/
            │   ├── IMG/
            │   ├── css/
            │   │   ├── base.css
            │   │   ├── component.css
            │   │   ├── dashboard.css
            │   │   ├── landing.css
            │   │   └── login.css
            │   ├── favicon/
            │   └── js/
            │       ├── landing.js
            │       └── theme.js
            └── templates/laundry/
                ├── base.html
                ├── landing.html
                ├── auth/
                │   └── login.html
                ├── customers/
                ├── dashboard/
                ├── orders/
                ├── payments/
                ├── services/
                └── shared/
```

---

## ⚙️ Local Setup Guide

### 1. Clone or open the project

```bash
cd freshwave_laundry_system
```

### 2. Create and activate a virtual environment

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Do not upload or commit your real `.env` file because it contains private credentials.

### 5. Go to the Django project folder

```bash
cd laundry_system
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Create sample data and admin account

```bash
python scripts/setup_data.py
```

The setup script creates sample services, sample customers, sample orders, and this development admin account:

```text
Username: Freshwave
Password: freshwave7
```

For real deployment, change this password immediately or create a new secure superuser.

### 8. Run the development server

```bash
python manage.py runserver
```

Open the system in your browser:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

---

## 🔐 Authentication

The system uses Django's built-in authentication system.

Important pages require login. The login URL is:

```text
/login/
```

Logout URL:

```text
/logout/
```

To create another admin account:

```bash
python manage.py createsuperuser
```

---

## 🌐 Main Web Routes

| Page | URL |
|---|---|
| Dashboard | `/` |
| Login | `/login/` |
| Logout | `/logout/` |
| Customers | `/customers/` |
| Add Customer | `/customers/new/` |
| Customer Detail | `/customers/<customer_number>/` |
| Edit Customer | `/customers/<customer_number>/edit/` |
| Delete Customer | `/customers/<customer_number>/delete/` |
| Orders | `/orders/` |
| Add Order | `/orders/new/` |
| Order Detail | `/orders/<order_number>/` |
| Delete Order | `/orders/<order_number>/delete/` |
| Payments | `/payments/` |
| Services | `/services/` |
| Django Admin | `/admin/` |

---

## 🔌 API Routes

The project uses Django REST Framework.

| API | URL |
|---|---|
| Customers API | `/api/customers/` |
| Orders API | `/api/orders/` |
| Order Payments API | `/api/orders/<id>/payments/` |
| Payments API | `/api/payments/` |
| Services API | `/api/services/` |
| Dashboard Stats API | `/api/dashboard/` |
| DRF Login/Logout | `/api/auth/` |

Most API endpoints require authentication.

---

## 🧾 Core Models

### Customer
Stores customer details and automatically assigns a customer number.

Main fields:
- `customer_number`
- `name`
- `phone`
- `address`
- `email`
- `created_at`
- `updated_at`

### Service
Stores laundry services and their prices.

Main fields:
- `name`
- `price`
- `description`
- `is_active`

### Order
Stores customer laundry orders.

Main fields:
- `order_number`
- `customer`
- `tracking_id`
- `status`
- `weight_kg`
- `notes`
- `pickup_date`
- `created_at`
- `updated_at`

Computed properties:
- `total_amount`
- `amount_paid`
- `balance`
- `is_paid`
- `status_badge_color`

### OrderItem
Connects an order to one or more selected laundry services.

Main fields:
- `order`
- `service`
- `quantity`

Computed property:
- `subtotal`

### Payment
Stores payment records per order.

Main fields:
- `order`
- `amount`
- `method`
- `status`
- `reference_no`
- `notes`
- `paid_at`

### Notification
Stores in-app notifications.

Main fields:
- `order`
- `title`
- `message`
- `type`
- `is_read`
- `created_at`

### SMSLog
Stores SMS sending logs.

Main fields:
- `phone`
- `message`
- `reference_id`
- `status`
- `response`
- `created_at`

---

## 🧪 Development Commands

Run server:

```bash
python manage.py runserver
```

Make migrations after model changes:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Create admin user:

```bash
python manage.py createsuperuser
```

Open Django shell:

```bash
python manage.py shell
```

Collect static files for deployment:

```bash
python manage.py collectstatic
```

---

## 📱 Accessing the System From Another Device on the Same Wi-Fi

Run the server using:

```bash
python manage.py runserver 0.0.0.0:8000
```

Then update `.env`:

```env
ALLOWED_HOSTS=127.0.0.1,localhost,YOUR_LOCAL_IP
```

Example:

```env
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.10
```

Then open this on your phone browser:

```text
http://YOUR_LOCAL_IP:8000/
```

Your computer and phone must be connected to the same network.

---

## 🧼 Default Services From Setup Script

| Service | Default Price |
|---|---:|
| Washing | ₱25.00/kg |
| Drying | ₱20.00/kg |
| Folding | ₱5.00/kg |
| Ironing | ₱40.00/kg |
| Bleaching | ₱20.00/kg |

You can change services and prices in the database or Django admin.

---

## 🎨 Frontend Organization

CSS files are located in:

```text
apps/laundry/static/laundry/css/
```

Main CSS files:

- `base.css` — global layout, theme variables, typography, sidebar/header styles
- `component.css` — reusable UI components
- `dashboard.css` — dashboard-specific styling
- `landing.css` — landing page styling
- `login.css` — login page styling

JavaScript files are located in:

```text
apps/laundry/static/laundry/js/
```

Main JS files:

- `theme.js`
- `landing.js`

---

## 🔒 Security Notes

Before deploying or submitting the project, check these items:

- Do not commit `.env`.
- Do not commit `venv/`.
- Do not commit `db.sqlite3` if it contains real customer data.
- Change the default setup admin password.
- Set `DEBUG=False` in production.
- Set proper `ALLOWED_HOSTS` in production.
- Use a strong `SECRET_KEY`.
- Use an email app password instead of your real email password.
- Keep API keys private.
- Avoid exposing customer phone numbers, emails, and addresses in public demos.

Recommended `.gitignore` entries:

```gitignore
.env
venv/
__pycache__/
*.pyc
.DS_Store
db.sqlite3
staticfiles/
```

---

## 🚀 Production Notes

For production deployment, consider these improvements:

- Use PostgreSQL instead of SQLite.
- Set `DEBUG=False`.
- Configure secure `ALLOWED_HOSTS`.
- Configure HTTPS.
- Store static files properly using `collectstatic`.
- Use environment variables for all secrets.
- Use a real email sender account.
- Review SMS provider endpoint and error handling.
- Add role-based access control for admin, staff, and customer-facing pages.
- Add automated tests for orders, payments, and notifications.

---

## 🗺️ Suggested Future Improvements

These are recommended next steps for the system:

1. Separate role access for admin, staff, and customer tracking.
2. Add a customer tracking page where users can enter only their tracking number.
3. Add staff-only order processing pages.
4. Add admin-only user and staff management.
5. Improve receipt printing for 80mm thermal printers.
6. Add audit logs for status changes and payments.
7. Add reports for daily, weekly, and monthly revenue.
8. Add tests for payment balance logic.
9. Add better SMS failure logs using `SMSLog`.
10. Move any remaining inline CSS or JavaScript into static files.

---

## 👥 Project Purpose

FreshWave Laundry System is built to help a laundry business manage daily operations more efficiently by centralizing customer records, order tracking, service pricing, payment records, and customer notifications.


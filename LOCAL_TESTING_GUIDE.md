# Local Testing Guide with Demo Data

This guide will help you set up and test the application locally with demo data.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ installed
- Node.js 18+ and npm installed
- PostgreSQL 14+ installed and running
- Stripe account (for test keys)

---

## 📋 Step-by-Step Setup

### Step 1: Clone and Install Dependencies

```bash
# Navigate to project
cd Baking

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (in new terminal)
cd frontend
npm install
```

### Step 2: Set Up PostgreSQL Database

```bash
# Create database
createdb cookie_shop_dev

# Or using psql
psql -U postgres
CREATE DATABASE cookie_shop_dev;
\q
```

### Step 3: Configure Environment Variables

#### Backend Environment (.env)

Create `backend/.env`:

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cookie_shop_dev

# JWT Configuration
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Stripe Configuration (Test Mode)
STRIPE_SECRET_KEY=sk_test_your_stripe_test_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_test_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**Get Stripe Test Keys:**
1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy the **Publishable key** and **Secret key**
3. Add them to your `.env` file

#### Frontend Environment (.env)

Create `frontend/.env`:

```bash
# API Configuration
VITE_API_URL=http://localhost:5000/api/v1

# Stripe Configuration (Test Mode)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_test_publishable_key

# App Configuration
VITE_APP_NAME=Cookie Shop
VITE_APP_URL=http://localhost:5173
```

### Step 4: Initialize Database

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run migrations
flask db upgrade

# Seed demo data
python scripts/seed_demo_data.py
```

When prompted, type `yes` to confirm seeding demo data.

**Expected Output:**
```
============================================================
SEEDING DEMO DATA FOR LOCAL TESTING
============================================================

Creating demo users...
  ✓ Created admin: admin@cookieshop.com (password: admin123)
  ✓ Created customer: customer@example.com (password: customer123)
  ✓ Created customer: jane@example.com (password: jane123)
✓ Created 3 users

Creating categories...
  ✓ Created category: Chocolate Chip
  ✓ Created category: Sugar Cookies
  ✓ Created category: Oatmeal
  ✓ Created category: Special
✓ Created 4 categories

Creating products...
  ✓ Created product: Classic Chocolate Chip ($12.99, Stock: 100)
  ...
✓ Created 10 products

Creating demo orders...
  ✓ Created order: ORD-001 (delivered, $39.97)
  ...
✓ Created 4 orders

============================================================
✓ DEMO DATA SEEDED SUCCESSFULLY!
============================================================
```

### Step 5: Start the Backend Server

```bash
cd backend
source venv/bin/activate  # If not already active

# Run Flask development server
flask run
# Or
python run.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://127.0.0.1:5000
```

### Step 6: Start the Frontend Server

Open a **new terminal**:

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

---

## 🧪 Testing Checklist

### 1. Test Homepage & Product Browsing

**✅ Verify:**
- [ ] Homepage loads at http://localhost:5173
- [ ] Products display on homepage
- [ ] Navigate to Products page
- [ ] Filter by category works
- [ ] Search functionality works
- [ ] Product details page shows correctly

**Demo Products to Check:**
- Classic Chocolate Chip ($12.99) - 100 in stock
- Double Chocolate Delight ($14.99) - Featured
- Low Stock Item - Shows low stock warning
- Out of Stock Item - Shows "Out of Stock"

### 2. Test Shopping Cart

**✅ Verify:**
- [ ] Click "Add to Cart" on a product
- [ ] Cart count increases in header
- [ ] Navigate to cart page
- [ ] Update quantity works
- [ ] Remove item works
- [ ] Cart totals calculate correctly (subtotal, tax 10%, shipping)
- [ ] Free shipping message appears when subtotal < $50
- [ ] "Proceed to Checkout" button works

**Test Scenario:**
1. Add Classic Chocolate Chip (2 items)
2. Add Vanilla Sugar Cookies (1 item)
3. Verify subtotal: $36.97
4. Verify tax (10%): $3.70
5. Verify shipping: FREE (over $50 threshold) or $5.99
6. Verify total

### 3. Test Guest Checkout

**✅ Verify:**
- [ ] Click "Proceed to Checkout" without logging in
- [ ] Shipping form displays
- [ ] Fill in shipping information:
  - Full Name: Test User
  - Address: 123 Test St
  - City: San Francisco
  - State: CA
  - ZIP: 94102
  - Country: US
  - Phone: 555-1234
- [ ] Click "Continue to Payment"
- [ ] Payment form displays with Stripe Elements
- [ ] Order summary shows on the right

**Use Stripe Test Card:**
```
Card Number: 4242 4242 4242 4242
Expiry: 12/25 (any future date)
CVC: 123
ZIP: 12345
```

- [ ] Submit payment
- [ ] Success page displays with order number
- [ ] Order confirmation shows

### 4. Test User Registration & Login

**✅ Verify Registration:**
- [ ] Click "Login" in header
- [ ] Click "Sign up" link
- [ ] Fill registration form:
  - First Name: Test
  - Last Name: Customer
  - Email: test@example.com
  - Password: test123
  - Confirm Password: test123
- [ ] Submit registration
- [ ] Redirects to login page
- [ ] Success message appears

**✅ Verify Login:**
- [ ] Enter email: customer@example.com
- [ ] Enter password: customer123
- [ ] Click "Sign In"
- [ ] Redirects to homepage
- [ ] User name appears in header

### 5. Test User Profile & Orders

**Login as:** customer@example.com / customer123

**✅ Verify Profile:**
- [ ] Click profile link in header
- [ ] Account details display correctly
- [ ] Order History tab shows
- [ ] "View All Orders" link works

**✅ Verify Order History:**
- [ ] Navigate to Orders page
- [ ] Past orders display (should see 3 demo orders)
- [ ] Filter by status works
- [ ] Click "View Details" on an order
- [ ] Order details page shows full information
- [ ] Tracking number displays (if shipped/delivered)

**Expected Demo Orders:**
1. Order delivered with tracking: TRACK123456789
2. Order shipped with tracking: TRACK987654321
3. Order in processing status
4. Order pending payment

### 6. Test Authenticated Checkout

**✅ Verify:**
- [ ] While logged in, add items to cart
- [ ] Go to checkout
- [ ] Shipping form pre-fills with saved address (if applicable)
- [ ] Complete checkout
- [ ] Order appears in Order History
- [ ] Logout works

### 7. Test Admin Dashboard

**Login as:** admin@cookieshop.com / admin123

**✅ Verify Dashboard:**
- [ ] Navigate to /admin/dashboard or click from profile
- [ ] KPI cards display:
  - Total Revenue
  - Total Orders (should show 4)
  - Products (should show 10)
  - Customers (should show 3)
- [ ] Sales chart displays (last 7 days)
- [ ] Top products list shows
- [ ] Recent orders table displays
- [ ] All links work

**Expected Metrics:**
- Total Orders: 4
- Products: 10 (including 1 low stock, 1 out of stock)
- Customers: 3 users (2 customers, 1 admin)

### 8. Test Admin Product Management

**✅ Verify:**
- [ ] Navigate to Admin > Manage Products
- [ ] Products list displays
- [ ] Click "Add Product"
- [ ] Create new product with:
  - Name: Test Cookie
  - Price: 9.99
  - Description: Test description
  - Stock: 50
  - Category: Special
- [ ] Save product
- [ ] New product appears in list
- [ ] Edit existing product works
- [ ] Stock update works

### 9. Test Admin Order Management

**✅ Verify:**
- [ ] Navigate to Admin > Manage Orders
- [ ] Orders list displays (4 demo orders)
- [ ] Filter by status works (try "pending")
- [ ] Filter by payment status works
- [ ] Click "Status" button on an order
- [ ] Update status modal appears
- [ ] Change status (e.g., pending → processing)
- [ ] Status updates successfully
- [ ] Click "Tracking" button
- [ ] Add tracking number: TEST123456
- [ ] Add tracking URL (optional)
- [ ] Tracking updates successfully
- [ ] Pagination works (if > 20 orders)

### 10. Test Protected Routes

**✅ Verify:**
- [ ] Logout
- [ ] Try to access /profile (should redirect to login)
- [ ] Try to access /orders (should redirect to login)
- [ ] Try to access /admin/dashboard (should redirect to login)
- [ ] Login as customer@example.com
- [ ] /profile accessible
- [ ] /orders accessible
- [ ] /admin/dashboard still blocked (customer role)
- [ ] Login as admin@cookieshop.com
- [ ] All admin routes accessible

---

## 📊 Demo Data Summary

### Users
| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| admin@cookieshop.com | admin123 | Admin | Test admin features |
| customer@example.com | customer123 | Customer | Test customer with orders |
| jane@example.com | jane123 | Customer | Test second customer |

### Products (10 total)
- **8 regular products** - Various prices ($10.99 - $14.99)
- **4 featured products** - Show on homepage
- **1 low stock** - 5 units (threshold: 10)
- **1 out of stock** - 0 units

### Orders (4 total)
1. **Delivered** - 10 days ago, paid, with tracking
2. **Shipped** - 3 days ago, paid, with tracking
3. **Processing** - 1 day ago, paid
4. **Pending** - Today, payment pending

### Categories (4 total)
- Chocolate Chip
- Sugar Cookies
- Oatmeal
- Special

---

## 🐛 Troubleshooting

### Backend won't start
**Error:** `ModuleNotFoundError` or import errors
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

**Error:** Database connection failed
**Solution:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Try: `psql -U postgres -l` to list databases

### Frontend won't start
**Error:** Module not found
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error:** API calls failing (CORS)
**Solution:**
- Check CORS_ORIGINS in backend `.env`
- Ensure it includes `http://localhost:5173`

### Stripe payment fails
**Error:** Invalid API key
**Solution:**
- Verify Stripe keys in both backend and frontend `.env`
- Ensure using test keys (sk_test_... and pk_test_...)
- Get keys from: https://dashboard.stripe.com/test/apikeys

**Test Card Not Working:**
- Use: 4242 4242 4242 4242
- Any future expiry date
- Any 3-digit CVC
- Any 5-digit ZIP

### Seed script fails
**Error:** IntegrityError or foreign key constraint
**Solution:**
```bash
# Drop and recreate database
dropdb cookie_shop_dev
createdb cookie_shop_dev
flask db upgrade
python scripts/seed_demo_data.py
```

### Cannot login
**Error:** Invalid credentials
**Solution:**
- Ensure seed script ran successfully
- Check demo account credentials above
- Try resetting database and re-seeding

---

## 🔄 Reset Demo Data

To reset and reload demo data:

```bash
cd backend
python scripts/seed_demo_data.py
```

Type `yes` when prompted. This will:
1. Delete all existing data
2. Recreate demo users, products, and orders

---

## ✅ Testing Complete!

Once all tests pass, your application is working correctly locally.

### What to Test Next:
1. **Error Handling** - Try invalid inputs
2. **Edge Cases** - Empty cart, sold out products
3. **Mobile Responsiveness** - Test on different screen sizes
4. **Browser Compatibility** - Test in Chrome, Firefox, Safari

### Ready for Production?
Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide for production deployment.

---

## 📝 Test Results Template

Use this template to document your testing:

```
Date: [DATE]
Tester: [NAME]

✅ Homepage & Product Browsing: PASS/FAIL
✅ Shopping Cart: PASS/FAIL
✅ Guest Checkout: PASS/FAIL
✅ User Registration: PASS/FAIL
✅ User Login: PASS/FAIL
✅ User Profile & Orders: PASS/FAIL
✅ Authenticated Checkout: PASS/FAIL
✅ Admin Dashboard: PASS/FAIL
✅ Admin Product Management: PASS/FAIL
✅ Admin Order Management: PASS/FAIL
✅ Protected Routes: PASS/FAIL

Issues Found:
- [List any issues]

Notes:
- [Additional observations]
```

---

**Happy Testing! 🎉**

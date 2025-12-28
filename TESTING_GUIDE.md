# Cookie Shop - Testing Guide

## 🎉 Project is Running Successfully!

All Docker containers are up and running with the latest code including:
- ✅ Razorpay payment integration
- ✅ Cloudinary image CDN
- ✅ AI Chatbot assistant
- ✅ Complete e-commerce features

## 📊 Current Status

```
Service          Status      Port     URL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend         HEALTHY     3000     http://localhost:3000
Backend API      HEALTHY     5000     http://localhost:5000
PostgreSQL       HEALTHY     5432     localhost:5432
Redis            RUNNING     6379     localhost:6379
```

**Database:** 12 products loaded with demo data
**Payment:** Razorpay configured (add your test keys)
**Images:** Cloudinary CDN ready
**Chatbot:** AI assistant fully functional

## 🌐 Access the Application

### Main Website
```
http://localhost:3000
```

**What to test:**
- Browse products on homepage
- Search for products
- View product details
- Add items to cart
- Complete checkout process
- User registration & login
- Order history

### Admin Dashboard
```
http://localhost:3000/admin
```

**Login Credentials:**
```
Email: admin@cookieshop.com
Password: admin123
```

**What to test:**
- View dashboard statistics
- Manage products (CRUD)
- View and update orders
- Upload product images to Cloudinary
- Create/delete categories

### Customer Account
```
http://localhost:3000/login
```

**Test Customer Credentials:**
```
Email: customer@example.com
Password: password123
```

**What to test:**
- Login/logout
- View profile
- Order history
- Place new orders

## 🤖 Testing the Chatbot

### Access the Chatbot

1. Open http://localhost:3000
2. Look for the **bouncing fox chef** in the bottom-right corner
3. Click on the fox to open the chatbot

### Test Queries

Try these conversations:

**1. Greeting:**
```
"Hi" or "Hello"
```
Expected: Welcome message with suggestions

**2. Product Search:**
```
"Show me chocolate cookies"
"I need vanilla cookies"
"Do you have oatmeal cookies?"
```
Expected: List of matching products with images and prices

**3. Occasion Recommendations:**
```
"I need cookies for a birthday"
"Party suggestions"
"Gift ideas"
```
Expected: Featured products perfect for the occasion

**4. Allergen Queries:**
```
"Do you have gluten-free options?"
"Show me dairy-free cookies"
"I need nut-free cookies"
```
Expected: Filtered products based on allergens

**5. Stock Availability:**
```
"What's in stock?"
"Check availability"
```
Expected: List of available products

**6. Ingredients:**
```
"What's in the chocolate chip cookies?"
"Tell me the ingredients"
```
Expected: Detailed ingredient information

**7. Price Queries:**
```
"Show me budget-friendly cookies"
"What are your premium options?"
```
Expected: Products sorted by price

## 🛒 Test E-Commerce Flow

### Complete Purchase Flow

1. **Browse Products**
   - Visit http://localhost:3000
   - View featured products
   - Click on any product to see details

2. **Add to Cart**
   - Click "Add to Cart" on products
   - View cart icon update with count
   - Click cart icon to view cart

3. **Checkout**
   - Click "Proceed to Checkout"
   - Fill in shipping details:
     ```
     Name: Test User
     Email: test@example.com
     Phone: 9876543210
     Address: 123 Test Street
     City: Mumbai
     State: Maharashtra
     Pincode: 400001
     ```

4. **Payment (Test Mode)**
   - Order will be created
   - Note: Add Razorpay test keys to test actual payment
   - Order status will be "Pending" without payment

5. **View Order**
   - Go to "My Orders" in user menu
   - View order details
   - Check order status

### Admin Order Management

1. Login as admin (admin@cookieshop.com / admin123)
2. Go to http://localhost:3000/admin/orders
3. View all orders
4. Update order status
5. View order details

## 🎨 Test Product Management

### Add New Product (Admin)

1. Login as admin
2. Go to http://localhost:3000/admin
3. Click "Add Product"
4. Fill in details:
   ```
   Name: Test Cookie
   Price: 15.99
   Description: Delicious test cookie
   Category: Select from dropdown
   Stock: 50
   SKU: TEST-001
   Ingredients: Flour, Sugar, Butter
   Allergens: Wheat, Dairy
   ```
5. Upload image (will be stored in Cloudinary CDN)
6. Mark as "Active" and "Featured"
7. Save product

### Test Image Upload

**Note:** Product images are uploaded to Cloudinary CDN automatically.

1. In admin panel, click "Edit" on any product
2. Upload a new image
3. Image will be:
   - Uploaded to Cloudinary
   - Optimized automatically
   - Available in 3 sizes (thumbnail, medium, large)
   - Served via global CDN

## 🔌 API Testing

### Backend API Endpoints

Base URL: `http://localhost:5000/api/v1`

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Get Products:**
```bash
curl http://localhost:5000/api/v1/products
```

**Get Categories:**
```bash
curl http://localhost:5000/api/v1/categories
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","password":"password123"}'
```

**Chatbot:**
```bash
curl -X POST http://localhost:5000/api/v1/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{"message":"show me chocolate cookies"}'
```

**Create Order (requires auth token):**
```bash
# First login and get token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","password":"password123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Then create order
curl -X POST http://localhost:5000/api/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": {
      "full_name": "Test User",
      "phone": "9876543210",
      "address_line1": "123 Test St",
      "city": "Mumbai",
      "state": "Maharashtra",
      "pincode": "400001"
    }
  }'
```

## 💳 Razorpay Payment Testing

### Setup Test Credentials

1. **Get Razorpay Test Keys:**
   - Visit https://dashboard.razorpay.com/app/keys
   - Copy Test Key ID and Test Key Secret

2. **Update Environment:**
   ```bash
   # Edit backend/.env.docker
   RAZORPAY_KEY_ID=rzp_test_your_key_id
   RAZORPAY_KEY_SECRET=your_key_secret
   ```

3. **Restart Backend:**
   ```bash
   docker-compose restart backend
   ```

### Test Payment Flow

Once Razorpay is configured:

1. Complete checkout process
2. Razorpay payment modal will appear
3. Use test card details:
   ```
   Card Number: 4111 1111 1111 1111
   CVV: Any 3 digits
   Expiry: Any future date
   ```
4. Payment will be processed in test mode
5. Order status updates to "Processing"

## 📦 Available Demo Data

### Products (12 total)
- Classic Chocolate Chip
- Double Chocolate Delight
- Oatmeal Raisin
- Oatmeal Chocolate Chip
- Peanut Butter Cookies
- White Chocolate Macadamia
- Gingerbread Cookies
- Sugar Cookies
- Vanilla Sugar Cookies
- Lemon Sugar Cookies
- Snickerdoodle
- Cloudinary Test Cookie

### Categories (4 total)
- Classic Cookies
- Premium Cookies
- Seasonal Cookies
- Sugar Cookies

### Users (3 accounts)
1. **Admin:** admin@cookieshop.com / admin123
2. **Customer:** customer@example.com / password123
3. **Test User:** test@example.com / password123

### Orders (5 demo orders)
- Various order statuses: Pending, Processing, Completed
- Different payment statuses
- Order history for testing

## 🐛 Troubleshooting

### Container Issues

**Check container status:**
```bash
docker-compose ps
```

**View logs:**
```bash
# All logs
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

**Restart services:**
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
docker-compose restart frontend
```

**Rebuild if needed:**
```bash
docker-compose up --build -d
```

### Common Issues

**1. Frontend not loading:**
```bash
# Check frontend container
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

**2. API returning errors:**
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

**3. Database connection issues:**
```bash
# Check database health
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

**4. Chatbot not appearing:**
- Ensure frontend is rebuilt after adding chatbot
- Check browser console for errors
- Verify `chef-cookie.png` is in frontend/public/ folder

**5. Images not uploading:**
- Check Cloudinary credentials in backend/.env.docker
- Verify Cloudinary is configured (check backend logs)
- Test image upload in admin panel

### Reset Database

If you need to reset the database:

```bash
# Stop all containers
docker-compose down

# Remove database volume
docker volume rm baking_postgres_data

# Start fresh
docker-compose up -d

# Seed demo data
docker-compose exec backend python scripts/seed_demo_data.py --force
```

## 📝 Test Checklist

Use this checklist to verify all features:

### Frontend
- [ ] Homepage loads correctly
- [ ] Products display with images
- [ ] Product details page works
- [ ] Cart functionality works
- [ ] Checkout process completes
- [ ] User registration works
- [ ] User login works
- [ ] Order history displays
- [ ] Admin dashboard loads
- [ ] Product management (CRUD) works
- [ ] Chatbot appears and responds

### Backend API
- [ ] Health check responds
- [ ] Products API returns data
- [ ] Categories API works
- [ ] Authentication endpoints work
- [ ] Order creation works
- [ ] Chatbot API responds correctly
- [ ] Image upload to Cloudinary works

### Chatbot
- [ ] Chatbot button appears
- [ ] Chat window opens/closes
- [ ] Greetings work
- [ ] Product search works
- [ ] Allergen filtering works
- [ ] Occasion recommendations work
- [ ] Stock queries work
- [ ] Product cards display
- [ ] Suggestions appear

### Payment (with Razorpay configured)
- [ ] Payment modal appears
- [ ] Test payment processes
- [ ] Order status updates
- [ ] Payment confirmation received

### Images (Cloudinary)
- [ ] Image upload works
- [ ] Images display from CDN
- [ ] Multiple sizes generated
- [ ] Product images show correctly

## 🚀 Performance Tips

### For Best Testing Experience:

1. **Use Chrome/Firefox** for best compatibility
2. **Clear browser cache** if seeing old data
3. **Check network tab** to see API calls
4. **Use React DevTools** for debugging frontend
5. **Monitor Docker logs** for backend issues

### Quick Commands

```bash
# View all containers
docker-compose ps

# Follow logs in real-time
docker-compose logs -f

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Rebuild and start
docker-compose up --build -d
```

## 📞 Support

If you encounter issues:

1. Check the relevant logs
2. Verify all containers are healthy
3. Ensure environment variables are set
4. Try rebuilding containers
5. Check this troubleshooting guide

## 🎯 Next Steps

After testing, you can:

1. **Add Real Razorpay Keys** for actual payments
2. **Add Product Images** to Cloudinary for better visuals
3. **Customize Products** via admin panel
4. **Create Test Orders** to verify full flow
5. **Test Chatbot** with various queries
6. **Deploy to Production** when ready

---

**Status:** ✅ All Services Running
**Last Updated:** December 28, 2025
**Ready for Testing!** 🎉

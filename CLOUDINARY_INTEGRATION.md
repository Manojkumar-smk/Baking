# Cloudinary Integration Guide

## Overview

The Cookie Shop application uses **Cloudinary** for secure, scalable product image storage and delivery. Images are uploaded to Cloudinary's CDN, which provides automatic optimization, transformations, and fast global delivery.

## Architecture

```
┌──────────────┐      Upload      ┌──────────────┐      Store      ┌──────────────┐
│   Admin UI   │ ─────────────>   │   Backend    │ ─────────────>  │  Cloudinary  │
└──────────────┘                  └──────────────┘                  └──────────────┘
                                         │                                   │
                                         │ Save URL                          │
                                         ▼                                   │
                                  ┌──────────────┐                          │
                                  │  PostgreSQL  │                          │
                                  └──────────────┘                          │
                                                                              │
┌──────────────┐      View        ┌──────────────┐      Fetch      ┌────────┘
│ Customer UI  │ <───────────────  │   Backend    │ <──────────────┘
└──────────────┘                  └──────────────┘
```

### Flow:
1. **Upload**: Admin uploads product image through the API
2. **Storage**: Backend uploads to Cloudinary and receives URL
3. **Database**: Only the Cloudinary URL is saved in PostgreSQL
4. **Delivery**: Customers load optimized images directly from Cloudinary CDN

## Features

### ✅ Automated Image Optimization
- Automatic format conversion (WebP, AVIF)
- Quality optimization based on device and network
- Responsive image delivery

### ✅ Multiple Image Sizes
Each uploaded image generates 3 optimized versions:
- **Thumbnail**: 300x300px (for listings, cart)
- **Medium**: 800x800px (for product pages)
- **Large**: 1200x1200px (for lightbox/zoom)

### ✅ CDN Delivery
- Global CDN ensures fast loading worldwide
- Built-in caching and compression
- 99.99% uptime SLA

### ✅ Security
- Secure HTTPS URLs
- API key authentication
- Image validation and sanitization

## Configuration

### Environment Variables

Add these to your `.env` or `.env.docker` file:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=drgbtdjip
CLOUDINARY_API_KEY=221116352726669
CLOUDINARY_API_SECRET=bffdDaq2a3Op-TpKILWMDYQcaW4
```

**Where to find your credentials:**
1. Log in to [Cloudinary Console](https://cloudinary.com/console)
2. Navigate to Dashboard
3. Copy Cloud Name, API Key, and API Secret

### Docker Setup

The credentials are already configured in `backend/.env.docker`. When you rebuild the backend container, Cloudinary will be automatically initialized:

```bash
docker-compose up --build backend
```

## API Usage

### Create Product with Image

**Endpoint:** `POST /api/v1/admin/products`

**Content-Type:** `multipart/form-data`

**Headers:**
```
Authorization: Bearer <admin_jwt_token>
Content-Type: multipart/form-data
```

**Form Data:**
```
name: "Chocolate Chip Cookies"
price: 12.99
description: "Delicious homemade cookies"
category_id: "category-uuid"
stock_quantity: 100
image: <file>                      # Main product image
additional_images[]: <file>        # Optional: Multiple files
ingredients: ["Flour", "Sugar", "Chocolate"]  # JSON array
allergens: ["Wheat", "Dairy"]      # JSON array
is_featured: true
is_active: true
```

**Example using cURL:**

```bash
# Get admin token first
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cookieshop.com","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Upload product with image
curl -X POST http://localhost:5000/api/v1/admin/products \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Chocolate Chip Cookies" \
  -F "price=12.99" \
  -F "description=Delicious homemade cookies" \
  -F "stock_quantity=100" \
  -F "image=@/path/to/cookie-image.jpg" \
  -F 'ingredients=["Flour","Sugar","Chocolate Chips"]' \
  -F 'allergens=["Wheat","Dairy"]' \
  -F "is_featured=true"
```

**Response:**
```json
{
  "message": "Product created successfully",
  "product": {
    "id": "product-uuid",
    "name": "Chocolate Chip Cookies",
    "price": 12.99,
    "image_url": "https://res.cloudinary.com/drgbtdjip/image/upload/v1234567/cookie-shop/products/product-uuid.jpg",
    "images": [
      "https://res.cloudinary.com/drgbtdjip/image/upload/v1234567/cookie-shop/products/product-uuid_0.jpg"
    ],
    ...
  }
}
```

### Update Product Image

**Endpoint:** `PUT /api/v1/admin/products/<product_id>`

```bash
curl -X PUT http://localhost:5000/api/v1/admin/products/<product_id> \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@/path/to/new-image.jpg"
```

## Image Transformations

Cloudinary automatically generates optimized versions of each image:

### URL Patterns

**Original Upload:**
```
https://res.cloudinary.com/drgbtdjip/image/upload/v1234567/cookie-shop/products/product-uuid.jpg
```

**Thumbnail (300x300, optimized quality):**
```
https://res.cloudinary.com/drgbtdjip/image/upload/w_300,h_300,c_fill,q_auto:good/cookie-shop/products/product-uuid.jpg
```

**Medium (800x800, best quality):**
```
https://res.cloudinary.com/drgbtdjip/image/upload/w_800,h_800,c_limit,q_auto:best/cookie-shop/products/product-uuid.jpg
```

**Large (1200x1200, best quality):**
```
https://res.cloudinary.com/drgbtdjip/image/upload/w_1200,h_1200,c_limit,q_auto:best/cookie-shop/products/product-uuid.jpg
```

### Transformation Parameters
- `w_X,h_Y` - Width and height
- `c_fill` - Crop and fill to exact dimensions
- `c_limit` - Limit size while maintaining aspect ratio
- `q_auto:good` - Automatic quality optimization (good balance)
- `q_auto:best` - Automatic quality optimization (best quality)

## Image Upload Service

The backend includes a comprehensive `ImageService` class in `app/services/image_service.py`:

### Key Functions

#### `upload_product_image(file, product_id)`
Uploads an image to Cloudinary with validation and optimization.

```python
from app.services.image_service import ImageService

# Upload image
result = ImageService.upload_product_image(file, product_id)

# Result contains:
# - url: Original Cloudinary URL
# - thumbnail_url: 300x300 optimized
# - medium_url: 800x800 optimized
# - large_url: 1200x1200 optimized
# - public_id: Cloudinary identifier
# - format, width, height, bytes
```

#### `delete_product_image(public_id)`
Deletes an image from Cloudinary.

```python
success = ImageService.delete_product_image(public_id)
```

#### `extract_public_id_from_url(url)`
Extracts the Cloudinary public_id from a full URL.

```python
public_id = ImageService.extract_public_id_from_url(cloudinary_url)
```

## File Validation

Images are validated before upload:

- **Allowed Formats**: PNG, JPG, JPEG, GIF, WebP
- **Max File Size**: 10MB
- **Format Verification**: Uses PIL to verify actual image data
- **Security**: Filename sanitization and validation

## Frontend Integration

### Displaying Images

The frontend receives Cloudinary URLs directly from the API:

```typescript
// Product object from API
interface Product {
  id: string;
  name: string;
  price: number;
  image_url: string;  // Cloudinary URL
  images: string[];   // Array of Cloudinary URLs
}

// In React component
<img
  src={product.image_url}
  alt={product.name}
  loading="lazy"  // Native lazy loading
/>
```

### Image Optimization in Frontend

Cloudinary automatically:
- Delivers WebP/AVIF to supported browsers
- Adjusts quality based on connection speed
- Provides responsive images via `srcset`
- Caches globally for fast delivery

## Testing Image Upload

### Using Postman or Insomnia

1. **Login as Admin:**
   - POST `http://localhost:5000/api/v1/auth/login`
   - Body: `{"email": "admin@cookieshop.com", "password": "admin123"}`
   - Copy the `access_token`

2. **Create Product with Image:**
   - POST `http://localhost:5000/api/v1/admin/products`
   - Headers: `Authorization: Bearer <token>`
   - Body type: `form-data`
   - Add fields: name, price, description, etc.
   - Add file: `image` (select a JPG/PNG file)
   - Send request

3. **Verify Upload:**
   - Check response for `image_url` containing Cloudinary URL
   - Visit the URL in browser to see the image
   - Test different transformations by modifying URL parameters

## Cloudinary Dashboard

Monitor your image usage at [Cloudinary Console](https://cloudinary.com/console):

- **Media Library**: View all uploaded images
- **Transformations**: See most-used transformations
- **Usage**: Track bandwidth and storage
- **Analytics**: Monitor CDN performance

## Folder Structure in Cloudinary

All product images are organized in:
```
cookie-shop/
  └── products/
       ├── product-uuid-1.jpg
       ├── product-uuid-2.jpg
       └── product-uuid-3.jpg
```

## Benefits

### vs. Local Storage
- ✅ No server disk space usage
- ✅ Automatic backups and redundancy
- ✅ Global CDN delivery (faster loading)
- ✅ Automatic optimization
- ✅ Scales infinitely

### vs. S3/Cloud Storage
- ✅ Built-in image transformations
- ✅ Automatic format optimization
- ✅ Easier integration
- ✅ Better performance for images
- ✅ Free tier available

## Troubleshooting

### "Cloudinary not configured" Warning

**Cause**: Environment variables not set correctly

**Solution:**
```bash
# Check environment variables in container
docker-compose exec backend env | grep CLOUDINARY

# Should show:
# CLOUDINARY_CLOUD_NAME=drgbtdjip
# CLOUDINARY_API_KEY=221116352726669
# CLOUDINARY_API_SECRET=bffdDaq2a3Op-TpKILWMDYQcaW4

# If missing, update .env.docker and rebuild:
docker-compose up --build backend
```

### Upload Fails with "Invalid image file"

**Cause**: File is corrupted or not a valid image

**Solution:**
- Verify file is a real image (not renamed .txt)
- Try a different image
- Check file size (max 10MB)

### Image URL returns 404

**Cause**: Image not uploaded or deleted from Cloudinary

**Solution:**
- Check Cloudinary Media Library
- Verify public_id matches URL
- Re-upload the image

## Migration from Local Storage

If you have existing products with local images:

1. **Create Migration Script:**
   ```python
   # In backend container
   from app.services.image_service import ImageService
   from app.models.product import Product
   from app.database.db import db

   products = Product.query.filter(Product.image_url != None).all()

   for product in products:
       if '/static/uploads/' in product.image_url:
           # Download local image
           local_path = f"app{product.image_url}"
           with open(local_path, 'rb') as f:
               # Upload to Cloudinary
               result = ImageService.upload_product_image(f, product.id)
               product.image_url = result['medium_url']
               db.session.commit()
   ```

2. **Run Migration:**
   ```bash
   docker-compose exec backend python scripts/migrate_to_cloudinary.py
   ```

## Best Practices

1. **Always use medium_url** for product listings
2. **Use thumbnail_url** for cart items and small previews
3. **Use large_url** for product detail pages
4. **Enable lazy loading** on all images
5. **Set proper alt text** for accessibility
6. **Monitor usage** in Cloudinary dashboard
7. **Set up transformations** for consistent styling

## Pricing

Cloudinary Free Tier includes:
- **25 GB** storage
- **25 GB** monthly bandwidth
- **25,000** transformations/month

For Cookie Shop demo: **Free tier is sufficient**

Upgrade only needed for:
- High traffic production sites
- Large number of products (>1000 images)
- Video support

## Support

- **Cloudinary Docs**: https://cloudinary.com/documentation
- **API Reference**: https://cloudinary.com/documentation/image_upload_api_reference
- **Support**: https://support.cloudinary.com

---

**Integration Status:** ✅ Fully Configured and Ready

**Last Updated:** December 28, 2025

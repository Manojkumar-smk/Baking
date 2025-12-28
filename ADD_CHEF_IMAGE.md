# How to Add the Chef Cookie Image

## Current Status

✅ **The chatbot is now working with a fallback emoji avatar (👨‍🍳)**

The chatbot will display a chef emoji until you add the actual chef cookie image.

## To Add Your Custom Chef Cookie Image

### Step 1: Save the Image

1. **Right-click** on the chef cookie image you want to use (the cute fox chef character)
2. **Save image as...**
3. **Name it exactly:** `chef-cookie.png`
4. **Save location:** `C:\Users\manoj\Baking\frontend\public\chef-cookie.png`

### Step 2: Rebuild Frontend

After saving the image, rebuild the frontend container:

```bash
cd C:\Users\manoj\Baking
docker-compose up --build -d frontend
```

### Step 3: Verify

1. Open http://localhost:3000
2. The chatbot button should now show your chef cookie image
3. Click it to open and see the image in the chat header and messages

## Alternative: Use a URL

If you have the image hosted somewhere (like Cloudinary, Imgur, etc.), you can update the image path directly:

1. Edit `frontend/src/components/Chatbot/Chatbot.tsx`
2. Change all instances of `/chef-cookie.png` to your image URL
3. For example: `https://your-cdn.com/chef-cookie.png`
4. Rebuild: `docker-compose up --build -d frontend`

## File Formats Supported

- PNG (recommended for transparency)
- JPEG/JPG
- GIF (animated gifs will work!)
- SVG
- WebP

## Recommended Image Specs

- **Size:** 200x200px to 400x400px
- **Format:** PNG with transparent background
- **File Size:** Under 100KB
- **Aspect Ratio:** Square (1:1)

## Current Fallback

Until you add the chef-cookie.png image, the chatbot displays:
- 👨‍🍳 Chef emoji on an orange circular background
- Fully functional chatbot
- All features work exactly the same

## Troubleshooting

**Image not showing after adding it:**
1. Verify the filename is exactly `chef-cookie.png` (case-sensitive)
2. Verify it's in `frontend/public/` folder
3. Rebuild frontend: `docker-compose up --build -d frontend`
4. Clear browser cache (Ctrl+Shift+Delete)
5. Hard refresh the page (Ctrl+F5)

**Image looks distorted:**
1. Make sure it's a square image (same width and height)
2. Use PNG format with transparent background
3. Recommended size: 300x300px or 400x400px

**Want to use a different image:**
1. Replace `frontend/public/chef-cookie.png` with your new image
2. Keep the same filename
3. Rebuild: `docker-compose up --build -d frontend`

## Quick Test

After adding the image, you should see:
1. ✅ Chef cookie image on floating button (bottom-right corner)
2. ✅ Chef cookie image in chat header when opened
3. ✅ Chef cookie image next to bot messages
4. ✅ Bouncing and wiggling animations on the button

---

**Note:** The chatbot is fully functional with or without the custom image! The emoji fallback works perfectly.

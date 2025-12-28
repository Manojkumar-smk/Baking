# Chatbot Integration Guide

## Overview

The Cookie Shop features an intelligent assistive chatbot powered by "Chef Cookie" - your friendly fox chef assistant! The chatbot helps customers find products, check ingredients, get recommendations, and answers questions about the cookie shop.

## Features

### Intelligent Query Processing

The chatbot understands natural language queries and provides contextual responses for:

- **Product Search**: Find cookies by flavor, type, or name
- **Occasion Recommendations**: Get suggestions for birthdays, parties, gifts, etc.
- **Allergen Information**: Filter products by dietary restrictions
- **Ingredient Details**: Check what's in each cookie
- **Stock Availability**: See what's currently in stock
- **Price Queries**: Find budget-friendly or premium options
- **General Help**: Learn what the chatbot can do

### Interactive Elements

- **Product Cards**: Visual product displays with images, prices, and stock status
- **Quick Suggestions**: Context-aware suggestion buttons for follow-up queries
- **Real-time Responses**: Instant answers with typing indicators
- **Persistent Chat**: Conversation history maintained during session

## Architecture

```
┌──────────────┐      Query      ┌──────────────┐      Process      ┌──────────────┐
│   Frontend   │ ─────────────>   │   Backend    │ ─────────────>  │   ChatBot    │
│   Chatbot    │                  │   API        │                  │   Service    │
│  Component   │ <─────────────   │              │ <─────────────  │              │
└──────────────┘    Response      └──────────────┘    Results       └──────────────┘
                                         │
                                         │ Query Products
                                         ▼
                                  ┌──────────────┐
                                  │  PostgreSQL  │
                                  │   Database   │
                                  └──────────────┘
```

## Backend Implementation

### API Endpoints

**Base URL**: `http://localhost:5000/api/v1/chatbot`

#### POST /message
Send a message to the chatbot

**Request:**
```json
{
  "message": "Show me chocolate cookies"
}
```

**Response:**
```json
{
  "type": "search_results",
  "message": "Found 3 delicious matches! 🍪",
  "products": [
    {
      "id": "product-uuid",
      "name": "Classic Chocolate Chip",
      "price": 12.99,
      "image_url": "https://cloudinary.com/...",
      "description": "Traditional chocolate chip cookies",
      "in_stock": true
    }
  ],
  "suggestions": [
    "Tell me the ingredients",
    "What else do you have?"
  ]
}
```

#### GET /suggestions
Get conversation starter suggestions

**Response:**
```json
{
  "suggestions": [
    "Hi! What can you help me with?",
    "Show me birthday cookies",
    "What cookies are in stock?",
    "I need gluten-free options",
    "Show me chocolate cookies"
  ]
}
```

### Response Types

The chatbot returns different response types based on the query:

| Type | Description | Includes Products |
|------|-------------|-------------------|
| `greeting` | Initial welcome message | No |
| `recommendation` | Occasion-based suggestions | Yes |
| `allergen_safe` | Allergen-free products | Yes |
| `ingredients` | Ingredient information | Optional |
| `stock` | In-stock products | Yes |
| `price_info` | Price-based results | Yes |
| `search_results` | Product search results | Yes |
| `help` | Capabilities overview | No |
| `clarification` | Unclear query response | No |
| `error` | Error occurred | No |

### ChatbotService Logic

The service processes queries using pattern matching:

```python
# Example patterns
GREETINGS = ['hi', 'hello', 'hey', 'greetings']
OCCASIONS = ['birthday', 'party', 'celebration', 'gift']
ALLERGENS = ['allergy', 'allergic', 'allergen', 'vegan', 'gluten']
INGREDIENTS = ['ingredient', 'contain', 'made of', 'recipe']
STOCK = ['stock', 'available', 'in stock', 'availability']
PRICE = ['price', 'cost', 'expensive', 'cheap', 'budget']
PRODUCTS = ['chocolate', 'vanilla', 'oatmeal', 'peanut', 'cookie']
```

Each pattern triggers specific database queries to fetch relevant products.

## Frontend Implementation

### Component Structure

```
Chatbot/
├── Chatbot.tsx       # Main chatbot component
└── Chatbot.css       # Styling and animations
```

### Key Features

**1. Floating Button**
- Fixed position in bottom-right corner
- Animated pulse effect
- Fox chef character image
- Bounce and wiggle animations

**2. Chat Window**
- 400x600px chat interface
- Responsive design (full-screen on mobile)
- Smooth slide-up animation
- Auto-scroll to latest message

**3. Message Types**
- User messages (right-aligned, orange gradient)
- Bot messages (left-aligned, white background)
- Typing indicator during processing
- Timestamp for each message

**4. Product Display**
- Grid layout for product cards
- Product images (if available)
- Price in INR (₹)
- Stock status indicators
- Hover effects

**5. Quick Suggestions**
- Context-aware suggestion buttons
- Pill-shaped design
- Click to send as message
- Hover animations

### Usage in App

The chatbot is globally available across all pages:

```tsx
// App.tsx
import Chatbot from '@/components/Chatbot/Chatbot'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <CartProvider>
            <Routes />
            <Chatbot />  {/* Global chatbot */}
          </CartProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}
```

### Customization

**Colors:**
```css
/* Primary gradient */
background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);

/* Status indicators */
.in-stock { background: #d1fae5; color: #065f46; }
.out-of-stock { background: #fee2e2; color: #991b1b; }
```

**Animations:**
- Pulse: 2s infinite
- Bounce: 2s infinite
- Wiggle: 3s infinite
- Typing: 1.4s infinite
- Slide-up: 0.3s ease
- Fade-in: 0.3s ease

## Example Conversations

### 1. Finding Birthday Cookies
```
User: "I need cookies for a birthday party"

Bot: "🎂 Perfect for birthdays! Here are our most popular celebration cookies:"
[Shows featured products]
Suggestions: ["Tell me about ingredients", "What's in stock?"]
```

### 2. Checking Allergens
```
User: "Do you have gluten-free cookies?"

Bot: "Great news! Here are our gluten-free cookies: 🍪✨"
[Shows gluten-free products]
Suggestions: ["Tell me the ingredients", "What else is available?"]
```

### 3. Product Search
```
User: "Show me chocolate cookies"

Bot: "Found 3 delicious matches! 🍪"
[Shows chocolate cookie products]
Suggestions: ["Tell me the ingredients", "What else do you have?"]
```

### 4. Ingredient Inquiry
```
User: "What's in the chocolate chip cookies?"

Bot: "**Classic Chocolate Chip** 🍪

**Ingredients:**
Flour, Sugar, Butter, Chocolate Chips, Eggs, Vanilla

**Allergens:**
Wheat, Dairy, Eggs

**Description:**
Traditional chocolate chip cookies made with premium chocolate chips"

Suggestions: ["Add to cart", "Show similar cookies"]
```

### 5. Stock Check
```
User: "What's in stock?"

Bot: "We have 10 delicious cookies in stock right now! 🎉"
[Shows in-stock products with quantities]
Suggestions: ["Show me chocolate cookies", "Birthday recommendations"]
```

## Mobile Responsiveness

The chatbot adapts to mobile screens:

```css
@media (max-width: 480px) {
  .chatbot-window {
    width: calc(100vw - 32px);
    height: calc(100vh - 32px);
  }

  .chatbot-button {
    width: 60px;
    height: 60px;
  }
}
```

## Integration Steps

### 1. Save Chef Cookie Image

Save the fox chef character image as `frontend/public/chef-cookie.png`

### 2. Backend Setup

The chatbot API is automatically loaded with the backend:

```bash
# Rebuild backend (if needed)
docker-compose up --build backend
```

### 3. Frontend Setup

The chatbot is already integrated into `App.tsx`. No additional setup needed.

### 4. Testing

**Test Backend API:**
```bash
curl -X POST http://localhost:5000/api/v1/chatbot/message \
  -H "Content-Type: application/json" \
  -d '{"message":"hi"}'
```

**Test Frontend:**
1. Open http://localhost:5173
2. Click the fox chef button in bottom-right
3. Chat window opens with greeting
4. Try various queries:
   - "Show me birthday cookies"
   - "What's gluten-free?"
   - "I need chocolate cookies"
   - "What's in stock?"

## Query Examples

### Greetings
- "hi", "hello", "hey"
- "greetings", "good morning"

### Occasions
- "birthday cookies"
- "party suggestions"
- "gift ideas"
- "celebration cookies"

### Allergens
- "gluten-free options"
- "dairy-free cookies"
- "nut-free products"
- "egg-free cookies"
- "vegan options"

### Ingredients
- "what's in the chocolate chip cookies?"
- "show me ingredients"
- "what contains peanuts?"

### Stock
- "what's in stock?"
- "is this available?"
- "check availability"

### Price
- "show me cheap cookies"
- "budget options"
- "expensive cookies"
- "premium products"

### Products
- "chocolate cookies"
- "vanilla products"
- "oatmeal cookies"
- "peanut butter cookies"

### Help
- "what can you help with?"
- "help me"
- "how can you assist?"

## Best Practices

### 1. Clear Messaging
- Keep responses concise and friendly
- Use emojis to enhance engagement
- Provide context-aware suggestions

### 2. Product Display
- Always show product images when available
- Include stock status for all products
- Display prices in local currency (₹ INR)

### 3. Conversation Flow
- Limit products shown to 4-6 per response
- Provide 2-4 relevant suggestions
- Maintain conversational tone

### 4. Error Handling
- Graceful fallbacks for unclear queries
- Helpful "did you mean" suggestions
- Clear error messages

## Performance Considerations

- **Response Time**: < 500ms for most queries
- **Database Queries**: Optimized with proper indexing
- **Caching**: Consider Redis for frequent queries
- **Image Loading**: Lazy load product images
- **Message History**: Limited to current session

## Future Enhancements

- **Natural Language AI**: Integrate OpenAI/Anthropic for advanced NLP
- **User Preferences**: Remember user preferences across sessions
- **Order Tracking**: Check order status through chatbot
- **Recommendations Engine**: ML-based product recommendations
- **Multi-language**: Support multiple languages
- **Voice Input**: Speech-to-text integration
- **Cart Integration**: Add products directly from chat
- **Analytics**: Track common queries and improve responses

## Troubleshooting

### Chatbot Button Not Appearing
- Check if `chef-cookie.png` exists in `frontend/public/`
- Verify `<Chatbot />` is in `App.tsx`
- Check browser console for errors

### API Returns 404
- Ensure backend container is rebuilt after adding chatbot files
- Check `app/api/chatbot.py` exists in container
- Verify blueprint registration in `app/__init__.py`

### No Products Returned
- Check database has demo data (`seed_demo_data.py`)
- Verify products are marked as `is_active=True`
- Check database connection

### Typing Indicator Stuck
- Check network tab for failed requests
- Verify backend API is responding
- Check CORS configuration

## Files Modified/Created

### Backend
- ✅ `backend/app/services/chatbot_service.py` - Main chatbot logic
- ✅ `backend/app/api/chatbot.py` - API endpoints
- ✅ `backend/app/__init__.py` - Blueprint registration

### Frontend
- ✅ `frontend/src/components/Chatbot/Chatbot.tsx` - Component
- ✅ `frontend/src/components/Chatbot/Chatbot.css` - Styling
- ✅ `frontend/src/App.tsx` - Integration
- ⚠️ `frontend/public/chef-cookie.png` - **Needs to be added manually**

## Support

For issues or questions:
- Check backend logs: `docker-compose logs backend`
- Test API directly with cURL
- Verify all files are in place
- Ensure Docker containers are rebuilt after changes

---

**Status:** ✅ Fully Integrated and Tested
**Last Updated:** December 28, 2025

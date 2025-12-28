"""
Chatbot service for Cookie Shop assistant
"""
from typing import Dict, List, Optional
from app.models.product import Product
from app.models.category import Category
from sqlalchemy import func


class ChatbotService:
    """Service for handling chatbot queries and responses"""

    @staticmethod
    def get_response(user_message: str) -> Dict:
        """
        Process user message and generate appropriate response

        Args:
            user_message: User's query

        Returns:
            Dict with response type, message, and optional data
        """
        message_lower = user_message.lower().strip()

        # Greeting responses
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
            return ChatbotService._greeting_response()

        # Product recommendations by occasion
        if any(word in message_lower for word in ['birthday', 'party', 'celebration', 'gift']):
            return ChatbotService._occasion_response(message_lower)

        # Dietary/allergen queries
        if any(word in message_lower for word in ['allergy', 'allergic', 'allergen', 'vegan', 'gluten']):
            return ChatbotService._allergen_response(message_lower)

        # Ingredient queries
        if any(word in message_lower for word in ['ingredient', 'contain', 'made of', 'recipe']):
            return ChatbotService._ingredient_response(message_lower)

        # Stock availability
        if any(word in message_lower for word in ['stock', 'available', 'in stock', 'availability']):
            return ChatbotService._stock_response()

        # Price queries
        if any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap', 'budget']):
            return ChatbotService._price_response(message_lower)

        # Product search
        if any(word in message_lower for word in ['chocolate', 'vanilla', 'oatmeal', 'peanut', 'cookie']):
            return ChatbotService._product_search(message_lower)

        # Help/general query
        if any(word in message_lower for word in ['help', 'what can you', 'how can you']):
            return ChatbotService._help_response()

        # Default response
        return ChatbotService._default_response()

    @staticmethod
    def _greeting_response() -> Dict:
        """Greeting response"""
        return {
            'type': 'greeting',
            'message': "Hi there! I'm Chef Cookie, your personal cookie assistant! 🍪\n\n"
                      "I can help you:\n"
                      "• Find the perfect cookies for any occasion\n"
                      "• Check ingredients and allergens\n"
                      "• See what's in stock\n"
                      "• Get cookie recommendations\n\n"
                      "What would you like to know?",
            'suggestions': [
                'Show me birthday cookies',
                'What cookies are in stock?',
                'I need gluten-free options',
                'Show me chocolate cookies'
            ]
        }

    @staticmethod
    def _occasion_response(message: str) -> Dict:
        """Recommend cookies for specific occasions"""
        products = Product.query.filter_by(is_active=True).all()

        occasion = None
        if 'birthday' in message:
            occasion = 'birthday'
            intro = "🎂 Perfect for birthdays! Here are our most popular celebration cookies:"
        elif 'party' in message:
            occasion = 'party'
            intro = "🎉 Party time! These cookies are crowd-pleasers:"
        elif 'gift' in message:
            occasion = 'gift'
            intro = "🎁 Great gift choices! These premium cookies are perfect:"
        else:
            occasion = 'celebration'
            intro = "🎊 For your special celebration, I recommend:"

        # Prioritize featured products and high-rated items
        recommended = [p for p in products if p.is_featured][:4]

        if not recommended:
            recommended = products[:4]

        product_list = []
        for product in recommended:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'image_url': product.image_url,
                'description': product.description,
                'in_stock': product.in_stock
            })

        return {
            'type': 'recommendation',
            'message': intro,
            'products': product_list,
            'suggestions': [
                'Tell me about ingredients',
                'What\'s in stock?',
                'Show me more options'
            ]
        }

    @staticmethod
    def _allergen_response(message: str) -> Dict:
        """Filter products by allergens"""
        products = Product.query.filter_by(is_active=True).all()

        allergen_free = []
        allergen_type = None

        if 'gluten' in message:
            allergen_type = 'gluten'
            allergen_free = [p for p in products if p.allergens and 'Wheat' not in p.allergens and 'Gluten' not in p.allergens]
        elif 'dairy' in message or 'milk' in message:
            allergen_type = 'dairy'
            allergen_free = [p for p in products if p.allergens and 'Dairy' not in p.allergens and 'Milk' not in p.allergens]
        elif 'nut' in message or 'peanut' in message:
            allergen_type = 'nut'
            allergen_free = [p for p in products if p.allergens and not any(a in ['Peanuts', 'Tree Nuts', 'Nuts'] for a in p.allergens)]
        elif 'egg' in message:
            allergen_type = 'egg'
            allergen_free = [p for p in products if p.allergens and 'Eggs' not in p.allergens]
        else:
            # General allergen inquiry
            return {
                'type': 'info',
                'message': "I can help you find cookies that are safe for your dietary needs! 🌟\n\n"
                          "Tell me what you need to avoid:\n"
                          "• Gluten-free\n"
                          "• Dairy-free\n"
                          "• Nut-free\n"
                          "• Egg-free\n\n"
                          "Or ask about a specific cookie's ingredients!",
                'suggestions': [
                    'Show gluten-free cookies',
                    'I need dairy-free options',
                    'What cookies have no nuts?'
                ]
            }

        if allergen_free:
            product_list = []
            for product in allergen_free[:5]:
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image_url': product.image_url,
                    'allergens': product.allergens or [],
                    'in_stock': product.in_stock
                })

            return {
                'type': 'allergen_safe',
                'message': f"Great news! Here are our {allergen_type}-free cookies: 🍪✨",
                'products': product_list,
                'suggestions': [
                    'Tell me the ingredients',
                    'What else is available?'
                ]
            }
        else:
            return {
                'type': 'info',
                'message': f"I'm sorry, we don't currently have {allergen_type}-free options in stock. "
                          f"But we're always adding new varieties! Check back soon or contact us for custom orders. 💝",
                'suggestions': [
                    'Show me all cookies',
                    'What\'s popular?'
                ]
            }

    @staticmethod
    def _ingredient_response(message: str) -> Dict:
        """Show ingredient information"""
        # Try to find specific product mentioned
        products = Product.query.filter_by(is_active=True).all()

        for product in products:
            if product.name.lower() in message:
                ingredients_text = ', '.join(product.ingredients) if product.ingredients else 'Not specified'
                allergens_text = ', '.join(product.allergens) if product.allergens else 'None listed'

                return {
                    'type': 'ingredients',
                    'message': f"**{product.name}** 🍪\n\n"
                              f"**Ingredients:**\n{ingredients_text}\n\n"
                              f"**Allergens:**\n{allergens_text}\n\n"
                              f"**Description:**\n{product.description}",
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'image_url': product.image_url
                    },
                    'suggestions': [
                        'Add to cart',
                        'Show similar cookies',
                        'Any allergen-free options?'
                    ]
                }

        # General ingredients info
        return {
            'type': 'info',
            'message': "I can tell you about the ingredients in any of our cookies! 📋\n\n"
                      "Just ask:\n"
                      "• 'What's in the chocolate chip cookies?'\n"
                      "• 'Tell me about oatmeal cookie ingredients'\n"
                      "• Or click on any cookie to see details!",
            'suggestions': [
                'Show all cookies',
                'What cookies are gluten-free?'
            ]
        }

    @staticmethod
    def _stock_response() -> Dict:
        """Show in-stock products"""
        in_stock = Product.query.filter_by(is_active=True, in_stock=True).all()

        if in_stock:
            product_list = []
            for product in in_stock[:6]:
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image_url': product.image_url,
                    'stock_quantity': product.stock_quantity,
                    'in_stock': True
                })

            return {
                'type': 'stock',
                'message': f"We have {len(in_stock)} delicious cookies in stock right now! 🎉",
                'products': product_list,
                'suggestions': [
                    'Show me chocolate cookies',
                    'What\'s on sale?',
                    'Birthday recommendations'
                ]
            }
        else:
            return {
                'type': 'info',
                'message': "We're currently restocking! Check back soon for fresh batches. 🍪",
                'suggestions': [
                    'View all products',
                    'Contact us'
                ]
            }

    @staticmethod
    def _price_response(message: str) -> Dict:
        """Show products by price range"""
        products = Product.query.filter_by(is_active=True).all()

        if 'cheap' in message or 'budget' in message or 'affordable' in message:
            # Show lower-priced items
            sorted_products = sorted(products, key=lambda p: p.price)[:5]
            intro = "Here are our most budget-friendly options! 💰"
        elif 'expensive' in message or 'premium' in message:
            # Show higher-priced items
            sorted_products = sorted(products, key=lambda p: p.price, reverse=True)[:5]
            intro = "Our premium selection! ⭐"
        else:
            # Show all with prices
            sorted_products = products[:5]
            intro = "Here's our price range:"

        product_list = []
        for product in sorted_products:
            product_list.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'image_url': product.image_url,
                'in_stock': product.in_stock
            })

        return {
            'type': 'price_info',
            'message': intro,
            'products': product_list,
            'suggestions': [
                'Show all cookies',
                'What\'s in stock?'
            ]
        }

    @staticmethod
    def _product_search(message: str) -> Dict:
        """Search for specific products"""
        products = Product.query.filter_by(is_active=True).all()

        # Search by name or description
        found_products = []
        search_terms = ['chocolate', 'vanilla', 'oatmeal', 'peanut', 'butter', 'chip', 'raisin']

        for term in search_terms:
            if term in message:
                found_products = [
                    p for p in products
                    if term in p.name.lower() or (p.description and term in p.description.lower())
                ]
                break

        if found_products:
            product_list = []
            for product in found_products[:5]:
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'image_url': product.image_url,
                    'description': product.description,
                    'in_stock': product.in_stock
                })

            return {
                'type': 'search_results',
                'message': f"Found {len(found_products)} delicious matches! 🍪",
                'products': product_list,
                'suggestions': [
                    'Tell me the ingredients',
                    'What else do you have?'
                ]
            }
        else:
            return {
                'type': 'no_results',
                'message': "Hmm, I couldn't find exactly what you're looking for. "
                          "But we have many other delicious options! Want to see what's available?",
                'suggestions': [
                    'Show all cookies',
                    'What\'s in stock?',
                    'Birthday recommendations'
                ]
            }

    @staticmethod
    def _help_response() -> Dict:
        """Help/capabilities response"""
        return {
            'type': 'help',
            'message': "I'm Chef Cookie, and I'm here to help! 👨‍🍳\n\n"
                      "**I can help you with:**\n"
                      "🍪 Find cookies by flavor or type\n"
                      "🎂 Get recommendations for occasions\n"
                      "📋 Check ingredients and allergens\n"
                      "📦 See what's in stock\n"
                      "💰 Find cookies in your budget\n"
                      "🌟 Suggest the perfect cookies for you!\n\n"
                      "Just ask me anything!",
            'suggestions': [
                'Show birthday cookies',
                'What\'s gluten-free?',
                'Show me chocolate cookies',
                'What\'s in stock?'
            ]
        }

    @staticmethod
    def _default_response() -> Dict:
        """Default response when query is unclear"""
        return {
            'type': 'clarification',
            'message': "I'm not quite sure what you're looking for, but I'm here to help! 🤔\n\n"
                      "You can ask me about:\n"
                      "• Specific cookie flavors\n"
                      "• Cookies for occasions (birthdays, parties, gifts)\n"
                      "• Ingredients and allergens\n"
                      "• What's in stock\n"
                      "• Price ranges",
            'suggestions': [
                'Show all cookies',
                'What can you help with?',
                'Birthday recommendations',
                'Show chocolate cookies'
            ]
        }

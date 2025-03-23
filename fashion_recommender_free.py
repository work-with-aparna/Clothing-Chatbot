import streamlit as st
import sqlite3
import pandas as pd
import requests

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('fashion_dataset.db')
    return conn

def is_fashion_related(query):
    """Check if the query is fashion-related"""
    fashion_keywords = {
        'clothing', 'fashion', 'wear', 'dress', 'shirt', 'pants', 'jeans', 'skirt',
        'shoes', 'boots', 'sneakers', 'jacket', 'coat', 'sweater', 'top', 'bottom',
        'outfit', 'style', 'accessory', 'accessories', 'bag', 'scarf', 'hat',
        'belt', 'jewelry', 'necklace', 'bracelet', 'ring', 'earrings', 'watch',
        'formal', 'casual', 'trendy', 'vintage', 'modern', 'classic', 'elegant',
        'comfortable', 'fit', 'size', 'color', 'pattern', 'design', 'brand',
        'fashion', 'wardrobe', 'closet', 'outfit', 'attire', 'apparel', 'wear',
        'clothes', 'clothing', 'dressed', 'dressing', 'dressed', 'wearing',
        'white', 'black', 'blue', 'red', 'green', 'yellow', 'purple', 'pink',
        'brown', 'grey', 'gray', 'orange', 'cotton', 'leather', 'silk', 'wool',
        'denim', 'linen', 'polyester', 'suit', 'blazer', 'blouse', 'hoodie',
        'sweatshirt', 'cardigan', 'dress shirt', 't-shirt', 'tee', 'tank top',
        'shorts', 'leggings', 'socks', 'underwear', 'swimwear', 'beachwear'
    }
    
    query_words = set(query.lower().split())
    return bool(query_words & fashion_keywords)

def search_products(query):
    """Search for products in the database based on user query"""
    conn = get_db_connection()
    
    # Extract color and product type from query
    query = query.lower()
    words = query.split()
    
    # Build the SQL query dynamically
    sql_conditions = []
    params = []
    
    # Add condition for each word in the query
    for word in words:
        sql_conditions.append("""
            (LOWER(name) LIKE ? OR 
             LOWER(description) LIKE ? OR 
             LOWER(colour) LIKE ? OR 
             LOWER(brand) LIKE ?)
        """)
        param = f"%{word}%"
        params.extend([param, param, param, param])
    
    # Construct the final SQL query
    sql = f"""
    SELECT name as product_name, description, price, colour, brand, avg_rating
    FROM fashion_items
    WHERE {' OR '.join(sql_conditions)}
    ORDER BY avg_rating DESC NULLS LAST
    LIMIT 10
    """
    
    # Debug information
    st.sidebar.markdown("### Debug Info")
    st.sidebar.write("Search terms:", words)
    
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        st.sidebar.write("Found items:", len(df))
        return df
    except Exception as e:
        st.sidebar.error(f"Database error: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_ai_response(query):
    """Generate AI response using HuggingFace's free inference API"""
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
    headers = {"Content-Type": "application/json"}
    
    # Create a fashion-specific prompt
    prompt = f"""You are a helpful fashion advisor. A customer is asking about: '{query}'
    Please provide specific fashion advice and recommendations. Focus on:
    1. Style suggestions
    2. Color combinations
    3. Occasion appropriateness
    4. Practical tips
    Keep the response friendly, specific, and fashion-focused."""
    
    try:
        # Make request to HuggingFace API
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_length": 150}}
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                    generated_text = result[0].get('generated_text', '')
                    # Clean up the response to keep only the relevant part
                    if 'Assistant:' in generated_text:
                        generated_text = generated_text.split('Assistant:')[1].strip()
                    return generated_text
            except:
                pass
        
        # If any issues with API or response format, use enhanced fallback
        return get_enhanced_fallback_response(query)
            
    except Exception as e:
        return get_enhanced_fallback_response(query)

def get_enhanced_fallback_response(query):
    """Provide an enhanced fallback response with specific fashion advice"""
    query = query.lower()
    
    # More detailed and specific responses
    enhanced_responses = {
        'top': {
            'casual': "For a casual top, I recommend a well-fitted cotton t-shirt or a comfortable blouse. Consider these style tips:\n- Choose breathable fabrics for comfort\n- Solid colors are versatile and easy to mix\n- Look for details like interesting necklines\n- Pair with jeans or skirts for a complete look",
            'formal': "For a formal top, consider a silk blouse or a structured shirt. Style tips:\n- Stick to classic colors like white, black, or navy\n- Look for quality materials that drape well\n- Choose appropriate necklines for the occasion\n- Consider the fit around shoulders and bust",
            'general': "When choosing a top, consider these key factors:\n- Your body type and what styles flatter you\n- The occasion you're dressing for\n- The season and weather\n- Your existing wardrobe for mix-and-match options"
        },
        'dress': {
            'casual': "For a casual dress, try an A-line or wrap style. Key recommendations:\n- Choose comfortable, breathable fabrics\n- Look for versatile lengths (knee-length is always safe)\n- Consider patterns that suit your style\n- Add pockets for practicality",
            'formal': "For a formal dress, focus on elegant cuts and quality materials. Tips:\n- Choose appropriate length for the occasion\n- Consider the venue and dress code\n- Look for flattering silhouettes\n- Pay attention to the fit at waist and hips",
            'general': "When selecting a dress, keep in mind:\n- Your body shape and what styles complement it\n- The event or occasion\n- The season and appropriate fabrics\n- Accessorizing options"
        },
        'jeans': "For jeans, focus on fit and versatility. Consider:\n- Your body type and preferred rise (high/mid/low)\n- Stretch content for comfort\n- Wash (dark washes are more versatile)\n- Length and hem style",
        'shoes': "When choosing shoes, balance style and comfort:\n- Consider the occasion and outfit pairing\n- Look for quality materials and construction\n- Ensure proper fit and comfort\n- Think about versatility in your wardrobe",
        'jacket': "For jackets, consider these factors:\n- The climate and season\n- Your typical daily activities\n- Versatility with your existing wardrobe\n- Quality of construction and materials",
        'accessories': "When selecting accessories:\n- Choose pieces that complement your outfits\n- Consider your personal style\n- Think about versatility\n- Focus on quality over quantity"
    }
    
    # Check for specific terms in query
    for key, responses in enhanced_responses.items():
        if key in query:
            if isinstance(responses, dict):
                if 'formal' in query:
                    return responses['formal']
                elif 'casual' in query:
                    return responses['casual']
                else:
                    return responses['general']
            else:
                return responses
    
    # If no specific match, provide a detailed general response
    return f"""Let me help you with your fashion query about '{query}'. Here are some general style tips:
    1. Consider your body type and what styles make you feel confident
    2. Think about the occasion and appropriate dress codes
    3. Look for quality materials and good fit
    4. Choose versatile pieces that can be mixed and matched
    5. Pay attention to comfort as well as style"""

# Streamlit UI
st.title("👗 Fashion Product Recommender (Free Version)")
st.write("Ask me about fashion products! For example: 'Suggest a white top' or 'Recommend blue jeans'")

# Add a sidebar with information about the free version
with st.sidebar:
    st.info("""
    This is the free version of the Fashion Recommender that uses:
    - HuggingFace's free inference API for AI responses
    - Local database for product search
    - Pre-written responses as fallback
    
    No API key required! 🎉
    """)
    
    st.markdown("""
    ### What can I ask?
    You can ask about:
    - Clothing recommendations
    - Style advice
    - Specific fashion items
    - Color combinations
    - Outfit suggestions
    """)

# User input
user_query = st.text_input("What are you looking for?")

if user_query:
    # Check if the query is fashion-related
    if not is_fashion_related(user_query):
        st.warning("""
        👋 I'm a fashion-focused chatbot! I can only help you with:
        - Fashion advice
        - Clothing recommendations
        - Style suggestions
        - Outfit ideas
        
        Please ask me something about fashion or clothing instead!
        """)
    else:
        # Search for products
        results = search_products(user_query)
        
        if not results.empty:
            st.write(f"Found {len(results)} products matching your query:")
            
            # Display products in a grid-like layout
            cols = st.columns(2)
            for idx, row in results.iterrows():
                with cols[idx % 2]:
                    st.subheader(row['product_name'])
                    st.write(f"Brand: {row['brand']}")
                    st.write(f"Color: {row['colour']}")
                    st.write(row['description'])
                    st.write(f"Price: ${row['price']:.2f}")
                    if pd.notna(row['avg_rating']):
                        st.write(f"Rating: {row['avg_rating']:.1f}/5")
                    st.markdown("---")
        else:
            # Get AI-generated response when no products are found
            ai_response = get_ai_response(user_query)
            st.info("I couldn't find exact matches in our database, but here's a suggestion:")
            st.write(ai_response) 
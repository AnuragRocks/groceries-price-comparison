"""Test the search functionality"""
import csv
from difflib import SequenceMatcher

# Load products
products = []
with open('d:/projects/Price Comparison/database/product_prices.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    products = list(reader)

print(f"Total products: {len(products)}")

# Test search for "chicken breast"
search_term = "chicken breast"
search_lower = search_term.lower()
search_words = set(search_lower.split())
min_similarity = 0.6

results = []
for product in products:
    name = product.get('product_name', '').lower()
    description = product.get('description', '').lower()
    search_field = product.get('search_term', '').lower()
    
    # Check if search term is in the main fields (exact substring match)
    exact_match = (search_lower in name or 
                  search_lower in description or 
                  search_lower in search_field)
    
    # Check if individual words from search are in the product fields
    name_words = set(name.split())
    word_match = len(search_words.intersection(name_words)) > 0 or \
                search_words.issubset(set(search_field.split()))
    
    similarity = SequenceMatcher(None, search_lower, name).ratio()
    
    if exact_match or (word_match and similarity > min_similarity):
        
        results.append({
            'name': product.get('product_name', ''),
            'search_term': product.get('search_term', ''),
            'store': product.get('store', ''),
            'price': product.get('price', ''),
            'similarity': similarity
        })

print(f"\nFound {len(results)} results for '{search_term}'")
print("\nTop 10 results:")
for i, r in enumerate(results[:10], 1):
    print(f"{i}. {r['name'][:50]}")
    print(f"   Search field: {r['search_term']}, Store: {r['store']}, Price: {r['price']}")
    print(f"   Similarity: {r['similarity']:.3f}\n")

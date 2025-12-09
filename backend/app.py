"""
Flask Web Application for Product Price Comparison
"""

from flask import Flask, render_template, request, jsonify
import csv
import re
from typing import List, Dict
from difflib import SequenceMatcher

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')


class ProductComparator:
    """Compare product prices from the scraped data"""
    
    def __init__(self, csv_file: str = '../database/product_prices.csv'):
        self.csv_file = csv_file
        self.products = []
        self.load_data()
    
    def load_data(self):
        """Load product data from CSV"""
        import os
        try:
            # Try multiple possible paths
            possible_paths = [
                self.csv_file,
                os.path.join(os.path.dirname(__file__), '..', 'database', 'product_prices.csv'),
                'database/product_prices.csv',
                '../database/product_prices.csv'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"✓ Found CSV at: {path}")
                    with open(path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.products = list(reader)
                    print(f"✓ Loaded {len(self.products)} products")
                    return
            
            print(f"✗ CSV file not found. Tried: {possible_paths}")
            self.products = []
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
            self.products = []
    
    def get_available_categories(self) -> List[str]:
        """Get list of available product categories"""
        search_terms = set()
        for product in self.products:
            term = product.get('search_term', '').strip()
            if term:
                search_terms.add(term)
        return sorted(search_terms)
    
    def normalize_price(self, price_str: str) -> float:
        """Convert price string to float"""
        if not price_str:
            return float('inf')
        price_cleaned = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return float(price_cleaned)
        except ValueError:
            return float('inf')
    
    def normalize_quantity(self, quantity: str, unit: str) -> float:
        """Normalize quantity to grams for comparison"""
        if not quantity:
            return 0
        try:
            qty = float(quantity)
        except ValueError:
            return 0
        
        unit_lower = unit.lower() if unit else ""
        
        if 'kg' in unit_lower:
            return qty * 1000
        elif 'g' in unit_lower:
            return qty
        elif 'lb' in unit_lower:
            return qty * 453.592
        elif 'oz' in unit_lower:
            return qty * 28.3495
        elif 'ml' in unit_lower:
            return qty
        elif 'l' in unit_lower or 'litre' in unit_lower or 'liter' in unit_lower:
            return qty * 1000
        else:
            return qty
    
    def calculate_unit_price(self, price: float, quantity: float) -> float:
        """Calculate price per 100g/100ml"""
        if quantity == 0:
            return float('inf')
        return (price / quantity) * 100
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def search_products(self, search_term: str, min_similarity: float = 0.6) -> List[Dict]:
        """Search for products matching the search term"""
        results = []
        search_lower = search_term.lower()
        search_words = set(search_lower.split())
        
        for product in self.products:
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
            
            # High similarity score for fuzzy matching
            similarity = self.similarity_score(search_lower, name)
            
            if exact_match or (word_match and similarity > min_similarity):
                
                price = self.normalize_price(product.get('price', ''))
                quantity = self.normalize_quantity(
                    product.get('quantity', ''),
                    product.get('unit', '')
                )
                
                product_info = {
                    'product_name': product.get('product_name', 'N/A'),
                    'price': price,
                    'price_display': product.get('price', 'N/A'),
                    'quantity': product.get('quantity', 'N/A'),
                    'unit': product.get('unit', 'N/A'),
                    'quantity_normalized': quantity,
                    'unit_price': self.calculate_unit_price(price, quantity),
                    'brand': product.get('brand', 'N/A'),
                    'store': product.get('store', 'N/A'),
                    'category': product.get('category', 'N/A'),
                    'description': product.get('description', 'N/A'),
                    'product_url': product.get('product_url', '')
                }
                
                results.append(product_info)
        
        return results
    
    def compare_products(self, search_term: str, sort_by: str = 'price') -> List[Dict]:
        """Search and compare products"""
        results = self.search_products(search_term)
        
        if not results:
            return []
        
        if sort_by == 'price':
            results.sort(key=lambda x: x['price'])
        elif sort_by == 'unit_price':
            results.sort(key=lambda x: x['unit_price'])
        elif sort_by == 'quantity':
            results.sort(key=lambda x: x['quantity_normalized'], reverse=True)
        
        return results


# Initialize comparator
comparator = ProductComparator()


@app.route('/')
def index():
    """Home page"""
    categories = comparator.get_available_categories()
    print(f"Categories available: {len(categories)}")
    print(f"Total products loaded: {len(comparator.products)}")
    return render_template('index.html', categories=categories)


@app.route('/search', methods=['POST'])
def search():
    """Search for products"""
    data = request.get_json()
    search_term = data.get('search_term', '')
    sort_by = data.get('sort_by', 'price')
    
    if not search_term:
        return jsonify({'error': 'Please enter a search term'}), 400
    
    results = comparator.compare_products(search_term, sort_by)
    
    if not results:
        return jsonify({'error': f'No products found matching "{search_term}"'}), 404
    
    # Format results for JSON
    formatted_results = []
    for product in results:
        formatted_product = {
            'product_name': product['product_name'],
            'price_display': product['price_display'],
            'quantity': product['quantity'],
            'unit': product['unit'],
            'store': product['store'],
            'brand': product['brand'],
            'category': product['category'],
            'description': product['description'],
            'product_url': product['product_url']
        }
        
        if product['unit_price'] != float('inf'):
            formatted_product['unit_price'] = f"${product['unit_price']:.2f}"
        else:
            formatted_product['unit_price'] = 'N/A'
        
        formatted_results.append(formatted_product)
    
    return jsonify({
        'results': formatted_results,
        'count': len(formatted_results),
        'search_term': search_term
    })


@app.route('/refresh-data', methods=['POST'])
def refresh_data():
    """Reload CSV data"""
    comparator.load_data()
    categories = comparator.get_available_categories()
    return jsonify({
        'success': True,
        'categories': categories,
        'product_count': len(comparator.products)
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

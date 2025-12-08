"""
Product Price Comparison Tool
Search for products and compare prices across stores
"""

import csv
import re
from typing import List, Dict
from difflib import SequenceMatcher


class ProductComparator:
    """Compare product prices from the scraped data"""
    
    def __init__(self, csv_file: str = 'product_prices.csv'):
        self.csv_file = csv_file
        self.products = []
        self.load_data()
    
    def load_data(self):
        """Load product data from CSV"""
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.products = list(reader)
            print(f"✓ Loaded {len(self.products)} products from {self.csv_file}")
        except FileNotFoundError:
            print(f"⚠ CSV file '{self.csv_file}' not found. Please run the scraper first.")
            self.products = []
    
    def normalize_price(self, price_str: str) -> float:
        """Convert price string to float"""
        if not price_str:
            return float('inf')
        
        # Remove $ and any non-numeric characters except decimal point
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
        
        # Convert to grams
        if 'kg' in unit_lower:
            return qty * 1000
        elif 'g' in unit_lower:
            return qty
        elif 'lb' in unit_lower:
            return qty * 453.592
        elif 'oz' in unit_lower:
            return qty * 28.3495
        elif 'ml' in unit_lower:
            return qty  # Treat ml as g for comparison
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
    
    def search_products(self, search_term: str) -> List[Dict]:
        """
        Search for products with priority:
        1. Exact category match (search_term column)
        2. Partial category match
        3. Fuzzy search (product name/description)
        """
        results = []
        search_lower = search_term.lower().strip()
        
        # 1. Exact Category Match
        category_matches = []
        for product in self.products:
            if product.get('search_term', '').lower() == search_lower:
                category_matches.append(product)
        
        if category_matches:
            # If we found matches in the category, RETURN ONLY THESE
            # This ensures "milk" searches only return items from the "milk" category
            return self._process_results(category_matches)

        # 2. Partial Category Match (e.g., "mil" finding "milk")
        partial_cat_matches = []
        for product in self.products:
            if search_lower in product.get('search_term', '').lower():
                partial_cat_matches.append(product)
        
        if partial_cat_matches:
            return self._process_results(partial_cat_matches)

        # 3. Fuzzy/Global Search (Fallback)
        fuzzy_matches = []
        for product in self.products:
            name = product.get('product_name', '').lower()
            description = product.get('description', '').lower()
            
            if (search_lower in name or 
                search_lower in description or 
                self.similarity_score(search_lower, name) > 0.4): # Increased threshold slightly
                fuzzy_matches.append(product)
                
        return self._process_results(fuzzy_matches)

    def _process_results(self, raw_products: List[Dict]) -> List[Dict]:
        """Convert raw CSV rows into processed product objects"""
        processed_results = []
        for product in raw_products:
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
                'category': product.get('search_term', 'N/A').title(), # Use search_term as category name
                'description': product.get('description', 'N/A')
            }
            processed_results.append(product_info)
        return processed_results
    
    def compare_products(self, search_term: str, sort_by: str = 'price') -> List[Dict]:
        """
        Search and compare products
        sort_by options: 'price' (cheapest first), 'unit_price' (best value), 'quantity'
        """
        results = self.search_products(search_term)
        
        if not results:
            return []
        
        # Sort based on criteria
        if sort_by == 'price':
            results.sort(key=lambda x: x['price'])
        elif sort_by == 'unit_price':
            results.sort(key=lambda x: x['unit_price'])
        elif sort_by == 'quantity':
            results.sort(key=lambda x: x['quantity_normalized'], reverse=True)
        
        return results
    
    def display_comparison(self, search_term: str, sort_by: str = 'price', limit: int = None):
        """Display product comparison results with 'Right Answer' first"""
        results = self.compare_products(search_term, sort_by)
        
        print("\n" + "=" * 100)
        print(f"SEARCH RESULTS FOR: '{search_term}'")
        print("=" * 100)
        
        if not results:
            print(f"\n⚠ No products found in category matching '{search_term}'")
            print("\nPlease select from the available categories list above.")
            return
        
        # Identify the "Right Answer" (Best Option)
        # If sorting by price, it's the first one.
        best_option = results[0]
        
        print("\n" + "⭐ BEST OPTION (Lowest Price) ⭐".center(100))
        print("=" * 100)
        
        print(f"\n  Product:     {best_option['product_name'].upper()}")
        print(f"  Price:       {best_option['price_display']}")
        print(f"  Store:       {best_option['store']}")
        print(f"  Quantity:    {best_option['quantity']} {best_option['unit']}")
        if best_option['brand'] != 'N/A':
            print(f"  Brand:       {best_option['brand']}")
        print("=" * 100)
        
        if len(results) > 1:
            print(f"\nComparing with {len(results)-1} other options (Sorted Low to High):")
            print("-" * 100)
            
            # Header for listing
            print(f"{'#':<4} {'Price':<10} {'Store':<20} {'Product Name':<50}")
            print("-" * 100)

            display_results = results[1:] # Skip the first one as it's already shown
            if limit:
                display_results = display_results[:limit-1]
            
            for i, product in enumerate(display_results, 1):
                p_str = product['price_display']
                s_str = product['store'][:18]
                n_str = product['product_name'][:48]
                print(f"{i:<4} {p_str:<10} {s_str:<20} {n_str:<50}")
            
            print("-" * 100)
            if limit and len(results) > limit:
                print(f"... and {len(results) - limit} more options.")


def main():
    """Interactive product comparison"""
    print("\n" + "=" * 100)
    print("PRODUCT PRICE COMPARISON TOOL")
    print("=" * 100)
    
    comparator = ProductComparator()
    
    if not comparator.products:
        print("\n⚠ No data available. Please run 'python product_price_scraper.py' first.")
        return
    
    # Get unique search terms/categories from the data
    search_terms = set()
    for product in comparator.products:
        term = product.get('search_term', '').strip()
        if term:
            search_terms.add(term)
    
    search_terms = sorted(search_terms)
    
    print("\n" + "=" * 100)
    print("AVAILABLE PRODUCT CATEGORIES:")
    print("=" * 100)
    print("\nYou have data for the following products:")
    print("-" * 100)
    
    # Display in columns
    for i in range(0, len(search_terms), 3):
        row = search_terms[i:i+3]
        print("  " + "".join(f"{term:<30}" for term in row))
    
    print("-" * 100)
    print(f"\nTotal: {len(search_terms)} product categories")
    
    print("\n" + "=" * 100)
    print("How would you like to compare prices?")
    print("  1. Cheapest price first (default)")
    print("  2. Best value (price per 100g/100ml)")
    print("  3. Largest quantity first")
    
    sort_choice = input("\nEnter choice (1-3) or press Enter for default: ").strip()
    
    sort_map = {
        '1': 'price',
        '2': 'unit_price',
        '3': 'quantity',
        '': 'price'
    }
    
    sort_by = sort_map.get(sort_choice, 'price')
    
    print("\n" + "-" * 100)
    print("Enter product name from the list above (or 'quit' to exit)")
    print("-" * 100)
    
    while True:
        search_term = input("\nSearch for product: ").strip()
        
        if search_term.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using the Price Comparison Tool!")
            break
        
        if not search_term:
            print("Please enter a product name.")
            continue
        
        comparator.display_comparison(search_term, sort_by=sort_by, limit=20)
        
        print("\n" + "=" * 100)


if __name__ == "__main__":
    main()

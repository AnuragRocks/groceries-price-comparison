
from compare_prices import ProductComparator

def test_search():
    comparator = ProductComparator()
    print("Loaded products:", len(comparator.products))
    
    term = "milk"
    print(f"\nSearching for '{term}'...")
    results = comparator.compare_products(term, sort_by='price')
    
    print(f"Found {len(results)} results.")
    for r in results:
        print(f"{r['product_name']} - ${r['price_display']} (Category: {r.get('search_term', 'N/A')})")

if __name__ == "__main__":
    test_search()

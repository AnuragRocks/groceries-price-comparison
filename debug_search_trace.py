
from compare_prices import ProductComparator

def debug_search():
    c = ProductComparator()
    print(f"Loaded {len(c.products)} products")
    
    term = "milk"
    search_lower = term.lower().strip()
    print(f"Searching for '{search_lower}'")
    
    # Debug loop
    matches = 0
    for i, p in enumerate(c.products):
        st = p.get('search_term', '')
        if st.lower() == search_lower:
            matches += 1
        
        if i < 5:
            print(f"Item {i}: '{st}' (len={len(st)})")
            
    print(f"Total Exact Matches manual check: {matches}")
    
    # Call actual method
    results = c.search_products(term)
    print(f"Method returned {len(results)} results")
    if results:
        print(f"Top result category: {results[0].get('category')}")

if __name__ == "__main__":
    debug_search()

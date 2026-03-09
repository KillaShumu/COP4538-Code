import time
import random
import string

# ============================================================================
# Search Algorithm Implementations
# ============================================================================

def linear_search(contact_id, contacts):
    """Linear search to find a contact by name.
    
    Time Complexity: O(n) where n is the number of contacts.
    Space Complexity: O(1)
    
    Args:
        contact_id: The contact name to search for.
        contacts: A list of contact names.
    
    Returns:
        A tuple (index, contact_name) if found, otherwise None.
    """
    contact_id_lower = contact_id.lower()
    for i, contact in enumerate(contacts):
        if contact.lower() == contact_id_lower:
            return (i, contact)
    return None


def binary_search(contact_id, sorted_contacts):
    """Binary search to find a contact by name in a sorted list.
    
    Time Complexity: O(log n) where n is the number of contacts.
    Space Complexity: O(1)
    
    Args:
        contact_id: The contact name to search for.
        sorted_contacts: A sorted list of contact names.
    
    Returns:
        A tuple (index, contact_name) if found, otherwise None.
    """
    if not sorted_contacts:
        return None
    
    left = 0
    right = len(sorted_contacts) - 1
    contact_id_lower = contact_id.lower()
    
    while left <= right:
        mid = (left + right) // 2
        mid_contact = sorted_contacts[mid]
        mid_contact_lower = mid_contact.lower()
        
        if mid_contact_lower == contact_id_lower:
            return (mid, mid_contact)
        elif mid_contact_lower < contact_id_lower:
            left = mid + 1
        else:
            right = mid - 1
    
    return None


def quick_sort(arr, key=lambda x: x):
    """Quick sort implementation.
    
    Time Complexity: O(n log n) average case.
    Space Complexity: O(n) for the new lists created.
    """
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[len(arr) // 2]
    pivot_key = key(pivot)
    left = [x for x in arr if key(x) < pivot_key]
    middle = [x for x in arr if key(x) == pivot_key]
    right = [x for x in arr if key(x) > pivot_key]
    return quick_sort(left, key) + middle + quick_sort(right, key)


# ============================================================================
# Benchmark Test Suite
# ============================================================================

def generate_test_data(size, seed=42):
    """Generate a list of random contact names.
    
    Args:
        size: Number of contacts to generate.
        seed: Random seed for reproducibility.
    
    Returns:
        A list of random contact names.
    """
    random.seed(seed)
    first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 
                   'Henry', 'Iris', 'Jack', 'Kate', 'Liam', 'Mia', 'Noah', 'Olivia']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
                  'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez']
    
    contacts = []
    for i in range(size):
        first = random.choice(first_names)
        last = random.choice(last_names)
        contacts.append(f"{first} {last}")
    
    return contacts


def benchmark_search(name, search_func, test_data, search_targets, iterations=1):
    """Benchmark a search function.
    
    Args:
        name: Name of the search algorithm.
        search_func: The search function to benchmark.
        test_data: The data to search in.
        search_targets: List of target contacts to search for.
        iterations: Number of times to repeat the search.
    
    Returns:
        A tuple (total_time, avg_time_per_search)
    """
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        for target in search_targets:
            search_func(target, test_data)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    avg_time = total_time / (iterations * len(search_targets))
    
    return total_time, avg_time


def run_benchmark_suite():
    """Run comprehensive benchmarks comparing linear vs binary search."""
    
    print("=" * 80)
    print("BENCHMARK: Linear Search vs Binary Search")
    print("=" * 80)
    print()
    
    # Test with different dataset sizes
    test_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
    
    results = {
        'Linear': [],
        'Binary': [],
        'Speedup': []
    }
    
    for size in test_sizes:
        print(f"Testing with {size:,} contacts...")
        
        # Generate test data
        contacts = generate_test_data(size)
        sorted_contacts = quick_sort(contacts, key=lambda x: x.lower())
        
        # Select random search targets (from middle, end, and various positions)
        num_searches = min(100, size // 10)
        search_targets = random.sample(sorted_contacts, min(num_searches, len(sorted_contacts)))
        
        # Benchmark linear search
        linear_total, linear_avg = benchmark_search(
            'Linear Search',
            linear_search,
            contacts,
            search_targets,
            iterations=1
        )
        
        # Benchmark binary search
        binary_total, binary_avg = benchmark_search(
            'Binary Search',
            binary_search,
            sorted_contacts,
            search_targets,
            iterations=1
        )
        
        # Calculate speedup
        speedup = linear_total / binary_total if binary_total > 0 else 0
        
        results['Linear'].append(linear_avg)
        results['Binary'].append(binary_avg)
        results['Speedup'].append(speedup)
        
        print(f"  Linear Search:  {linear_avg:.9f} seconds (avg per search)")
        print(f"  Binary Search:  {binary_avg:.9f} seconds (avg per search)")
        print(f"  Speedup:        {speedup:.2f}x faster")
        print()
    
    # Print detailed results table
    print("=" * 80)
    print("DETAILED RESULTS TABLE")
    print("=" * 80)
    print(f"{'Dataset Size':<15} {'Linear (μs)':<20} {'Binary (μs)':<20} {'Speedup':<15}")
    print("-" * 80)
    
    for i, size in enumerate(test_sizes):
        linear_us = results['Linear'][i] * 1e6
        binary_us = results['Binary'][i] * 1e6
        speedup = results['Speedup'][i]
        print(f"{size:<15,} {linear_us:<20.3f} {binary_us:<20.3f} {speedup:<15.2f}x")
    
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    print("Key Findings:")
    print(f"  • Average speedup: {sum(results['Speedup']) / len(results['Speedup']):.2f}x")
    print(f"  • Maximum speedup: {max(results['Speedup']):.2f}x (at {test_sizes[results['Speedup'].index(max(results['Speedup']))]:,} contacts)")
    print(f"  • Linear Search Time Growth: O(n)")
    print(f"  • Binary Search Time Growth: O(log n)")
    print()
    print("Efficiency Gain:")
    print(f"  For {test_sizes[-1]:,} contacts:")
    print(f"    Linear Search avg:  {results['Linear'][-1]*1e6:.3f} microseconds")
    print(f"    Binary Search avg:  {results['Binary'][-1]*1e6:.3f} microseconds")
    print(f"    Total Speedup:      {results['Speedup'][-1]:.2f}x faster")
    print()
    print("Theoretical Comparison:")
    print(f"  With N = {test_sizes[-1]:,}:")
    print(f"    Linear Search:  up to {test_sizes[-1]:,} comparisons")
    print(f"    Binary Search:  up to {test_sizes[-1].bit_length()} comparisons")
    print()


if __name__ == '__main__':
    run_benchmark_suite()
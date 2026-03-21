"""
Firebase Connection Test Script
Tests the Firebase connection and basic operations.
"""

from library_backend import LibraryManager

def test_firebase_connection():
    """Test Firebase connection and basic operations."""
    
    print("=" * 60)
    print("FIREBASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Initialize LibraryManager
        print("\n[Test 1] Initializing LibraryManager...")
        library = LibraryManager()
        print("[PASS] LibraryManager initialized successfully!")

        # Test 2: Check Firestore connection
        print("\n[Test 2] Testing Firestore connection...")
        inventory = library.get_inventory()
        print(f"[PASS] Firestore connection successful!")
        print(f"   Current inventory contains {len(inventory)} book(s)")

        # Test 3: Display current inventory
        if inventory:
            print("\n[Test 3] Current books in database:")
            for i, book in enumerate(inventory, 1):
                print(f"   {i}. {book['title']} by {book['author']}")
                print(f"      ISBN: {book['isbn']}, Available: {book['available_quantity']}")
        else:
            print("\n[Test 3] No books in database yet.")

        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED - Firebase connection is working!")
        print("=" * 60)
        return True

    except FileNotFoundError:
        print("\n[ERROR] serviceAccountKey.json not found!")
        print("   Please ensure the file is in the same directory as the script.")
        return False

    except Exception as e:
        print(f"\n[ERROR] Firebase connection failed!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\n   Possible issues:")
        print("   1. Invalid serviceAccountKey.json file")
        print("   2. Incorrect Firebase project configuration")
        print("   3. Network connectivity issues")
        print("   4. Firebase project permissions")
        return False

if __name__ == "__main__":
    test_firebase_connection()

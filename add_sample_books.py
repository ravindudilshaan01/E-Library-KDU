"""
Add Sample Books to Kothalawala Library
This script adds 10 popular real books to the Firebase database
"""

from library_backend import LibraryManager, Book

def add_sample_books():
    """Add 10 real popular books to the library database"""

    # Initialize library manager
    try:
        library = LibraryManager()
        print("[OK] Connected to Firebase database successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        return

    # Create 10 real popular books with proper ISBNs
    sample_books = [
        Book(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            isbn="978-0-06-112008-4",
            late_return_fee=15.0,
            available_quantity=3
        ),
        Book(
            title="1984",
            author="George Orwell",
            isbn="978-0-452-28423-4",
            late_return_fee=12.0,
            available_quantity=4
        ),
        Book(
            title="Pride and Prejudice",
            author="Jane Austen",
            isbn="978-0-14-143951-8",
            late_return_fee=10.0,
            available_quantity=2
        ),
        Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="978-0-7432-7356-5",
            late_return_fee=12.0,
            available_quantity=5
        ),
        Book(
            title="Harry Potter and the Philosopher's Stone",
            author="J.K. Rowling",
            isbn="978-0-7475-3269-9",
            late_return_fee=20.0,
            available_quantity=6
        ),
        Book(
            title="The Catcher in the Rye",
            author="J.D. Salinger",
            isbn="978-0-316-76948-0",
            late_return_fee=14.0,
            available_quantity=2
        ),
        Book(
            title="Lord of the Flies",
            author="William Golding",
            isbn="978-0-571-05686-2",
            late_return_fee=11.0,
            available_quantity=3
        ),
        Book(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            isbn="978-0-547-92822-7",
            late_return_fee=16.0,
            available_quantity=4
        ),
        Book(
            title="Fahrenheit 451",
            author="Ray Bradbury",
            isbn="978-1-4516-7331-9",
            late_return_fee=13.0,
            available_quantity=2
        ),
        Book(
            title="Jane Eyre",
            author="Charlotte Brontë",
            isbn="978-0-14-144114-6",
            late_return_fee=11.0,
            available_quantity=3
        )
    ]

    print(f"\n[ADDING BOOKS] Adding {len(sample_books)} books to the library...")
    print("=" * 60)

    # Add each book to the database
    successful_adds = 0
    for i, book in enumerate(sample_books, 1):
        print(f"{i:2d}. Adding: {book.title} by {book.author}")
        print(f"    ISBN: {book.isbn} | Copies: {book.available_quantity} | Late Fee: Rs.{book.late_return_fee}/day")

        try:
            if library.add_book(book):
                successful_adds += 1
                print(f"    [OK] Successfully added!")
            else:
                print(f"    [ERROR] Failed to add")
        except Exception as e:
            print(f"    [ERROR] Error: {e}")

        print()

    print("=" * 60)
    print(f"[SUMMARY] {successful_adds}/{len(sample_books)} books added successfully!")

    if successful_adds > 0:
        print("\n[SUCCESS] Books have been added to your Kothalawala Library database!")
        print("You can now view them in your Streamlit app by running:")
        print("   streamlit run app.py")
    else:
        print("\n[WARNING] No books were added. Please check your Firebase configuration.")

if __name__ == "__main__":
    add_sample_books()
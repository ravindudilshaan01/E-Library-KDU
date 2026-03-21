"""
Library Management System Backend
This module handles all backend operations for the library system using Firebase Firestore.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class Book:
    """
    Blueprint for a Book object.
    Represents a book with all its properties.
    """
    
    def __init__(self, title: str, author: str, isbn: str, 
                 late_return_fee: float = 1.0, available_quantity: int = 1):
        """
        Initialize a Book object.
        
        Args:
            title: The title of the book
            author: The author of the book
            isbn: The ISBN (International Standard Book Number)
            late_return_fee: Fee per day for late returns (default: 1.0)
            available_quantity: Number of copies available (default: 1)
        """
        self.title = title
        self.author = author
        self.isbn = isbn
        self.late_return_fee = late_return_fee
        self.available_quantity = available_quantity
    
    def to_dict(self) -> Dict:
        """
        Convert Book object to dictionary for Firebase storage.
        
        Returns:
            Dictionary representation of the book
        """
        return {
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'late_return_fee': self.late_return_fee,
            'available_quantity': self.available_quantity
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Book':
        """
        Create a Book object from a dictionary.
        
        Args:
            data: Dictionary containing book data
            
        Returns:
            Book object
        """
        return Book(
            title=data.get('title', ''),
            author=data.get('author', ''),
            isbn=data.get('isbn', ''),
            late_return_fee=data.get('late_return_fee', 1.0),
            available_quantity=data.get('available_quantity', 0)
        )
    
    def __str__(self) -> str:
        """String representation of the book."""
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"


class LibraryManager:
    """
    Manager class to handle all library operations with Firebase.
    Handles book management, borrowing, returning, and inventory tracking.
    """
    
    def __init__(self, service_account_path: str = 'serviceAccountKey.json'):
        """
        Initialize the Library Manager and connect to Firebase.
        
        Args:
            service_account_path: Path to the Firebase service account key JSON file
        """
        try:
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            
            # Get Firestore client
            self.db = firestore.client()
            self.books_collection = self.db.collection('books')
            self.transactions_collection = self.db.collection('transactions')
            
            print("[OK] Firebase connection established successfully!")

        except Exception as e:
            print(f"[ERROR] Error initializing Firebase: {e}")
            raise
    
    def add_book(self, book: Book) -> bool:
        """
        Add a new book to the Firestore database.
        
        Args:
            book: Book object to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use ISBN as document ID for easy retrieval
            self.books_collection.document(book.isbn).set(book.to_dict())
            print(f"[OK] Book added successfully: {book.title}")
            return True
        except Exception as e:
            print(f"[ERROR] Error adding book: {e}")
            return False
    
    def search_book(self, query: str, search_by: str = 'title') -> List[Dict]:
        """
        Search for books by title or author.
        
        Args:
            query: Search query string
            search_by: Field to search by ('title' or 'author')
            
        Returns:
            List of matching books as dictionaries
        """
        try:
            results = []
            
            # Get all books from Firestore
            books = self.books_collection.stream()
            
            # Filter books based on search criteria
            for book_doc in books:
                book_data = book_doc.to_dict()
                book_data['isbn'] = book_doc.id  # Add ISBN from document ID
                
                # Case-insensitive search
                if search_by == 'title' and query.lower() in book_data.get('title', '').lower():
                    results.append(book_data)
                elif search_by == 'author' and query.lower() in book_data.get('author', '').lower():
                    results.append(book_data)

            print(f"[OK] Found {len(results)} book(s) matching '{query}'")
            return results

        except Exception as e:
            print(f"[ERROR] Error searching books: {e}")
            return []
    
    def borrow_book(self, isbn: str, borrower_name: str) -> bool:
        """
        Borrow a book by reducing its available quantity.
        Creates a transaction record with borrow date.
        
        Args:
            isbn: ISBN of the book to borrow
            borrower_name: Name of the person borrowing the book
            
        Returns:
            True if successful, False otherwise
        """
        try:
            book_ref = self.books_collection.document(isbn)
            book_doc = book_ref.get()
            
            if not book_doc.exists:
                print(f"[ERROR] Book with ISBN {isbn} not found")
                return False

            book_data = book_doc.to_dict()
            available = book_data.get('available_quantity', 0)

            if available <= 0:
                print(f"[ERROR] No copies available for this book")
                return False
            
            # Reduce available quantity
            book_ref.update({'available_quantity': available - 1})
            
            # Create transaction record
            transaction_data = {
                'isbn': isbn,
                'title': book_data.get('title', ''),
                'borrower_name': borrower_name,
                'borrow_date': datetime.now(),
                'due_date': datetime.now() + timedelta(weeks=2),  # 2 weeks loan period
                'return_date': None,
                'late_fee': 0.0
            }
            
            self.transactions_collection.add(transaction_data)

            print(f"[OK] Book borrowed successfully by {borrower_name}")
            print(f"  Due date: {transaction_data['due_date'].strftime('%Y-%m-%d')}")
            return True

        except Exception as e:
            print(f"[ERROR] Error borrowing book: {e}")
            return False
    
    def return_book(self, isbn: str, borrower_name: str) -> Optional[float]:
        """
        Return a borrowed book and calculate late fee if applicable.
        Late fee is charged if the return is more than 2 weeks after borrowing.
        
        Args:
            isbn: ISBN of the book to return
            borrower_name: Name of the person returning the book
            
        Returns:
            Late fee amount if applicable, 0.0 if on time, None if error
        """
        try:
            # Find the active transaction for this book and borrower
            transactions = self.transactions_collection.where('isbn', '==', isbn)\
                                                       .where('borrower_name', '==', borrower_name)\
                                                       .where('return_date', '==', None)\
                                                       .limit(1)\
                                                       .stream()
            
            transaction_doc = None
            for trans in transactions:
                transaction_doc = trans
                break
            
            if not transaction_doc:
                print(f"[ERROR] No active borrow record found for {borrower_name} with ISBN {isbn}")
                return None

            transaction_data = transaction_doc.to_dict()

            # Get book data to retrieve late return fee
            book_ref = self.books_collection.document(isbn)
            book_doc = book_ref.get()

            if not book_doc.exists:
                print(f"[ERROR] Book with ISBN {isbn} not found")
                return None
            
            book_data = book_doc.to_dict()
            
            # Increase available quantity
            current_quantity = book_data.get('available_quantity', 0)
            book_ref.update({'available_quantity': current_quantity + 1})
            
            # Calculate late fee
            return_date = datetime.now()
            due_date = transaction_data['due_date']
            
            late_fee = 0.0
            if return_date > due_date:
                # Calculate days late
                days_late = (return_date - due_date).days
                late_fee_per_day = book_data.get('late_return_fee', 1.0)
                late_fee = days_late * late_fee_per_day

                print(f"[WARNING] Book returned {days_late} day(s) late")
                print(f"  Late fee: ${late_fee:.2f}")
            else:
                print(f"[OK] Book returned on time")
            
            # Update transaction record
            transaction_ref = self.transactions_collection.document(transaction_doc.id)
            transaction_ref.update({
                'return_date': return_date,
                'late_fee': late_fee
            })

            print(f"[OK] Book returned successfully by {borrower_name}")
            return late_fee

        except Exception as e:
            print(f"[ERROR] Error returning book: {e}")
            return None
    
    def get_inventory(self) -> List[Dict]:
        """
        Get all books in the library inventory.
        
        Returns:
            List of all books with their details
        """
        try:
            inventory = []
            
            books = self.books_collection.stream()
            
            for book_doc in books:
                book_data = book_doc.to_dict()
                book_data['isbn'] = book_doc.id  # Add ISBN from document ID
                inventory.append(book_data)

            print(f"[OK] Retrieved {len(inventory)} book(s) from inventory")
            return inventory

        except Exception as e:
            print(f"[ERROR] Error retrieving inventory: {e}")
            return []
    
    def get_book_by_isbn(self, isbn: str) -> Optional[Dict]:
        """
        Get a specific book by its ISBN.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            Book data as dictionary, or None if not found
        """
        try:
            book_doc = self.books_collection.document(isbn).get()
            
            if book_doc.exists:
                book_data = book_doc.to_dict()
                book_data['isbn'] = book_doc.id
                return book_data
            else:
                print(f"[ERROR] Book with ISBN {isbn} not found")
                return None

        except Exception as e:
            print(f"[ERROR] Error retrieving book: {e}")
            return None
    
    def get_transaction_history(self, isbn: Optional[str] = None) -> List[Dict]:
        """
        Get transaction history for all books or a specific book.
        
        Args:
            isbn: Optional ISBN to filter transactions
            
        Returns:
            List of transactions
        """
        try:
            if isbn:
                transactions = self.transactions_collection.where('isbn', '==', isbn).stream()
            else:
                transactions = self.transactions_collection.stream()
            
            history = []
            for trans_doc in transactions:
                trans_data = trans_doc.to_dict()
                trans_data['transaction_id'] = trans_doc.id
                history.append(trans_data)

            print(f"[OK] Retrieved {len(history)} transaction(s)")
            return history

        except Exception as e:
            print(f"[ERROR] Error retrieving transactions: {e}")
            return []


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Initialize library manager
    library = LibraryManager()
    
    # Create sample books
    book1 = Book(
        title="Python Programming",
        author="John Doe",
        isbn="978-1234567890",
        late_return_fee=2.0,
        available_quantity=5
    )
    
    book2 = Book(
        title="Data Structures and Algorithms",
        author="Jane Smith",
        isbn="978-0987654321",
        late_return_fee=1.5,
        available_quantity=3
    )
    
    # Add books to database
    library.add_book(book1)
    library.add_book(book2)
    
    # Search for books
    results = library.search_book("Python", search_by='title')
    
    # Get inventory
    inventory = library.get_inventory()
    print(f"\nTotal books in inventory: {len(inventory)}")

# 📚 Kothalawala E-Library Management System

A comprehensive library management system built with Python, Streamlit, and Firebase Firestore for Kothalawala Defence University.

## 🚀 Features

### Core Requirements Implemented
- **REQ 1**: Add Books - Complete book entry system with title, author, ISBN, late fees, and quantity
- **REQ 2 & 3**: Search & Borrow - Advanced search by title/author with automatic quantity management
- **REQ 4**: Returns & Late Fee Calculator - Automated fee calculation based on days overdue
- **REQ 5**: Inventory Dashboard - Complete inventory reporting with filters and export

### UI/UX Features
- **Professional Design**: Clean top navigation with responsive layout
- **Real-time Data**: Live Firebase integration with instant updates
- **Interactive Dashboard**: Statistics, quick actions, and recent activity
- **Advanced Search**: Filter by availability, export data, detailed book information
- **Fee Calculator**: Live preview of late fees with step-by-step process

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Backend**: Python with Firebase Admin SDK
- **Database**: Google Firestore (NoSQL)
- **Authentication**: Firebase service account
- **Deployment**: Ready for Streamlit Cloud/local hosting

## 📋 Installation & Setup

### Prerequisites
- Python 3.7+
- Firebase project with Firestore enabled
- Firebase service account key

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ravindudilshaan01/E-Library-KDU.git
   cd E-Library-KDU
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit firebase-admin pandas
   ```

3. **Firebase Setup**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
   - Enable Firestore Database
   - Generate service account key (JSON file)
   - Save as `serviceAccountKey.json` in project root

4. **Add Sample Data**
   ```bash
   python add_sample_books.py
   ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📊 Sample Data

The system comes with 10 popular books pre-configured:
- To Kill a Mockingbird by Harper Lee
- 1984 by George Orwell
- Pride and Prejudice by Jane Austen
- The Great Gatsby by F. Scott Fitzgerald
- Harry Potter and the Philosopher's Stone by J.K. Rowling
- And 5 more classic titles...

## 🏗️ Project Structure

```
E-Library-KDU/
├── app.py                    # Main Streamlit application
├── library_backend.py        # Firebase backend operations
├── add_sample_books.py      # Script to populate sample data
├── test_firebase.py         # Firebase connection testing
├── PROJECT_DOCUMENTATION.md # Detailed technical documentation
├── firestore.rules         # Firestore security rules
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── .gitignore              # Git ignore file
```

## 🔒 Security Features

- Firebase service account authentication
- Firestore security rules
- Input validation and sanitization
- Secure credential management (credentials excluded from repo)

## 📱 User Interface

### Dashboard
- Real-time statistics (books, available copies, loans, fees)
- Quick action buttons for common tasks
- Recent inventory overview

### Inventory Management
- Complete book catalog with search and filtering
- Export functionality for reports
- Availability status indicators

### Book Operations
- **Add Books**: Guided form with validation
- **Search & Borrow**: Advanced search with live results
- **Returns**: Interactive fee calculator with preview

## 🚀 Deployment

### Streamlit Cloud
1. Create Streamlit Cloud account
2. Connect your GitHub repository
3. Add Firebase credentials via Streamlit secrets
4. Deploy with one click

### Local Deployment
- Run `streamlit run app.py`
- Access via `http://localhost:8501`

## 🧠 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed for educational purposes at Kothalawala Defence University.

## 👥 Authors

- **Ravindudilshaan** - *Initial work* - [ravindudilshaan01](https://github.com/ravindudilshaan01)

## ✍️ Acknowledgments

- Kothalawala Defence University
- Firebase team for excellent documentation
- Streamlit community for UI components
- Open source libraries used in this project

---

**Note**: Make sure to keep your `serviceAccountKey.json` file secure and never commit it to version control.

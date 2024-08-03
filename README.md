# Library 1.0
![library](https://github.com/fsemke/library_website/assets/94831163/aeddf840-cad3-49c9-a15c-a359b1fca7ae)

## Description:
This website is a conceptual solution for organizing our small club library. Every member of the club has free access to it, and the system operates on a trust basis. Currently, the library is managed using a traditional index card system. The goal of this website is to modernize and simplify the process of borrowing and returning books.

# Functionality

## Register / Login
To begin using the system, users need to register and log in. If you are the first user in the database, you will automatically be granted admin status. Our system uses token-based authentication to verify user identities and ensure secure access.

## Library
The library section allows users to browse through all the books available. The books are categorized into two sections: "Available books" and "Borrowed Books". Each book entry is clickable, providing more details when selected.

### Admin Capabilities
If you are an admin, you have additional capabilities. You can create a new book entry by providing all necessary details, including the title, author, published date, and a link to an image of the book cover.

### Book Description
When you click on a book, you are taken to a detailed description page. This page provides comprehensive information about the book, including its availability status. Users can borrow the book directly from this page. Admins have additional access to a borrowing history, showing which users have borrowed the book in the past.

## Users
This section lists all registered users within the system. Users can view the basic information of other members.

### Admin Capabilities
As an admin, you can manage user accounts more thoroughly. You have the ability to delete users from the system.

### Specific User Profile
On your own profile page, you can see a list of books you currently have borrowed. You also have the option to set a new password for your account. If you are an admin, you can view the borrowed books of any user, reset passwords for any account, and upgrade or downgrade user privileges to admin status.

## Statistics
Admins have access to a dedicated statistics section. Here, you can view a list of books that have been borrowed for the longest periods. This feature helps ensure that no book remains borrowed for an excessively long time without being returned.

# Files

## app.py
All the backend logic and functionality of the website are contained within this file. It handles user authentication, database interactions, and the overall operation of the website.

## layout.html
This is the base HTML file upon which all other HTML files are built. It includes the navigation bar and head configurations, ensuring a consistent look and feel across the entire website.

## Login / Registration
The login and registration pages are designed based on a template, providing a visually appealing interface for users to access the system.

## Home
There are two different HTML files for the homepage, one for logged-in users and one for visitors. The appropriate file is served based on the user's login status.

## Library
The library page uses CSS flexbox for layout management. This ensures that the display adapts seamlessly to varying numbers of books.

### add_book
This page allows admins to add new books to the library. Initially, the system checks if the user has admin privileges. If not, the user is redirected back to a previous page. Although there is no current feature to upload book covers directly, it remains a potential enhancement for future updates.

### book_detail
The book detail page includes several interactive options:
1. If the book is available, a "Borrow the book" button is displayed.
2. If you have borrowed the book, a "Return the book" button is shown.
3. If another user has borrowed the book, a message stating "Book is not available" is displayed.

Only admins have access to the borrowing history of the book to respect user privacy. The history is limited to the last 20 entries to keep the information concise and clear. Entries are ordered by date or, alternatively, by ID, to display them chronologically.

## Statistics
The statistics page also displays information ordered by date. The queries used to generate these statistics were complex, involving joins between multiple tables to gather all necessary data.

## Users
In the users section, a JavaScript popup is implemented to prevent accidental deletion of user accounts. This additional step ensures that user management actions are deliberate and reduces the risk of mistakes.

## User
This page displays all the books currently borrowed by a specific user.

# How It's Made
This project is entirely coded using Flask, along with some JavaScript. The backend relies on an SQLite3 database, structured with three interconnected tables to manage users, books, and borrowing history. SQLAlchemy is used to connect Flask with the database, providing an ORM (Object Relational Mapping) layer for efficient data management.

# .env
The .env file needs two variables:
- DATABASE_URI for example: 'sqlite:///db.db'
- SECRET_KEY

# To start the website in dev mode
``python3 app.py``

# Deploy
## Build
``docker build -t fsemke/library:v1.0.0 .``

## Run docker
``docker run --name library -p 5000:5000 -v ./instance:/app/src/instance -v ./uploads:/app/src/static/uploads -d fsemke/library:v1.0.0``

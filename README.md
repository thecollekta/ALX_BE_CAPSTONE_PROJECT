# Library Management System API

## Project Overview

The Library Management System API is a robust backend solution built using Django and Django REST Framework (DRF). This API facilitates the management of library resources, allowing users to interact with the system by borrowing, returning, and viewing books.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Installation

To set up the Library Management System API locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/library_management_system.git
   cd library_management_system
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:

   - On Windows:

     ```bash
     .venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

4. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Apply migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

## Configuration

1. **Environment Variables**: Set up the required environment variables, such as `SECRET_KEY`, `DEBUG`, and database settings.
2. **Settings**: Update the `settings.py` file to configure installed apps, middleware, and authentication backends as necessary.

## Usage

1. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

2. **Access the API**: Open a web browser or an API client (like Postman) and navigate to:

   ```web
   http://127.0.0.1:8000/api/
   ```

3. **URL Roots**

**register**: `http://127.0.0.1:8000/api/register/` # User registration

**login**: `http://127.0.0.1:8000/api/login/` # User login

**logout**: `http://127.0.0.1:8000/api/logout/` # User logout - Use refresh token

**users**: `http://127.0.0.1:8000/api/users/` # View all users - Authentication required

**books**: `http://127.0.0.1:8000/api/books/` # View all books - Authentication required

**transactions**: `http://127.0.0.1:8000/api/transactions/` # View all transactions

**Token**`http://127.0.0.1:8000/api/token/refresh/` # Generate JWT token

**Swagger**`http://127.0.0.1:8000/api/swagger/` # View API Documentation

**Redoc**`http://127.0.0.1:8000/api/redoc/` # View API Documentation

**Doc**`http://127.0.0.1:8000/api/docs/` # View API Documentation - Authentication required

## API Endpoints- Postman Testing Guide

Below a step-by-step guide on how to test the **Library Management System API** endpoints using **Postman**. Below are details for testing book-related actions using sample data for the book **"Book of Rhymes"** by **Festus Aboagye**.

```sql
| Method | Endpoint                         | Description                                |
|--------|----------------------------------|--------------------------------------------|
| POST   | /api/register/                   | Allows a new user to create an account.    |
| POST   | /api/login/                      | Allows a user to login into their account. |
| POST   | /api/logout/                     | Allows a user to logout of their account.  |
|--------|----------------------------------|--------------------------------------------|
| POST   | /api/books/                      | Create a new book (Admin Only).            |
| GET    | /api/books/                      | Retrieve a list of all books.              |
| GET    | /api/books/{id}/                 | Retrieve details of a specific book.       |
| PUT    | /api/books/{id}/                 | Update a specific book (Admin Only).       |
| DELETE | /api/books/{id}/                 | Delete a specific book (Admin Only).       |
| GET    | /api/books/available/            | Retrieve a list of available books.        |
|--------|----------------------------------|--------------------------------------------|
| POST   | /api/users/                      | Create a new user (Admin Only).            |
| GET    | /api/users/                      | Retrieve a list of all users (Admin Only). |
|--------|----------------------------------|--------------------------------------------|
| GET    | /api/transactions/               | Retrieve a list of all transactions.       |
| POST   | /api/transactions/{id}/checkout  | Check out a book.                          |
| POST   | /api/transactions/{id}/return    | Return a checked-out book.                 |
|--------|----------------------------------|--------------------------------------------|
```

## Base URL

- **Local Development URL**: `http://localhost:8000/`

---

## Authentication

### User Authentication (JWT)

1. **Create a new user**
   - **Method**: `POST`
   - **Endpoint**: `/api/register/`
   - **Body** (JSON):

```json
{
   "username": "admin",
   "email": "admin@example.com",
   "password": "admin123",
   "password2": "admin123"
}
```

- **Response** (JSON):

```json
     {
         "user": {
            "username": "admin",
            "email": "admin@example.com"
         },
         "tokens": {
            "refresh": "<your-refresh-token>",
            "access": "<your-access-token>"
         }
     }
```

> **Note**: Copy the `access` token for authorization in subsequent requests by adding it in the Postman **Authorization** tab, choosing **Bearer Token** type and pasting the token.

---

## API Endpoints

### 1. **Create a Book**

- **Method**: `POST`
- **Endpoint**: `/books/`
- **Authorization**: `Bearer <access_token>`
- **Body** (JSON):

  ```json
  {
   "title": "Book of Rhymes",
   "author": "Festus Aboagye",
   "isbn": "8732305902233",
   "published_date": "2024-01-24",
   "available_copies": 2
  }

- **Response** (JSON):

```json
  {
   "id": 1,
   "title": "Book of Rhymes",
   "author": "Festus Aboagye",
   "isbn": "8732305902233",
   "published_date": "2024-01-24",
   "available_copies": 2
  }
```

### 2. **View All Books**

**Note**: Admin Only

- **Method**: `GET`
- **Endpoint**: `/books/`
- **Authorization**: `Bearer <access_token>`
- **Body** (JSON):
- **Query Params** (Optional): You can use one of the params below to search for a book.
   `title`: Search by book title
   `author`: Search by book author
   `isbn`: Search by book ISBN

- **Response** (JSON):

```json
  {
   "id": 1,
   "title": "Book of Rhymes",
   "author": "Festus Aboagye",
   "isbn": "8732305902233",
   "published_date": "2024-01-24",
   "available_copies": 2
  }
```

### 3. **Check Out a Book**

- **Method**: `POST`
- **Endpoint**: `/transactions/`
- **Authorization**: `Bearer <access_token>`
- **Body** (JSON):

  ```json
  {
      "user": "1",
      "book": "1"
  }

>Note: The user ID corresponds to the user performing the action (must be logged in), and the book ID corresponds to the book you want to check out.

- **Response** (JSON):

```json
{
   "id": 1,
   "user": 1,
   "book": 1,
   "check_out_date": "2024-10-06T10:25:00Z",
   "due_date": "2024-10-20T10:25:00Z",
   "is_returned": false
}
```

### 4. **Return Out a Book**

- **Method**: `PUT`
- **Endpoint**: `/transactions/1/`
- **Authorization**: `Bearer <access_token>`
- **Body** (JSON):

  ```json
  {
      "user": "1",
      "book": "1"
  }

>Note: The user ID corresponds to the user performing the action (must be logged in), and the book ID corresponds to the book you want to check out.

- **Response** (JSON):

```json
{
   "id": 1,
   "user": 1,
   "book": 1,
   "check_out_date": "2024-10-06T10:25:00Z",
   "due_date": "2024-10-20T10:25:00Z",
   "is_returned": false
}
```

### 6. Overdue Notifications

**Method**: Automatically triggered by the system when a book's due date has passed without being returned. A Celery task will send an email notification to the user.

### 7. Notify Users of Available Books

**Method**: Automatically triggered when a user returns a book, making it available. A Celery task will send an email notification to the user who requested the book.

## Additional Features

### 8. Advanced Filtering

You can use query parameters to filter books by availability, author, title, or ISBN.

Example URL for filtering by author:
GET /books/?author=Festus Aboagye

Example URL for filtering by title:
GET /books/?title=Book of Rhymes

### 9. Pagination

By default, the API provides paginated results for book listings. You can customize pagination by passing query parameters:

?page=1 for the first page
?page_size=10 to limit results per page

### Additional Notes

- Ensure Celery and a broker like Redis are running to test asynchronous email notifications.
- You can adjust the `Bearer <access_token>` placeholder in Postman’s Authorization tab for proper authentication.

## Deployment

To deploy the API on platforms like Heroku or PythonAnywhere, follow these general steps:

1. **Create an account** on your chosen platform.
2. **Create a new app** in your dashboard.
3. **Set environment variables** in the app settings.
4. **Deploy your code** using Git or any other method provided by the platform.
5. **Test your deployed API** by accessing the public URL provided by the platform.

## Contributing

Contributions are welcome! If you would like to contribute to the Library Management System API, please fork the repository, create a feature branch, and submit a pull request.

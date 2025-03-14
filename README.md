# Backend API for Test Task

## Description
This is a backend application developed for a test task. The project was created by **Bogdan Kraievskiy** and includes user authentication and post management. JWT token authentication is used to secure the API.

## Technologies Used
- **FastAPI** - Web framework for building APIs
- **Pydantic** - Data validation and serialization
- **SQLAlchemy** - ORM for database interactions
- **Redis** - Caching layer for performance optimization
- **JWT Authentication** - Secure user authentication

## API Routes

### Authentication Routes
#### **POST** `/login`
- **Description:** User login endpoint.
- **Request Body:**
  ```json
  {
    "login": "string",
    "password": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Login was success",
    "data": "JWT_TOKEN"
  }
  ```

#### **POST** `/sign-up`
- **Description:** User registration endpoint.
- **Request Body:**
  ```json
  {
    "login": "string",
    "password": "string",
    "email": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Sign up was success",
    "data": "JWT_TOKEN"
  }
  ```

### Post Management Routes
#### **POST** `/add`
- **Description:** Create a new post (requires authentication).
- **Request Body:**
  ```json
  {
    "text": "string"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Post was created",
    "data": 1
  }
  ```

#### **GET** `/all`
- **Description:** Get all posts for the authenticated user.
- **Response:**
  ```json
  {
    "success": true,
    "message": "All posts was retreived",
    "data": [
      {
        "id": 1,
        "text": "example post"
      }
    ]
  }
  ```

#### **DELETE** `/`
- **Description:** Delete a post (requires authentication).
- **Request Body:**
  ```json
  {
    "post_id": 1
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Post was deleted",
    "data": true
  }
  ```

## Authentication
This API uses **JWT token authentication**. To access protected routes, include the token in the `Authorization` header:
```http
Authorization: Bearer YOUR_JWT_TOKEN
```

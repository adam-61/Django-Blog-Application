# Django Blog Application

A simple Blog Application built using Django, Python, HTML, and CSS.

This project was created as a Django assignment to practice models, forms, templates, CRUD operations, user authentication, and connecting users with their own blog posts.

## Project Overview

The Django Blog Application allows users to register an account, log in, create blog posts, view posts, edit their own posts, and delete their own posts.

Each blog post is connected to the user who created it.

## Features

- User Registration
- User Login
- User Logout
- Authentication-protected pages
- Display logged-in user's name
- Create blog posts
- View all blog posts
- View individual post details
- Edit own blog posts
- Delete own blog posts
- My Posts page
- Post ownership protection
- Optional image upload for blog posts
- Success and error messages
- Django Admin Panel
- SQLite database
- Template inheritance
- Custom CSS styling

## Technologies Used

- Python
- Django
- HTML
- CSS
- SQLite
- Pillow

## Django Concepts Practiced

- Django Project and App
- Models
- Views
- URLs
- Templates
- Template Inheritance
- Django Forms
- Django ORM
- User Authentication
- User Registration
- Login and Logout
- CRUD Operations
- Django Messages
- Static Files
- Media Files
- Django Admin

## BlogPost Model

Each blog post contains:

- Title
- Content
- Author
- Optional Image
- Created Date
- Updated Date

The author is connected to Django's built-in User model.

## CRUD Operations

### Create

Authenticated users can create their own blog posts.

### Read

Users can view all blog posts, individual post details, and their own posts.

### Update

Users can edit only the posts they created.

### Delete

Users can delete only their own posts.

## Authentication

The application uses Django's built-in authentication system.

Users can:

1. Register an account
2. Log in
3. Create blog posts
4. View their own posts
5. Edit their own posts
6. Delete their own posts
7. Log out

Only authenticated users can access protected pages such as Create Post and My Posts.

## Post Ownership

Every blog post is connected to the user who created it.

Users are only allowed to edit or delete their own posts.

This prevents one user from modifying or deleting another user's posts.

## Image Upload

Blog posts can optionally contain an image.

Users can upload an image when creating a post and can change the image when editing a post.

Uploaded images are stored in the media directory.

## Django Admin

The Django Admin Panel can be used to manage blog posts.

Administrators can add, edit, and delete blog posts through the admin interface.

# Screenshots

## Home Page

<img src="screenshots/home.png" alt="Home Page" width="800">

## Registration Page

<img src="screenshots/register.png" alt="Registration Page" width="800">

## Login Page

<img src="screenshots/login.png" alt="Login Page" width="800">

## Create Post Page

<img src="screenshots/create-post.png" alt="Create Post Page" width="800">

## Post Details Page

<img src="screenshots/post-detail.png" alt="Post Details Page" width="800">

## My Posts Page

<img src="screenshots/my-posts.png" alt="My Posts Page" width="800">

## Edit Post Page

<img src="screenshots/edit-post.png" alt="Edit Post Page" width="800">

## Delete Confirmation Page

<img src="screenshots/delete-post.png" alt="Delete Confirmation Page" width="800">

# How to Run the Project

Follow these steps to run the Django Blog Application on your computer.

## Clone the Repository

Clone the project from GitHub:

```bash
git clone URL

## Follow the instructions below.

- cd Django-Blog-Application
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py createsuperuser
- python manage.py runserver
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/admin/
**In RagamLib25, you have access to the following functionalities:**

**1. View books**
   Method: GET, Route: /view-books
   Description: View all the books present in the library at the moment.
**2. View users**
   Method: GET, Route: /view-users
   Description: View all the users who have registered for library access. This is a protected endpoint and can only be accessed if you have logged in.
**3. View a specific book**
   Method: GET, Route: /view-book?id=x
   Description: View all details of a book by its id. You can get its id from the /view-books endpoint.
**4. Add a book**
   Method: POST, Route: /add-book
   Description: Add a book and all of its relevant details to the library store of information.
   Body: title, author, published_year, genre, available_copies
**5. Add a user aka Registration**
   Method: POST, Route: /add-user
   Description: Add a user to the list of registered users with the library. If a user requests premium subscription, they must pay a premium amount of 500 to succesfully register themselves.
   Body: name, email, payment, membership_type (regular or premium), password, registered_date, ( user_type is inferred as 'user' i.e. not an admin (only 1 admin is present in the library's "db".I have not set up any backend verification to let other users become the admin upon request.) )
**6. Update a book**
    Method: PATCH, Route: /update-book
    Description: Update a currently existing book's details in the library. 
    Parameter: id
    Body: title, author, published_year, genre, available_copies
**7. Delete a book**
    Method: DELETE, Route: /delete-book
    Description: Delete a book with a valid id from the library. You must be logged in and be an admin to do this.
    Parameter: id
**8. Login**
    Method: POST, Route: /login
    Description: Login with your name and password to the library if you have already registered. JWT authentication is used in my application.
    Body: name, password
**9. Forgot password**
    Method: PATCH, Route: /forgot-password
    Description: If you have forgotten the password associated with your username, you can re-enter a new one.
    Parameter: id
    Body: password
**10. Logout**
    Method: POST, Route: /logout
    Self-ecplanatory
**11. Update user**
    Method: PATCH, Route: /update-user
    Description: You need to be logged in and authenticated to use this functionality. You can only change your account details.
    Parameter: id
    Body: name, email, payment, membership_type
**12. Promote to admin**
    Method: PATCH, Route: /promote-to-admin
    Description: This isn't fully fleshed out yet, but some verification on the backend can grant a user their request to become an admin.
    Parameter: id


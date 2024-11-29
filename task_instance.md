1. Task Title: Implement PUT /api/user API Endpoint

2. Task Description:

Develop an API endpoint for updating a user's profile information in a Flask backend application.

3. Functional Overview:
-Endpoint: PUT /api/user
-Description:
    - Allows authenticated users to update their profile details.
    - Supports updating fields such as password and other user attributes.
    - Ensures sensitive fields like password are handled securely.
-Authentication:
    - Requires the user to be logged in (JWT-based authentication).
-Input:
    - Accepts user details in the request body following a predefined schema.
-Outcome:
    - Updates the current user's profile in the database and returns the updated user data in JSON format.




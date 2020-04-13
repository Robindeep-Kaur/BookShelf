# BookShelf
A REST Api for management of favorite books of user.

### Instructions to test application
- Use postman to for testing.
- insert raw data, i.e. json format for POST methods.
- "/register" is a POST method, include fields-> email, fullname and password.
- "/login" is a GET method, include email and password in 'Authorization' of postman app.
- From login a 'token' will be generated/displayed which can be used to perform CRUD operations for books.
- In the 'Headers' of postman include a field 'access-token' and paste the recieved token in its value fiels.
- "/library" is a GET method, it will display list of inserted books with auto-generated 'Id'.
-"/library/<book-id>" with GET method to display one specific book with that'Id'. 
- "/library/<book-id>" with POST method. For this, include data in json format. Include fields-> title, author, genre, amazon_url.
- "/library/<book-id>" with PUT method. Include all the fields same as POST method.
  (Note: You might have to include all the fields and values, but it will update the fields for same 'Id' unlike POST method with generates    new 'Id'.)
- "/library/<book-id>" with DELETE method will delete the book with that 'Id'.

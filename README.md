# Cafe-Wifi-Webservice


The project was written in the Python language with the usage of Flask framework and Bootstrap. The database was created in SQLite with help of SQLAlchemy. The database is stored In PostgresSQL. To protect sensitive data, passwords before storing are hashed (sha256).
The project includes an admin account from which you can delete any coffee shop card. Each account has the ability to add a card, add a rating and remove cards added by a given user. A message is displayed after each of the above operations. Tooltips are assigned to the icons on the card. All the routes for those functions are available only for registered and logged-in users.
The project is deployed on render.com, here is the URL: https://wifi-and-cafe.onrender.com/home

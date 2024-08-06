# Databases

Databases can be added by Admins from the Advanced page.

Specify an identifiable Name of the database, such as "Business Data" or "Client Data" etc.

The Connection String will determine how to connect to the database. See the examples for each supported database below. Since the Connection String may have sensitive info in it, it is omitted when selecting databases, instead AutoDocument references each by the Name you supply.

So far the supported databases are: MySQL (and MariaDb), PostgreSQL, Microsoft SQL Server and SQLite.

See [this](https://www.connectionstrings.com/) great resource for Connection String Options depending on your individual database setup.

**MySQL (and MariaDB)**

An example connection string:

mysql+mysqlconnector://MyUser:MyPassword@DatabaseServer:3306/MyDatabase?ssl_disabled=true

**PostgreSQL**

**Microsoft SQL Server**

**SQLite**

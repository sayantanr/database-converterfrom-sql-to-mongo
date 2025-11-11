# 🔄 Relational Database to MongoDB Converter

A powerful Streamlit application that converts tables from relational databases (MySQL, PostgreSQL, SQLite, SQL Server) to MongoDB with an intuitive web interface.

## ✨ Features

- **Multi-Database Support**: Connect to MySQL, PostgreSQL, SQLite, and SQL Server
- **Interactive UI**: User-friendly web interface built with Streamlit
- **Table Selection**: Browse and select specific tables to migrate
- **Data Type Mapping**: Automatic conversion of SQL data types to MongoDB-compatible types
- **Batch Processing**: Efficient migration of large datasets with configurable batch sizes
- **Progress Tracking**: Real-time progress indicators during migration
- **Table Preview**: View table structure and sample data before migration
- **Migration Logging**: Detailed logs of all migration operations
- **Export Logs**: Download migration logs in JSON format

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Access to source relational database
- MongoDB instance (local or remote)

## 🚀 Installation

1. **Navigate to the Database-Converter directory:**
   ```bash
   cd Database-Converter
   ```

2. **Install pip (if not already installed):**
   ```bash
   python3 -m ensurepip --upgrade
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note for SQL Server users:** You may need to install ODBC Driver 17 for SQL Server:
   - **Linux (Amazon Linux/RHEL/CentOS):**
     ```bash
     sudo dnf install -y unixODBC-devel
     # Follow Microsoft's guide for ODBC Driver installation
     ```
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install unixodbc-dev
     ```
   - **macOS:**
     ```bash
     brew install unixodbc
     ```

## 🎯 Usage

### 1. Start the Application

```bash
streamlit run streamlit_db_converter.py
```

The application will open in your default web browser at `http://localhost:8501`

### 2. Configure Source Database

In the sidebar, select your source database type and enter connection details:

**For MySQL/PostgreSQL/SQL Server:**
- Host (e.g., `localhost`)
- Port (MySQL: 3306, PostgreSQL: 5432, SQL Server: 1433)
- Database Name
- Username
- Password

**For SQLite:**
- File Path (e.g., `database.db`)

Click **"Connect to Source DB"** to establish connection.

### 3. Configure MongoDB

Enter MongoDB connection details:
- Host (e.g., `localhost`)
- Port (default: 27017)
- Database Name
- Optional: Username, Password, and Auth Database

Click **"Connect to MongoDB"** to establish connection.

### 4. Select Tables

- Browse available tables from your source database
- Use checkboxes to select tables for migration
- Use "Select All" / "Deselect All" for bulk selection
- Preview table structure and sample data

### 5. Configure Migration

- Set batch size (default: 1000 rows per batch)
- Larger batch sizes = faster migration but more memory usage
- Smaller batch sizes = slower but more stable for large tables

### 6. Start Migration

- Click **"🚀 Start Migration"** to begin the process
- Monitor real-time progress for each table
- View migration summary upon completion
- Download migration logs for record-keeping

## 📊 Data Type Mapping

The application automatically maps SQL data types to MongoDB-compatible types:

| SQL Type | MongoDB Type |
|----------|--------------|
| INT, BIGINT, SERIAL | integer |
| FLOAT, DOUBLE, DECIMAL | float |
| BOOLEAN, BIT | boolean |
| DATE, DATETIME, TIMESTAMP | datetime |
| JSON, JSONB | json |
| BLOB, BINARY | binary |
| VARCHAR, TEXT, CHAR | string |

## 🔧 Configuration Options

### Batch Size
- **Small (100-500)**: For tables with large rows or limited memory
- **Medium (500-2000)**: Balanced performance (recommended)
- **Large (2000-10000)**: For fast migration of simple tables

### Authentication
- **Source DB**: Always required (except SQLite)
- **MongoDB**: Optional, enable if your MongoDB requires authentication

## 📝 Examples

### Example 1: MySQL to MongoDB

```
Source Database:
- Type: MySQL
- Host: localhost
- Port: 3306
- Database: myapp_db
- Username: root
- Password: ****

Target MongoDB:
- Host: localhost
- Port: 27017
- Database: myapp_mongo
- No authentication

Tables: users, products, orders
Batch Size: 1000
```

### Example 2: PostgreSQL to MongoDB (with Auth)

```
Source Database:
- Type: PostgreSQL
- Host: db.example.com
- Port: 5432
- Database: production
- Username: admin
- Password: ****

Target MongoDB:
- Host: mongo.example.com
- Port: 27017
- Database: production_mongo
- Username: mongo_admin
- Password: ****
- Auth DB: admin

Tables: customers, transactions
Batch Size: 2000
```

### Example 3: SQLite to MongoDB

```
Source Database:
- Type: SQLite
- File Path: /path/to/database.db

Target MongoDB:
- Host: localhost
- Port: 27017
- Database: sqlite_migration
- No authentication

Tables: all tables
Batch Size: 1000
```

## 🐛 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to source database
- Verify host, port, and credentials
- Check if database server is running
- Ensure firewall allows connections
- For remote databases, check network connectivity

**Problem**: Cannot connect to MongoDB
- Verify MongoDB is running: `systemctl status mongod`
- Check MongoDB port is accessible
- Verify authentication credentials if enabled

### Migration Issues

**Problem**: Migration fails for specific tables
- Check table permissions
- Verify table is not locked
- Review error message in migration log
- Try smaller batch size

**Problem**: Out of memory errors
- Reduce batch size
- Close other applications
- Migrate tables one at a time

### Data Type Issues

**Problem**: Data not converting correctly
- Check the data type mapping table
- Review sample data before migration
- Some complex types may need manual handling

## 🔒 Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive data
- Ensure secure connections (SSL/TLS) for production
- Limit database user permissions to required tables only
- Regularly backup data before migration

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Data Modeling](https://docs.mongodb.com/manual/core/data-modeling-introduction/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is part of the 100 Plus Python Coding Problems repository.

## 💡 Tips

1. **Test First**: Always test with a small subset of data first
2. **Backup**: Backup your databases before migration
3. **Monitor**: Watch memory usage during large migrations
4. **Verify**: Check data integrity after migration
5. **Indexes**: Remember to create indexes in MongoDB after migration
6. **Schema Design**: Consider MongoDB schema design best practices

## 🎓 Learning Resources

This tool demonstrates:
- Database connectivity with SQLAlchemy
- MongoDB operations with PyMongo
- Interactive web apps with Streamlit
- Data transformation with Pandas
- Error handling and logging
- Batch processing techniques

---

**Happy Migrating! 🚀**

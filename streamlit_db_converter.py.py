"""
Streamlit Application: Relational Database to MongoDB Converter
Supports MySQL, PostgreSQL, SQLite, and SQL Server
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect, MetaData, Table, select
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import traceback
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="DB to MongoDB Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'source_engine' not in st.session_state:
    st.session_state.source_engine = None
if 'mongo_client' not in st.session_state:
    st.session_state.mongo_client = None
if 'selected_tables' not in st.session_state:
    st.session_state.selected_tables = []
if 'migration_log' not in st.session_state:
    st.session_state.migration_log = []


def create_sql_connection(db_type, host, port, database, username, password, sqlite_path=None):
    """Create SQLAlchemy engine for different database types"""
    try:
        if db_type == "MySQL":
            connection_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "PostgreSQL":
            connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        elif db_type == "SQLite":
            connection_string = f"sqlite:///{sqlite_path}"
        elif db_type == "SQL Server":
            connection_string = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            return None, "Unsupported database type"
        
        engine = create_engine(connection_string)
        # Test connection
        with engine.connect() as conn:
            pass
        return engine, None
    except Exception as e:
        return None, str(e)


def create_mongo_connection(host, port, database, username=None, password=None, auth_db="admin"):
    """Create MongoDB connection"""
    try:
        if username and password:
            connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_db}"
        else:
            connection_string = f"mongodb://{host}:{port}/"
        
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client, None
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def get_table_list(engine):
    """Get list of tables from the database"""
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []


def get_table_info(engine, table_name):
    """Get column information for a table"""
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return columns
    except Exception as e:
        st.error(f"Error fetching table info: {str(e)}")
        return []


def convert_sql_to_mongo_type(sql_type):
    """Map SQL data types to MongoDB-friendly types"""
    sql_type_lower = str(sql_type).lower()
    
    if 'int' in sql_type_lower or 'serial' in sql_type_lower:
        return 'integer'
    elif 'float' in sql_type_lower or 'double' in sql_type_lower or 'decimal' in sql_type_lower or 'numeric' in sql_type_lower:
        return 'float'
    elif 'bool' in sql_type_lower or 'bit' in sql_type_lower:
        return 'boolean'
    elif 'date' in sql_type_lower or 'time' in sql_type_lower:
        return 'datetime'
    elif 'json' in sql_type_lower:
        return 'json'
    elif 'blob' in sql_type_lower or 'binary' in sql_type_lower:
        return 'binary'
    else:
        return 'string'


def migrate_table(engine, mongo_db, table_name, batch_size=1000):
    """Migrate a single table from SQL to MongoDB"""
    try:
        # Read data from SQL table
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        with engine.connect() as conn:
            # Get total count
            count_query = select(table)
            result = conn.execute(count_query)
            rows = result.fetchall()
            total_rows = len(rows)
            
            if total_rows == 0:
                return True, "Table is empty", 0
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=result.keys())
            
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Handle data type conversions
            for record in records:
                for key, value in record.items():
                    # Convert pandas/numpy types to Python native types
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        record[key] = value
                    elif hasattr(value, 'item'):  # numpy types
                        record[key] = value.item()
            
            # Insert into MongoDB in batches
            collection = mongo_db[table_name]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                collection.insert_many(batch)
                
                progress = min((i + batch_size) / total_rows, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"Migrated {min(i + batch_size, total_rows)}/{total_rows} rows")
            
            progress_bar.empty()
            status_text.empty()
            
            return True, f"Successfully migrated {total_rows} rows", total_rows
            
    except Exception as e:
        return False, f"Error: {str(e)}\n{traceback.format_exc()}", 0


def main():
    st.title("🔄 Relational Database to MongoDB Converter")
    st.markdown("Convert tables from MySQL, PostgreSQL, SQLite, or SQL Server to MongoDB")
    
    # Sidebar for connections
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Source Database Configuration
        st.subheader("1️⃣ Source Database")
        db_type = st.selectbox(
            "Database Type",
            ["MySQL", "PostgreSQL", "SQLite", "SQL Server"]
        )
        
        if db_type == "SQLite":
            sqlite_path = st.text_input("SQLite File Path", value="database.db")
            if st.button("Connect to SQLite"):
                engine, error = create_sql_connection(db_type, None, None, None, None, None, sqlite_path)
                if error:
                    st.error(f"Connection failed: {error}")
                else:
                    st.session_state.source_engine = engine
                    st.success("✅ Connected to SQLite!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                host = st.text_input("Host", value="localhost")
            with col2:
                port = st.number_input("Port", value=3306 if db_type == "MySQL" else 5432, step=1)
            
            database = st.text_input("Database Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Connect to Source DB"):
                if not all([host, database, username]):
                    st.error("Please fill in all required fields")
                else:
                    engine, error = create_sql_connection(db_type, host, port, database, username, password)
                    if error:
                        st.error(f"Connection failed: {error}")
                    else:
                        st.session_state.source_engine = engine
                        st.success("✅ Connected to source database!")
        
        st.divider()
        
        # MongoDB Configuration
        st.subheader("2️⃣ Target MongoDB")
        mongo_host = st.text_input("MongoDB Host", value="localhost", key="mongo_host")
        mongo_port = st.number_input("MongoDB Port", value=27017, step=1, key="mongo_port")
        mongo_database = st.text_input("MongoDB Database Name", key="mongo_db")
        
        use_auth = st.checkbox("Use Authentication")
        if use_auth:
            mongo_username = st.text_input("MongoDB Username", key="mongo_user")
            mongo_password = st.text_input("MongoDB Password", type="password", key="mongo_pass")
            mongo_auth_db = st.text_input("Auth Database", value="admin", key="mongo_auth")
        else:
            mongo_username = None
            mongo_password = None
            mongo_auth_db = "admin"
        
        if st.button("Connect to MongoDB"):
            if not mongo_database:
                st.error("Please enter MongoDB database name")
            else:
                client, error = create_mongo_connection(
                    mongo_host, mongo_port, mongo_database,
                    mongo_username, mongo_password, mongo_auth_db
                )
                if error:
                    st.error(f"Connection failed: {error}")
                else:
                    st.session_state.mongo_client = client
                    st.success("✅ Connected to MongoDB!")
    
    # Main content area
    if st.session_state.source_engine is None:
        st.info("👈 Please connect to a source database using the sidebar")
        return
    
    if st.session_state.mongo_client is None:
        st.info("👈 Please connect to MongoDB using the sidebar")
        return
    
    # Table selection and migration
    st.header("📊 Select Tables to Migrate")
    
    tables = get_table_list(st.session_state.source_engine)
    
    if not tables:
        st.warning("No tables found in the source database")
        return
    
    # Display tables with checkboxes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Available Tables ({len(tables)})")
        
        # Select all / Deselect all
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Select All"):
                st.session_state.selected_tables = tables.copy()
        with col_b:
            if st.button("Deselect All"):
                st.session_state.selected_tables = []
        
        # Table selection
        selected_tables = []
        for table in tables:
            if st.checkbox(table, value=table in st.session_state.selected_tables, key=f"table_{table}"):
                selected_tables.append(table)
        
        st.session_state.selected_tables = selected_tables
    
    with col2:
        st.subheader("Migration Settings")
        batch_size = st.number_input("Batch Size", min_value=100, max_value=10000, value=1000, step=100)
        
        if st.session_state.selected_tables:
            st.info(f"Selected: {len(st.session_state.selected_tables)} table(s)")
    
    # Table preview
    if st.session_state.selected_tables:
        st.divider()
        st.subheader("📋 Table Preview")
        
        preview_table = st.selectbox("Select table to preview", st.session_state.selected_tables)
        
        if preview_table:
            col_info = get_table_info(st.session_state.source_engine, preview_table)
            
            if col_info:
                st.write("**Column Information:**")
                col_df = pd.DataFrame([
                    {
                        "Column": col['name'],
                        "SQL Type": str(col['type']),
                        "MongoDB Type": convert_sql_to_mongo_type(col['type']),
                        "Nullable": col['nullable']
                    }
                    for col in col_info
                ])
                st.dataframe(col_df, use_container_width=True)
                
                # Show sample data
                try:
                    sample_query = f"SELECT * FROM {preview_table} LIMIT 5"
                    sample_df = pd.read_sql(sample_query, st.session_state.source_engine)
                    st.write("**Sample Data (first 5 rows):**")
                    st.dataframe(sample_df, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not fetch sample data: {str(e)}")
    
    # Migration button
    st.divider()
    
    if st.session_state.selected_tables:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Start Migration", type="primary", use_container_width=True):
                mongo_db = st.session_state.mongo_client[mongo_database]
                
                st.header("📈 Migration Progress")
                
                success_count = 0
                failed_count = 0
                total_rows = 0
                
                for table in st.session_state.selected_tables:
                    st.subheader(f"Migrating: {table}")
                    
                    success, message, rows = migrate_table(
                        st.session_state.source_engine,
                        mongo_db,
                        table,
                        batch_size
                    )
                    
                    if success:
                        st.success(f"✅ {table}: {message}")
                        success_count += 1
                        total_rows += rows
                    else:
                        st.error(f"❌ {table}: {message}")
                        failed_count += 1
                    
                    # Log migration
                    st.session_state.migration_log.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "table": table,
                        "status": "Success" if success else "Failed",
                        "rows": rows,
                        "message": message
                    })
                
                # Summary
                st.divider()
                st.header("📊 Migration Summary")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Successful", success_count)
                with col2:
                    st.metric("❌ Failed", failed_count)
                with col3:
                    st.metric("📝 Total Rows", total_rows)
                
                if success_count > 0:
                    st.balloons()
        
        with col2:
            if st.button("🗑️ Clear Selection", use_container_width=True):
                st.session_state.selected_tables = []
                st.rerun()
    
    # Migration log
    if st.session_state.migration_log:
        st.divider()
        st.header("📜 Migration Log")
        
        log_df = pd.DataFrame(st.session_state.migration_log)
        st.dataframe(log_df, use_container_width=True)
        
        # Download log
        log_json = json.dumps(st.session_state.migration_log, indent=2)
        st.download_button(
            label="📥 Download Log (JSON)",
            data=log_json,
            file_name=f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()

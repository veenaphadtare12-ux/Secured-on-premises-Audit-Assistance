import pandas as pd
from sqlalchemy import create_engine, text

def migrate_database():
    print("🚀 Initiating Database Migration from SQLite to PostgreSQL...\n" + "="*50)
    
    # 1. Define connection strings
    sqlite_uri = "sqlite:///corporate_ledger.db"
    postgres_uri = "postgresql+psycopg2://audit_admin:secure_password_123@localhost:5432/corporate_ledger"
    
    try:
        # 2. Create SQLAlchemy engines
        sqlite_engine = create_engine(sqlite_uri)
        pg_engine = create_engine(postgres_uri)
        
        # 3. Get all table names from the local SQLite file
        with sqlite_engine.connect() as conn:
            # Query the internal SQLite master table to find user-created tables
            query = text("SELECT name FROM sqlite_master WHERE type='table';")
            tables = pd.read_sql(query, conn)
            
        if tables.empty:
            print("❌ No tables found in SQLite database. Is corporate_ledger.db empty?")
            return

        # 4. Loop through each table and migrate the data
        for table_name in tables['name']:
            # Skip SQLite's internal metadata tables
            if table_name.startswith('sqlite_'):
                continue
                
            print(f"📦 Reading table '{table_name}' from SQLite...")
            df = pd.read_sql_table(table_name, sqlite_engine)
            
            print(f"   -> Found {len(df)} rows. Writing to PostgreSQL container...")
            # Write to Postgres. 'replace' ensures we can run this multiple times safely during testing
            df.to_sql(table_name, pg_engine, if_exists='replace', index=False)
            print(f"✅ Table '{table_name}' migrated successfully.\n")
            
        print("="*50)
        print("🎉 Migration Complete! Your Dockerized PostgreSQL instance is fully loaded.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Check if your Docker container is running with 'docker ps'")

if __name__ == "__main__":
    migrate_database()
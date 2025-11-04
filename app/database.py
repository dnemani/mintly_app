"""
DuckDB database utilities for the budgeting app
"""
import duckdb
import polars as pl
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)s|%(message)s',
    handlers=[
        logging.FileHandler(f'logs/database_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages DuckDB database operations"""
    
    def __init__(self, db_path: str = "data/mintly.db", read_only: bool = False):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        if read_only:
            self.conn = duckdb.connect(db_path, read_only=True)
            # Skip schema initialization in read-only mode
            logger.info(f"Database initialized in read-only mode at {db_path}")
        else:
            self.conn = duckdb.connect(db_path)
            self._initialize_schema()
            logger.info(f"Database initialized at {db_path}")
    
    def _initialize_schema(self):
        """Create database tables if they don't exist"""
        try:
            # Create transactions table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    date TIMESTAMP NOT NULL,
                    description VARCHAR NOT NULL,
                    amount DOUBLE NOT NULL,
                    category VARCHAR NOT NULL,
                    notes VARCHAR,
                    is_split BOOLEAN DEFAULT FALSE,
                    parent_transaction_id INTEGER,
                    source VARCHAR,
                    merchant VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_transaction_id) REFERENCES transactions(id)
                )
            """)
            
            # Create tags table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transaction_tags junction table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_tags (
                    transaction_id INTEGER,
                    tag_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (transaction_id, tag_id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id)
                )
            """)
            
            # Add columns to existing transactions table if they don't exist
            self._add_column_if_not_exists('transactions', 'source', 'VARCHAR')
            self._add_column_if_not_exists('transactions', 'merchant', 'VARCHAR')
            
            # Create sequence for auto-incrementing IDs
            self.conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS transactions_id_seq START 1
            """)
            
            self.conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS tags_id_seq START 1
            """)
            
            # Sync sequence with existing data
            self._sync_sequence()
            
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database schema: {str(e)}")
            raise
    
    def _add_column_if_not_exists(self, table: str, column: str, datatype: str):
        """Add a column to a table if it doesn't already exist"""
        try:
            # Check if column exists
            result = self.conn.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = '{column}'
            """).fetchall()
            
            if not result:
                self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}")
                logger.info(f"Added column {column} to {table}")
        except Exception as e:
            logger.warning(f"Could not add column {column} to {table}: {str(e)}")
    
    def _sync_sequence(self):
        """Synchronize sequence with max ID in table"""
        try:
            # Get max ID from transactions table
            result = self.conn.execute("SELECT MAX(id) FROM transactions").fetchone()
            max_id = result[0] if result and result[0] is not None else 0
            
            # Set sequence to max_id + 1
            if max_id > 0:
                # Drop and recreate sequence
                self.conn.execute("DROP SEQUENCE IF EXISTS transactions_id_seq")
                self.conn.execute(f"CREATE SEQUENCE transactions_id_seq START {max_id + 1}")
                logger.info(f"Synced sequence to start at {max_id + 1}")
        except Exception as e:
            logger.warning(f"Could not sync sequence: {str(e)}")
    
    def insert_transaction(self, date: datetime, description: str, amount: float, 
                          category: str, notes: Optional[str] = None,
                          is_split: bool = False, parent_transaction_id: Optional[int] = None) -> int:
        """Insert a single transaction and return its ID"""
        try:
            result = self.conn.execute("""
                INSERT INTO transactions (id, date, description, amount, category, notes, is_split, parent_transaction_id)
                VALUES (nextval('transactions_id_seq'), ?, ?, ?, ?, ?, ?, ?)
                RETURNING id
            """, [date, description, amount, category, notes, is_split, parent_transaction_id])
            
            transaction_id = result.fetchone()[0]
            logger.info(f"Inserted transaction ID {transaction_id}: {description} - ${amount}")
            return transaction_id
        except Exception as e:
            logger.error(f"Error inserting transaction: {str(e)}")
            raise
    
    def insert_transactions_batch(self, transactions: List[dict]) -> int:
        """Insert multiple transactions from a list of dicts"""
        try:
            # Convert to Polars DataFrame for efficient batch insert
            df = pl.DataFrame(transactions)
            
            # Get starting ID and generate IDs for the batch
            # We need to advance the sequence for each row we're inserting
            start_id = self.conn.execute("SELECT nextval('transactions_id_seq') as next_id").fetchone()[0]
            
            # Generate sequential IDs
            ids = list(range(start_id, start_id + len(df)))
            df = df.with_columns(pl.Series('id', ids))
            
            # Advance the sequence to account for all IDs we used
            # We already used one nextval, so advance by (len - 1) more
            if len(df) > 1:
                for _ in range(len(df) - 1):
                    self.conn.execute("SELECT nextval('transactions_id_seq')")
            
            # Add default columns if not present
            if 'notes' not in df.columns:
                df = df.with_columns(pl.lit(None).alias('notes'))
            if 'is_split' not in df.columns:
                df = df.with_columns(pl.lit(False).alias('is_split'))
            if 'parent_transaction_id' not in df.columns:
                df = df.with_columns(pl.lit(None).alias('parent_transaction_id'))
            if 'source' not in df.columns:
                df = df.with_columns(pl.lit(None).alias('source'))
            if 'merchant' not in df.columns:
                df = df.with_columns(pl.lit(None).alias('merchant'))
            
            # Register as a temporary table and insert
            self.conn.register('temp_transactions', df.to_arrow())
            self.conn.execute("""
                INSERT INTO transactions (id, date, description, amount, category, notes, is_split, parent_transaction_id, source, merchant)
                SELECT id, date, description, amount, category, notes, is_split, parent_transaction_id, source, merchant
                FROM temp_transactions
            """)
            self.conn.unregister('temp_transactions')
            
            count = len(transactions)
            logger.info(f"Batch inserted {count} transactions (IDs {start_id} to {start_id + count - 1})")
            return count
        except Exception as e:
            logger.error(f"Error batch inserting transactions: {str(e)}")
            raise
    
    def get_all_transactions(self) -> pl.DataFrame:
        """Get all transactions as a Polars DataFrame"""
        try:
            result = self.conn.execute("""
                SELECT id, date, description, amount, category, notes, is_split, parent_transaction_id, source, merchant
                FROM transactions
                ORDER BY date DESC
            """).arrow()
            
            df = pl.from_arrow(result)
            logger.info(f"Retrieved {len(df)} transactions")
            return df
        except Exception as e:
            logger.error(f"Error retrieving transactions: {str(e)}")
            raise
    
    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> pl.DataFrame:
        """Get transactions within a date range"""
        try:
            result = self.conn.execute("""
                SELECT id, date, description, amount, category, notes, is_split, parent_transaction_id, source, merchant, created_at
                FROM transactions
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            """, [start_date, end_date]).fetchall()
            
            # Handle empty results
            if not result:
                logger.info(f"No transactions found between {start_date} and {end_date}")
                return pl.DataFrame({
                    'id': [], 'date': [], 'description': [], 'amount': [], 
                    'category': [], 'notes': [], 'is_split': [], 
                    'parent_transaction_id': [], 'source': [], 'merchant': [], 'created_at': []
                })
            
            # Convert to list of dicts
            columns = ['id', 'date', 'description', 'amount', 'category', 'notes', 'is_split', 'parent_transaction_id', 'source', 'merchant', 'created_at']
            transactions = [dict(zip(columns, row)) for row in result]
            df = pl.DataFrame(transactions)
            
            logger.info(f"Retrieved {len(df)} transactions between {start_date} and {end_date}")
            return df
        except Exception as e:
            logger.error(f"Error retrieving transactions by date range: {str(e)}")
            raise
    
    def get_category_summary(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> pl.DataFrame:
        """Get spending summary by category"""
        try:
            query = """
                SELECT 
                    category,
                    SUM(amount) as total_amount,
                    COUNT(*) as transaction_count
                FROM transactions
                WHERE is_split = FALSE
            """
            
            params = []
            if start_date and end_date:
                query += " AND date BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            query += " GROUP BY category ORDER BY total_amount ASC"
            
            result = self.conn.execute(query, params).arrow()
            df = pl.from_arrow(result)
            
            # Calculate percentages
            if len(df) > 0:
                total_spending = abs(df.filter(pl.col('total_amount') < 0)['total_amount'].sum())
                if total_spending > 0:
                    df = df.with_columns(
                        (abs(pl.col('total_amount')) / total_spending * 100).alias('percentage')
                    )
                else:
                    df = df.with_columns(pl.lit(0.0).alias('percentage'))
            
            logger.info(f"Retrieved category summary with {len(df)} categories")
            return df
        except Exception as e:
            logger.error(f"Error retrieving category summary: {str(e)}")
            raise
    
    def split_transaction(self, transaction_id: int, splits: List[dict]) -> bool:
        """Split a transaction into multiple categories"""
        try:
            # Mark original transaction as split
            self.conn.execute("""
                UPDATE transactions
                SET is_split = TRUE
                WHERE id = ?
            """, [transaction_id])
            
            # Insert split transactions
            for split in splits:
                self.insert_transaction(
                    date=datetime.now(),  # Will be updated to match parent
                    description=split.get('notes', 'Split transaction'),
                    amount=split['amount'],
                    category=split['category'],
                    notes=split.get('notes'),
                    is_split=True,
                    parent_transaction_id=transaction_id
                )
            
            # Update split transactions to have same date as parent
            self.conn.execute("""
                UPDATE transactions
                SET date = (SELECT date FROM transactions WHERE id = ?)
                WHERE parent_transaction_id = ?
            """, [transaction_id, transaction_id])
            
            logger.info(f"Split transaction {transaction_id} into {len(splits)} parts")
            return True
        except Exception as e:
            logger.error(f"Error splitting transaction: {str(e)}")
            raise
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction and its splits"""
        try:
            # Delete split transactions first
            self.conn.execute("""
                DELETE FROM transactions
                WHERE parent_transaction_id = ?
            """, [transaction_id])
            
            # Delete the main transaction
            self.conn.execute("""
                DELETE FROM transactions
                WHERE id = ?
            """, [transaction_id])
            
            logger.info(f"Deleted transaction {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            raise
    
    def update_transaction_category(self, transaction_id: int, category: str) -> bool:
        """Update the category of a transaction"""
        try:
            self.conn.execute("""
                UPDATE transactions
                SET category = ?
                WHERE id = ?
            """, [category, transaction_id])
            
            logger.info(f"Updated transaction {transaction_id} category to {category}")
            return True
        except Exception as e:
            logger.error(f"Error updating transaction category: {str(e)}")
            raise
    
    def get_or_create_tag(self, tag_name: str) -> int:
        """Get tag ID by name, or create if it doesn't exist"""
        try:
            # Check if tag exists
            result = self.conn.execute("""
                SELECT id FROM tags WHERE name = ?
            """, [tag_name]).fetchone()
            
            if result:
                return result[0]
            
            # Create new tag
            tag_id = self.conn.execute("SELECT nextval('tags_id_seq') as next_id").fetchone()[0]
            self.conn.execute("""
                INSERT INTO tags (id, name) VALUES (?, ?)
            """, [tag_id, tag_name])
            
            logger.info(f"Created new tag: {tag_name} (ID: {tag_id})")
            return tag_id
        except Exception as e:
            logger.error(f"Error getting/creating tag: {str(e)}")
            raise
    
    def add_tag_to_transaction(self, transaction_id: int, tag_name: str) -> bool:
        """Add a tag to a transaction"""
        try:
            tag_id = self.get_or_create_tag(tag_name)
            
            # Add tag to transaction (ignore if already exists)
            self.conn.execute("""
                INSERT OR IGNORE INTO transaction_tags (transaction_id, tag_id)
                VALUES (?, ?)
            """, [transaction_id, tag_id])
            
            logger.info(f"Added tag '{tag_name}' to transaction {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding tag to transaction: {str(e)}")
            raise
    
    def remove_tag_from_transaction(self, transaction_id: int, tag_name: str) -> bool:
        """Remove a tag from a transaction"""
        try:
            # Get tag ID
            result = self.conn.execute("""
                SELECT id FROM tags WHERE name = ?
            """, [tag_name]).fetchone()
            
            if not result:
                logger.warning(f"Tag '{tag_name}' does not exist")
                return False
            
            tag_id = result[0]
            
            # Remove tag from transaction
            self.conn.execute("""
                DELETE FROM transaction_tags
                WHERE transaction_id = ? AND tag_id = ?
            """, [transaction_id, tag_id])
            
            logger.info(f"Removed tag '{tag_name}' from transaction {transaction_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing tag from transaction: {str(e)}")
            raise
    
    def get_transaction_tags(self, transaction_id: int) -> List[str]:
        """Get all tags for a transaction"""
        try:
            result = self.conn.execute("""
                SELECT t.name
                FROM tags t
                JOIN transaction_tags tt ON t.id = tt.tag_id
                WHERE tt.transaction_id = ?
                ORDER BY t.name
            """, [transaction_id]).fetchall()
            
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting transaction tags: {str(e)}")
            raise
    
    def get_all_tags(self) -> List[Dict]:
        """Get all tags with usage count"""
        try:
            result = self.conn.execute("""
                SELECT t.id, t.name, COUNT(tt.transaction_id) as usage_count
                FROM tags t
                LEFT JOIN transaction_tags tt ON t.id = tt.tag_id
                GROUP BY t.id, t.name
                ORDER BY usage_count DESC, t.name
            """).fetchall()
            
            return [
                {'id': row[0], 'name': row[1], 'usage_count': row[2]}
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting all tags: {str(e)}")
            raise
    
    def get_transactions_by_tag(self, tag_name: str) -> pl.DataFrame:
        """Get all transactions with a specific tag"""
        try:
            result = self.conn.execute("""
                SELECT t.id, t.date, t.description, t.amount, t.category, 
                       t.notes, t.source, t.merchant, t.is_split, t.parent_transaction_id
                FROM transactions t
                JOIN transaction_tags tt ON t.id = tt.transaction_id
                JOIN tags tg ON tt.tag_id = tg.id
                WHERE tg.name = ?
                ORDER BY t.date DESC
            """, [tag_name]).fetchall()
            
            if not result:
                return pl.DataFrame({
                    'id': [], 'date': [], 'description': [], 'amount': [], 'category': [],
                    'notes': [], 'source': [], 'merchant': [], 'is_split': [], 'parent_transaction_id': []
                })
            
            columns = ['id', 'date', 'description', 'amount', 'category', 'notes', 
                      'source', 'merchant', 'is_split', 'parent_transaction_id']
            transactions = [dict(zip(columns, row)) for row in result]
            df = pl.DataFrame(transactions)
            
            logger.info(f"Retrieved {len(df)} transactions with tag '{tag_name}'")
            return df
        except Exception as e:
            logger.error(f"Error getting transactions by tag: {str(e)}")
            raise
    
    def update_transaction_merchant(self, transaction_id: int, merchant: str):
        """Update the merchant for a transaction"""
        try:
            self.conn.execute("""
                UPDATE transactions 
                SET merchant = ? 
                WHERE id = ?
            """, [merchant, transaction_id])
            
            logger.info(f"Updated merchant for transaction {transaction_id} to '{merchant}'")
        except Exception as e:
            logger.error(f"Error updating merchant: {str(e)}")
            raise
    
    def update_transaction_source(self, transaction_id: int, source: str):
        """Update the source for a transaction"""
        try:
            self.conn.execute("""
                UPDATE transactions 
                SET source = ? 
                WHERE id = ?
            """, [source, transaction_id])
            
            logger.info(f"Updated source for transaction {transaction_id} to '{source}'")
        except Exception as e:
            logger.error(f"Error updating source: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database connection closed")


# Global database instance - initialized per application
# db_manager = DatabaseManager()  # Commented out to avoid conflicts


"""
API endpoints for transaction management
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import polars as pl
import logging

from app.models import Transaction, TransactionSplit, CategoryEnum
from app.db_instance import db_manager
from app.categorizer import categorizer
from app.csv_parsers import CSVParserFactory

router = APIRouter(prefix="/api/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_transactions(file: UploadFile = File(...)):
    """
    Upload and process a CSV file of transactions
    
    Supports multiple formats:
    - Costco Visa: Status, Date, Description, Debit, Credit, Member Name
    - Citibank: Status, Date, Description, Debit, Credit
    - Chase: Transaction Date, Post Date, Description, Amount, Type
    - Generic: Date, Description, Amount
    """
    if not ( file.filename.endswith('.csv') or file.filename.endswith('.CSV') ):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV file
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # Use parser factory to detect and parse the CSV format
        parser_factory = CSVParserFactory()
        transactions = parser_factory.parse(csv_content)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No valid transactions found in CSV")
        
        # Categorize transactions
        categorized_transactions = categorizer.categorize_batch(transactions)
        
        # Insert into database
        count = db_manager.insert_transactions_batch(categorized_transactions)
        
        logger.info(f"Successfully uploaded {count} transactions from {file.filename}")
        
        return {
            "status": "success",
            "message": f"Successfully uploaded {count} transactions",
            "count": count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/list")
async def list_transactions(limit: int = 100):
    """Get list of recent transactions with tags, source, and merchant info"""
    try:
        df = db_manager.get_all_transactions()
        
        if len(df) > limit:
            df = df.head(limit)
        
        # Convert to list of dicts
        transactions = df.to_dicts()
        
        # Add tags, source, and merchant to each transaction
        for transaction in transactions:
            transaction_id = transaction.get('id')
            
            # Get tags for this transaction
            tags = db_manager.get_transaction_tags(transaction_id)
            transaction['tags'] = tags
            
            # Source and merchant should already be in the dataframe
            # but ensure they're present (might be None)
            if 'source' not in transaction:
                transaction['source'] = None
            if 'merchant' not in transaction:
                transaction['merchant'] = None
        
        return {
            "status": "success",
            "count": len(transactions),
            "transactions": transactions
        }
    
    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")


@router.put("/{transaction_id}/category")
async def update_category(transaction_id: int, category: CategoryEnum):
    """Update the category of a transaction"""
    try:
        db_manager.update_transaction_category(transaction_id, category.value)
        
        return {
            "status": "success",
            "message": f"Updated transaction {transaction_id} to category {category.value}"
        }
    
    except Exception as e:
        logger.error(f"Error updating transaction category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")


@router.post("/{transaction_id}/split")
async def split_transaction(transaction_id: int, split_data: TransactionSplit):
    """Split a transaction into multiple categories"""
    try:
        # Validate that transaction exists
        df = db_manager.get_all_transactions()
        transaction = df.filter(pl.col('id') == transaction_id)
        
        if len(transaction) == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Validate that split amounts sum to original amount
        original_amount = transaction['amount'][0]
        split_sum = sum(split['amount'] for split in split_data.splits)
        
        if abs(split_sum - original_amount) > 0.01:  # Allow small floating point differences
            raise HTTPException(
                status_code=400, 
                detail=f"Split amounts ({split_sum}) must sum to original amount ({original_amount})"
            )
        
        # Perform split
        db_manager.split_transaction(transaction_id, split_data.splits)
        
        return {
            "status": "success",
            "message": f"Successfully split transaction {transaction_id} into {len(split_data.splits)} parts"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error splitting transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error splitting transaction: {str(e)}")


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Delete a transaction"""
    try:
        db_manager.delete_transaction(transaction_id)
        
        return {
            "status": "success",
            "message": f"Deleted transaction {transaction_id}"
        }
    
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")


@router.get("/categories")
async def get_categories():
    """Get list of available categories"""
    return {
        "categories": [cat.value for cat in CategoryEnum]
    }


@router.get("/date-range")
async def get_transactions_by_date_range(start_date: str, end_date: str):
    """Get transactions within a date range"""
    try:
        df = db_manager.get_transactions_by_date_range(start_date, end_date)
        
        # Convert Polars DataFrame to list of dicts
        if len(df) == 0:
            return []
        
        transactions = df.to_dicts()
        return transactions
    
    except Exception as e:
        logger.error(f"Error getting transactions by date range: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")


@router.put("/{transaction_id}/merchant")
async def update_transaction_merchant(transaction_id: int, request: dict):
    """Update the merchant for a transaction"""
    try:
        merchant = request.get('merchant', '')
        db_manager.update_transaction_merchant(transaction_id, merchant)
        
        return {
            "status": "success",
            "message": f"Updated merchant for transaction {transaction_id}",
            "merchant": merchant
        }
    
    except Exception as e:
        logger.error(f"Error updating merchant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating merchant: {str(e)}")


@router.put("/{transaction_id}/source")
async def update_transaction_source(transaction_id: int, request: dict):
    """Update the source for a transaction"""
    try:
        source = request.get('source', '')
        db_manager.update_transaction_source(transaction_id, source)
        
        return {
            "status": "success",
            "message": f"Updated source for transaction {transaction_id}",
            "source": source
        }
    
    except Exception as e:
        logger.error(f"Error updating source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating source: {str(e)}")


"""
Pydantic data models for the budgeting app
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class CategoryEnum(str, Enum):
    """Pre-defined spending categories"""
    GROCERIES = "Groceries"
    RESTAURANTS = "Restaurants"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    HEALTHCARE = "Healthcare"
    TRAVEL = "Travel"
    INCOME = "Income"
    HOUSING = "Housing"
    INSURANCE = "Insurance"
    EDUCATION = "Education"
    PERSONAL_CARE = "Personal Care"
    SUBSCRIPTIONS = "Subscriptions"
    UNCATEGORIZED = "Uncategorized"


class Transaction(BaseModel):
    """Model for a financial transaction"""
    id: Optional[int] = None
    date: datetime
    description: str = Field(min_length=1)
    amount: float
    category: CategoryEnum = CategoryEnum.UNCATEGORIZED
    notes: Optional[str] = None
    is_split: bool = False
    parent_transaction_id: Optional[int] = None
    source: Optional[str] = None
    merchant: Optional[str] = None
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-15T00:00:00",
                "description": "Starbucks Coffee",
                "amount": -4.50,
                "category": "Restaurants"
            }
        }


class TransactionSplit(BaseModel):
    """Model for splitting a transaction into multiple categories"""
    transaction_id: int
    splits: List[dict] = Field(min_length=2)
    
    @field_validator('splits')
    @classmethod
    def validate_splits(cls, v):
        if len(v) < 2:
            raise ValueError('Must have at least 2 splits')
        
        # Check that all splits have required fields
        for split in v:
            if 'category' not in split or 'amount' not in split:
                raise ValueError('Each split must have category and amount')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": 1,
                "splits": [
                    {"category": "Groceries", "amount": 50.00, "notes": "Food items"},
                    {"category": "Personal Care", "amount": 15.00, "notes": "Toiletries"}
                ]
            }
        }


class TransactionUpload(BaseModel):
    """Model for uploading transactions from CSV"""
    date: str
    description: str
    amount: float
    
    @field_validator('date')
    @classmethod
    def parse_date(cls, v):
        # Try different date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                datetime.strptime(v, fmt)
                return v
            except ValueError:
                continue
        raise ValueError(f'Date {v} does not match any expected format')


class CategorySummary(BaseModel):
    """Model for category spending summary"""
    category: str
    total_amount: float
    transaction_count: int
    percentage: float


class SpendingReport(BaseModel):
    """Model for spending report"""
    start_date: datetime
    end_date: datetime
    total_spent: float
    total_income: float
    net_balance: float
    categories: List[CategorySummary]
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-01-01T00:00:00",
                "end_date": "2025-01-31T23:59:59",
                "total_spent": 2500.00,
                "total_income": 5000.00,
                "net_balance": 2500.00,
                "categories": [
                    {
                        "category": "Groceries",
                        "total_amount": 500.00,
                        "transaction_count": 15,
                        "percentage": 20.0
                    }
                ]
            }
        }


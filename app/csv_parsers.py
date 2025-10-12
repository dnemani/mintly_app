"""
CSV parsers for different credit card and bank statement formats
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)


class CSVParser(ABC):
    """Base class for CSV parsers"""
    
    @abstractmethod
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse CSV content and return list of transactions"""
        pass
    
    @abstractmethod
    def detect(self, csv_content: str) -> bool:
        """Detect if this parser can handle the given CSV format"""
        pass
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Try to parse date with multiple formats"""
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def clean_amount(self, amount_str: str) -> Optional[float]:
        """Clean and parse amount string"""
        if not amount_str or amount_str.strip() == '':
            return None
        try:
            amount_clean = amount_str.replace('$', '').replace(',', '').strip()
            if amount_clean.startswith('(') and amount_clean.endswith(')'):
                amount_clean = '-' + amount_clean[1:-1]
            return float(amount_clean)
        except (ValueError, AttributeError):
            return None


class CitibankParser(CSVParser):
    """Parser for Citibank credit card statements"""
    
    def detect(self, csv_content: str) -> bool:
        """Detect Citibank format by checking for Status, Debit, Credit columns"""
        try:
            csv_data = StringIO(csv_content)
            reader = csv.DictReader(csv_data)
            headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Citibank format has Status, Date, Description, Debit, Credit
            return all(col in headers for col in ['status', 'date', 'description', 'debit', 'credit'])
        except Exception:
            return False
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse Citibank CSV format"""
        csv_data = StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        transactions = []
        
        for row in reader:
            row_normalized = {k.lower().strip(): v.strip() if v else '' for k, v in row.items()}
            
            date_str = row_normalized.get('date', '')
            description = row_normalized.get('description', '')
            status = row_normalized.get('status', '')
            debit_str = row_normalized.get('debit', '')
            credit_str = row_normalized.get('credit', '')
            
            # Skip if no date or description
            if not date_str or not description:
                logger.warning(f"Citibank: Skipping row with missing date or description")
                continue
            
            # Parse date
            date_obj = self.parse_date(date_str)
            if not date_obj:
                logger.warning(f"Citibank: Could not parse date: {date_str}")
                continue
            
            # Parse amount
            # Citibank format: Debit = purchases (expenses), Credit = payments/returns
            amount = None
            
            if debit_str:
                debit_val = self.clean_amount(debit_str)
                if debit_val is not None:
                    # Debits are expenses, should be negative
                    amount = -abs(debit_val)
            
            if credit_str:
                credit_val = self.clean_amount(credit_str)
                if credit_val is not None:
                    # Credits are payments/returns
                    # If already negative, it's an expense (some Citibank formats do this)
                    # If positive, it's a return/payment
                    if credit_val < 0:
                        amount = credit_val  # Keep negative
                    else:
                        amount = credit_val  # Keep positive (refund/payment)
            
            if amount is None:
                logger.warning(f"Citibank: Could not parse amount for: {description}")
                continue
            
            transactions.append({
                'date': date_obj,
                'description': description,
                'amount': amount,
                'notes': f"Status: {status}" if status else None
            })
        
        logger.info(f"Citibank: Parsed {len(transactions)} transactions")
        return transactions


class GenericParser(CSVParser):
    """Generic parser for standard Date, Description, Amount format"""
    
    def detect(self, csv_content: str) -> bool:
        """Detect generic format"""
        try:
            csv_data = StringIO(csv_content)
            reader = csv.DictReader(csv_data)
            headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Generic format needs Date, Description, and Amount (or Debit/Credit)
            has_date = 'date' in headers
            has_description = 'description' in headers or 'merchant' in headers
            has_amount = 'amount' in headers or ('debit' in headers and 'credit' in headers)
            
            return has_date and has_description and has_amount
        except Exception:
            return False
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse generic CSV format"""
        csv_data = StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        transactions = []
        
        for row in reader:
            row_normalized = {k.lower().strip(): v.strip() if v else '' for k, v in row.items()}
            
            date_str = row_normalized.get('date', '')
            description = row_normalized.get('description', '') or row_normalized.get('merchant', '')
            
            # Handle different amount formats
            amount_str = row_normalized.get('amount', '')
            debit_str = row_normalized.get('debit', '')
            credit_str = row_normalized.get('credit', '')
            
            if not date_str or not description:
                continue
            
            date_obj = self.parse_date(date_str)
            if not date_obj:
                continue
            
            # Parse amount
            amount = None
            
            if amount_str:
                amount = self.clean_amount(amount_str)
            elif debit_str or credit_str:
                if debit_str:
                    debit_val = self.clean_amount(debit_str)
                    if debit_val is not None:
                        amount = -abs(debit_val)
                elif credit_str:
                    credit_val = self.clean_amount(credit_str)
                    if credit_val is not None:
                        amount = abs(credit_val)
            
            if amount is None:
                continue
            
            transactions.append({
                'date': date_obj,
                'description': description,
                'amount': amount
            })
        
        logger.info(f"Generic: Parsed {len(transactions)} transactions")
        return transactions


class CostcoVisaParser(CSVParser):
    """Parser for Costco Visa credit card statements"""
    
    def detect(self, csv_content: str) -> bool:
        """Detect Costco Visa format by checking for Member Name column"""
        try:
            csv_data = StringIO(csv_content)
            reader = csv.DictReader(csv_data)
            headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Costco Visa format has Status, Date, Description, Debit, Credit, Member Name
            required_cols = ['status', 'date', 'description', 'debit', 'credit', 'member name']
            return all(col in headers for col in required_cols)
        except Exception:
            return False
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse Costco Visa CSV format"""
        csv_data = StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        transactions = []
        
        for row in reader:
            row_normalized = {k.lower().strip(): v.strip() if v else '' for k, v in row.items()}
            
            date_str = row_normalized.get('date', '')
            description = row_normalized.get('description', '')
            status = row_normalized.get('status', '')
            debit_str = row_normalized.get('debit', '')
            credit_str = row_normalized.get('credit', '')
            member_name = row_normalized.get('member name', '')
            
            # Skip if no date or description
            if not date_str or not description:
                logger.warning(f"Costco Visa: Skipping row with missing date or description")
                continue
            
            # Parse date
            date_obj = self.parse_date(date_str)
            if not date_obj:
                logger.warning(f"Costco Visa: Could not parse date: {date_str}")
                continue
            
            # Parse amount
            # Costco Visa format: Debit = purchases (expenses), Credit = payments/returns
            amount = None
            
            if debit_str:
                debit_val = self.clean_amount(debit_str)
                if debit_val is not None:
                    # Debits are expenses, should be negative
                    amount = -abs(debit_val)
            
            if credit_str:
                credit_val = self.clean_amount(credit_str)
                if credit_val is not None:
                    # Credits are payments/returns (positive)
                    amount = abs(credit_val)
            
            if amount is None:
                logger.warning(f"Costco Visa: Could not parse amount for: {description}")
                continue
            
            # Build notes with status and member name
            notes_parts = []
            if status:
                notes_parts.append(f"Status: {status}")
            if member_name:
                notes_parts.append(f"Member: {member_name}")
            
            transactions.append({
                'date': date_obj,
                'description': description,
                'amount': amount,
                'notes': ' | '.join(notes_parts) if notes_parts else None
            })
        
        logger.info(f"Costco Visa: Parsed {len(transactions)} transactions")
        return transactions


class ChaseParser(CSVParser):
    """Parser for Chase credit card statements"""
    
    def detect(self, csv_content: str) -> bool:
        """Detect Chase format"""
        try:
            csv_data = StringIO(csv_content)
            reader = csv.DictReader(csv_data)
            headers = [h.lower().strip() for h in reader.fieldnames] if reader.fieldnames else []
            
            # Chase format: Transaction Date, Post Date, Description, Category, Type, Amount
            chase_indicators = ['transaction date', 'post date', 'type']
            return any(indicator in headers for indicator in chase_indicators)
        except Exception:
            return False
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse Chase CSV format"""
        csv_data = StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        transactions = []
        
        for row in reader:
            row_normalized = {k.lower().strip(): v.strip() if v else '' for k, v in row.items()}
            
            date_str = row_normalized.get('transaction date', '') or row_normalized.get('date', '')
            description = row_normalized.get('description', '')
            amount_str = row_normalized.get('amount', '')
            txn_type = row_normalized.get('type', '')
            
            if not date_str or not description:
                continue
            
            date_obj = self.parse_date(date_str)
            if not date_obj:
                continue
            
            amount = self.clean_amount(amount_str)
            if amount is None:
                continue
            
            # Chase shows purchases as negative, payments as positive
            transactions.append({
                'date': date_obj,
                'description': description,
                'amount': amount,
                'notes': f"Type: {txn_type}" if txn_type else None
            })
        
        logger.info(f"Chase: Parsed {len(transactions)} transactions")
        return transactions


class CSVParserFactory:
    """Factory to select appropriate parser for CSV content"""
    
    def __init__(self):
        self.parsers = [
            CostcoVisaParser(),  # Check Costco Visa first (has Member Name column)
            CitibankParser(),
            ChaseParser(),
            GenericParser(),  # Generic should be last as fallback
        ]
    
    def get_parser(self, csv_content: str) -> Optional[CSVParser]:
        """Detect and return appropriate parser for the CSV content"""
        for parser in self.parsers:
            if parser.detect(csv_content):
                logger.info(f"Detected format: {parser.__class__.__name__}")
                return parser
        
        logger.warning("No parser detected, using generic parser")
        return GenericParser()
    
    def parse(self, csv_content: str) -> List[Dict]:
        """Parse CSV content using appropriate parser"""
        parser = self.get_parser(csv_content)
        if parser:
            return parser.parse(csv_content)
        return []


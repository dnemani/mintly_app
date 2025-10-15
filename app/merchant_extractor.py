"""
Merchant extraction from transaction descriptions
Uses pattern matching and NLP to extract merchant names from transaction descriptions
"""
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MerchantExtractor:
    """Extract merchant names from transaction descriptions"""
    
    def __init__(self):
        # Common patterns in transaction descriptions
        self.patterns = [
            # Pattern: MERCHANT_NAME #STORE_NUMBER LOCATION STATE
            r'^([A-Z][A-Z\s&]+?)\s+#?\d{2,6}',
            # Pattern: MERCHANT_NAME LOCATION STATE
            r'^([A-Z][A-Z\s&]+?)\s+[A-Z]{2,}(?:\s+[A-Z]{2})?$',
            # Pattern: Website domain
            r'^([A-Z][A-Z]+)\.COM',
            # Pattern: Start with capital letters before numbers
            r'^([A-Z][A-Z\s&\-\']+?)\s+\d',
            # Pattern: Everything before phone number
            r'^(.+?)\s+\d{3}-?\d{3}-?\d{4}',
            # Pattern: Everything before city/state
            r'^(.+?)\s+[A-Z][A-Za-z]+\s+[A-Z]{2}$',
        ]
        
        # Common merchant name cleanups
        self.cleanup_patterns = [
            (r'\s+INC\.?$', ''),
            (r'\s+LLC\.?$', ''),
            (r'\s+LTD\.?$', ''),
            (r'\s+CORP\.?$', ''),
            (r'\s+CO\.?$', ''),
            (r'\s*\*+$', ''),  # Remove trailing asterisks
            (r'^\*+\s*', ''),  # Remove leading asterisks
            (r'\s+', ' '),     # Normalize spaces
        ]
        
        # Common merchant replacements (e.g., abbreviations to full names)
        self.merchant_mappings = {
            'AMZN': 'Amazon',
            'AMAZON MKTPLACE': 'Amazon',
            'AMAZON.COM': 'Amazon',
            'COSTCO WHSE': 'Costco',
            'COSTCO WHOLESALE': 'Costco',
            'TARGET.COM': 'Target',
            'WALMART.COM': 'Walmart',
            'TST* ': '',  # Remove TST* prefix (Square)
            'SQ *': '',   # Remove SQ* prefix (Square)
            'PAYPAL *': 'PayPal - ',
        }
    
    def extract(self, description: str) -> Optional[str]:
        """
        Extract merchant name from transaction description
        
        Args:
            description: Transaction description string
            
        Returns:
            Extracted merchant name or None if extraction fails
        """
        if not description:
            return None
        
        # Clean up description
        description = description.strip()
        
        # Try mapped replacements first
        for pattern, replacement in self.merchant_mappings.items():
            if pattern in description.upper():
                merchant = description.upper().replace(pattern.upper(), replacement)
                return self._cleanup_merchant_name(merchant)
        
        # Try extraction patterns
        for pattern in self.patterns:
            match = re.match(pattern, description, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                return self._cleanup_merchant_name(merchant)
        
        # Fallback: Take first few words (up to 3)
        words = description.split()
        if len(words) > 0:
            merchant = ' '.join(words[:min(3, len(words))])
            return self._cleanup_merchant_name(merchant)
        
        return None
    
    def _cleanup_merchant_name(self, merchant: str) -> str:
        """Clean up extracted merchant name"""
        if not merchant:
            return merchant
        
        # Apply cleanup patterns
        for pattern, replacement in self.cleanup_patterns:
            merchant = re.sub(pattern, replacement, merchant, flags=re.IGNORECASE)
        
        # Capitalize properly (Title Case)
        merchant = merchant.strip().title()
        
        # Remove extra spaces
        merchant = ' '.join(merchant.split())
        
        return merchant


# Global merchant extractor instance
merchant_extractor = MerchantExtractor()


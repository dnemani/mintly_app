"""
Transaction categorization logic
"""
import re
from typing import Dict, List
from app.models import CategoryEnum
import logging

logger = logging.getLogger(__name__)


class TransactionCategorizer:
    """Automatically categorize transactions based on merchant/description"""
    
    def __init__(self):
        # Define keyword patterns for each category
        self.category_patterns = {
            CategoryEnum.GROCERIES: [
                r'\bwhole foods\b', r'\btrader joe', r'\bsafeway\b', r'\bkroger\b',
                r'\bwalmart\b', r'\btarget\b', r'\bcostco\b', r'\bsams club\b',
                r'\baldi\b', r'\bpublix\b', r'\bfood lion\b', r'\bstop shop\b',
                r'\bwegmans\b', r'\bsprouts\b', r'\bgrocer', r'\bmarket\b',
                r'\bsupermarket\b'
            ],
            CategoryEnum.RESTAURANTS: [
                r'\brestaurant\b', r'\bcafe\b', r'\bcoffee\b', r'\bstarbucks\b',
                r'\bdunkin\b', r'\bmcdonald', r'\bburger\b', r'\bpizza\b',
                r'\btaco\b', r'\bsubway\b', r'\bchipotle\b', r'\bpanera\b',
                r'\bdining\b', r'\bbistro\b', r'\bgrill\b', r'\bbar\b',
                r'\bkitchen\b', r'\beatery\b', r'\bdiner\b', r'\bpub\b'
            ],
            CategoryEnum.TRANSPORTATION: [
                r'\bgas\b', r'\bshell\b', r'\bchevron\b', r'\bexxon\b',
                r'\bmobil\b', r'\bbp\b', r'\btexaco\b', r'\buber\b',
                r'\blyft\b', r'\bparking\b', r'\btransit\b', r'\bmetro\b',
                r'\btrain\b', r'\bbus\b', r'\btoll\b', r'\bauto\b'
            ],
            CategoryEnum.UTILITIES: [
                r'\belectric\b', r'\bpower\b', r'\bpge\b', r'\bwater\b',
                r'\bsewer\b', r'\binternet\b', r'\bcomcast\b', r'\bat&t\b',
                r'\bverizon\b', r'\bspectrum\b', r'\bphone\b', r'\bgas company\b',
                r'\butility\b'
            ],
            CategoryEnum.ENTERTAINMENT: [
                r'\bnetflix\b', r'\bhulu\b', r'\bspotify\b', r'\bapple music\b',
                r'\bcinema\b', r'\btheater\b', r'\bmovie\b', r'\bconcert\b',
                r'\bticket\b', r'\bgame\b', r'\bamuse', r'\bpark\b',
                r'\bsteam\b', r'\bplaystation\b', r'\bxbox\b'
            ],
            CategoryEnum.SHOPPING: [
                r'\bamazon\b', r'\bebay\b', r'\betsy\b', r'\bdepartment store\b',
                r'\bmacy', r'\bnordstrom\b', r'\bkohl', r'\bjcpenney\b',
                r'\bbest buy\b', r'\bhome depot\b', r'\blowe', r'\bikea\b',
                r'\bclothing\b', r'\bapparel\b', r'\bretail\b'
            ],
            CategoryEnum.HEALTHCARE: [
                r'\bpharmacy\b', r'\bcvs\b', r'\bwalgreens\b', r'\brite aid\b',
                r'\bdoctor\b', r'\bdental\b', r'\bmedical\b', r'\bhospital\b',
                r'\bclinic\b', r'\bhealth\b', r'\bcare\b', r'\boptical\b'
            ],
            CategoryEnum.TRAVEL: [
                r'\bairline\b', r'\bairport\b', r'\bhotel\b', r'\bmotel\b',
                r'\brental car\b', r'\bhertz\b', r'\benterprise\b', r'\bairbnb\b',
                r'\btravel\b', r'\bvacation\b', r'\bresort\b', r'\bcruise\b'
            ],
            CategoryEnum.HOUSING: [
                r'\brent\b', r'\bmortgage\b', r'\blandlord\b', r'\bproperty\b',
                r'\bhoa\b', r'\bhomeowners\b', r'\brepair\b', r'\bmaintenance\b'
            ],
            CategoryEnum.INSURANCE: [
                r'\binsurance\b', r'\bgeico\b', r'\bstate farm\b', r'\ballstate\b',
                r'\bprogressive\b', r'\bpolicy\b'
            ],
            CategoryEnum.EDUCATION: [
                r'\bschool\b', r'\buniversity\b', r'\bcollege\b', r'\btuition\b',
                r'\bcourse\b', r'\bbook store\b', r'\beducation\b', r'\blearning\b'
            ],
            CategoryEnum.PERSONAL_CARE: [
                r'\bsalon\b', r'\bbarber\b', r'\bspa\b', r'\bgym\b',
                r'\bfitness\b', r'\byoga\b', r'\bbeauty\b', r'\bhair\b'
            ],
            CategoryEnum.SUBSCRIPTIONS: [
                r'\bsubscription\b', r'\bmembership\b', r'\bmonthly\b',
                r'\bannual\b', r'\brenew'
            ]
        }
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = {
            category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for category, patterns in self.category_patterns.items()
        }
        
        logger.info("TransactionCategorizer initialized with pattern matching")
    
    def categorize(self, description: str, amount: float) -> CategoryEnum:
        """
        Categorize a transaction based on its description and amount
        
        Args:
            description: Transaction description/merchant name
            amount: Transaction amount (positive for income, negative for expense)
        
        Returns:
            CategoryEnum: The predicted category
        """
        # If positive amount, categorize as income
        if amount > 0:
            logger.debug(f"Categorized as INCOME: {description} (${amount})")
            return CategoryEnum.INCOME
        
        # Try to match patterns
        description_lower = description.lower()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description_lower):
                    logger.debug(f"Categorized as {category.value}: {description}")
                    return category
        
        # Default to uncategorized
        logger.debug(f"Categorized as UNCATEGORIZED: {description}")
        return CategoryEnum.UNCATEGORIZED
    
    def categorize_batch(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize multiple transactions
        
        Args:
            transactions: List of transaction dictionaries with 'description' and 'amount'
        
        Returns:
            List of transactions with 'category' field added
        """
        categorized = []
        for txn in transactions:
            category = self.categorize(txn['description'], txn['amount'])
            txn['category'] = category.value
            categorized.append(txn)
        
        logger.info(f"Categorized {len(transactions)} transactions")
        return categorized
    
    def add_custom_pattern(self, category: CategoryEnum, pattern: str):
        """Add a custom pattern for a category"""
        if category not in self.compiled_patterns:
            self.compiled_patterns[category] = []
        
        self.compiled_patterns[category].append(re.compile(pattern, re.IGNORECASE))
        logger.info(f"Added custom pattern '{pattern}' for category {category.value}")


# Global categorizer instance
categorizer = TransactionCategorizer()


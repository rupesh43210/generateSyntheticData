"""
Financial Transactions and Banking Data Generator - Creates comprehensive banking patterns and transaction history
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
import uuid

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    PURCHASE = "purchase"
    REFUND = "refund"
    INTEREST = "interest"
    FEE = "fee"
    INVESTMENT = "investment"
    LOAN_PAYMENT = "loan_payment"

class TransactionMethod(Enum):
    ATM = "atm"
    ONLINE = "online"
    MOBILE_APP = "mobile_app"
    BRANCH = "branch"
    CARD = "card"
    ACH = "ach"
    WIRE = "wire"
    CHECK = "check"
    CASH = "cash"
    DIRECT_DEPOSIT = "direct_deposit"

class AccountType(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    INVESTMENT = "investment"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    RETIREMENT = "retirement"

class TransactionCategory(Enum):
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    RENT_MORTGAGE = "rent_mortgage"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    RESTAURANTS = "restaurants"
    SALARY = "salary"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    EDUCATION = "education"
    TRAVEL = "travel"
    PERSONAL_CARE = "personal_care"
    OTHER = "other"

class BankAccount(BaseModel):
    account_id: str
    account_type: AccountType
    bank_name: str
    account_number: str
    routing_number: str
    balance: float
    opened_date: datetime
    is_primary: bool
    interest_rate: Optional[float]
    credit_limit: Optional[float]  # For credit accounts
    monthly_fee: Optional[float]

class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    date: datetime
    amount: float
    transaction_type: TransactionType
    method: TransactionMethod
    category: TransactionCategory
    description: str
    merchant_name: Optional[str]
    location: Optional[str]
    reference_number: Optional[str]
    balance_after: float
    is_recurring: bool

class Investment(BaseModel):
    investment_id: str
    type: str  # stocks, bonds, mutual_funds, etf, crypto, etc.
    symbol: Optional[str]
    name: str
    quantity: float
    purchase_price: float
    current_price: float
    purchase_date: datetime
    total_value: float
    gain_loss: float
    gain_loss_percent: float

class Loan(BaseModel):
    loan_id: str
    type: str  # mortgage, auto, personal, student, etc.
    lender: str
    original_amount: float
    current_balance: float
    interest_rate: float
    monthly_payment: float
    term_months: int
    start_date: datetime
    next_payment_date: datetime
    payment_history: List[Dict[str, Any]]

class CreditCard(BaseModel):
    card_id: str
    issuer: str
    card_type: str  # visa, mastercard, amex, etc.
    last_four: str
    credit_limit: float
    current_balance: float
    minimum_payment: float
    due_date: datetime
    apr: float
    rewards_program: Optional[str]
    annual_fee: float

class FinancialProfile(BaseModel):
    total_assets: float
    total_liabilities: float
    net_worth: float
    monthly_income: float
    monthly_expenses: float
    cash_flow: float
    bank_accounts: List[BankAccount]
    transactions: List[Transaction]
    investments: List[Investment]
    loans: List[Loan]
    credit_cards: List[CreditCard]
    financial_goals: List[str]
    risk_tolerance: str  # conservative, moderate, aggressive

class FinancialTransactionsGenerator:
    def __init__(self):
        self.banks = [
            "Chase Bank", "Bank of America", "Wells Fargo", "Citibank",
            "PNC Bank", "Capital One", "TD Bank", "US Bank", "Truist Bank",
            "Fifth Third Bank", "Regions Bank", "KeyBank", "First Republic"
        ]
        
        self.merchants = {
            "groceries": ["Whole Foods", "Safeway", "Kroger", "Target", "Walmart", "Trader Joe's"],
            "restaurants": ["McDonald's", "Starbucks", "Chipotle", "Olive Garden", "Subway", "Local Restaurant"],
            "utilities": ["PG&E", "ComEd", "Verizon", "AT&T", "Comcast", "Water District"],
            "transportation": ["Shell", "Chevron", "Uber", "Lyft", "Metro Transit", "Parking"],
            "entertainment": ["Netflix", "Spotify", "AMC Theaters", "Steam", "Amazon Prime"],
            "shopping": ["Amazon", "Target", "Macy's", "Best Buy", "Home Depot", "Nike"],
            "healthcare": ["CVS Pharmacy", "Walgreens", "Kaiser Permanente", "Local Clinic"]
        }
        
        self.investment_types = [
            {"type": "stocks", "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]},
            {"type": "etf", "symbols": ["SPY", "QQQ", "VTI", "VXUS", "BND"]},
            {"type": "mutual_funds", "symbols": ["VTSAX", "FXNAX", "VTIAX"]},
            {"type": "crypto", "symbols": ["BTC", "ETH", "ADA", "DOT"]}
        ]
        
        self.loan_types = [
            {"type": "mortgage", "rate_range": (2.5, 6.5), "term_range": (180, 360)},
            {"type": "auto", "rate_range": (3.0, 8.0), "term_range": (36, 84)},
            {"type": "personal", "rate_range": (6.0, 25.0), "term_range": (12, 60)},
            {"type": "student", "rate_range": (3.0, 7.0), "term_range": (120, 240)}
        ]

    def generate_financial_profile(self, age: int, income: float, credit_score: int, lifestyle: str) -> FinancialProfile:
        """Generate comprehensive financial profile"""
        
        # Generate bank accounts
        bank_accounts = self._generate_bank_accounts(age, income)
        
        # Generate transactions (last 6 months)
        transactions = self._generate_transactions(bank_accounts, income, lifestyle)
        
        # Generate investments based on age and income
        investments = self._generate_investments(age, income, lifestyle)
        
        # Generate loans based on age and income
        loans = self._generate_loans(age, income, credit_score)
        
        # Generate credit cards
        credit_cards = self._generate_credit_cards(income, credit_score)
        
        # Calculate financial summary
        total_assets = sum(acc.balance for acc in bank_accounts) + sum(inv.total_value for inv in investments)
        total_liabilities = sum(loan.current_balance for loan in loans) + sum(card.current_balance for card in credit_cards)
        net_worth = total_assets - total_liabilities
        
        # Monthly expenses from transactions
        monthly_expenses = self._calculate_monthly_expenses(transactions)
        cash_flow = income - monthly_expenses
        
        # Financial goals based on age and income
        financial_goals = self._generate_financial_goals(age, income, net_worth)
        
        # Risk tolerance
        risk_tolerance = self._determine_risk_tolerance(age, income, lifestyle)
        
        return FinancialProfile(
            total_assets=round(total_assets, 2),
            total_liabilities=round(total_liabilities, 2),
            net_worth=round(net_worth, 2),
            monthly_income=round(income, 2),
            monthly_expenses=round(monthly_expenses, 2),
            cash_flow=round(cash_flow, 2),
            bank_accounts=bank_accounts,
            transactions=transactions,
            investments=investments,
            loans=loans,
            credit_cards=credit_cards,
            financial_goals=financial_goals,
            risk_tolerance=risk_tolerance
        )

    def _generate_bank_accounts(self, age: int, income: float) -> List[BankAccount]:
        """Generate realistic bank accounts"""
        accounts = []
        
        # Primary checking account (everyone has one)
        primary_bank = random.choice(self.banks)
        checking_balance = random.uniform(income * 0.1, income * 0.5)
        
        accounts.append(BankAccount(
            account_id=str(uuid.uuid4()),
            account_type=AccountType.CHECKING,
            bank_name=primary_bank,
            account_number=f"****{random.randint(1000, 9999)}",
            routing_number=f"{random.randint(100000000, 999999999)}",
            balance=checking_balance,
            opened_date=datetime.now() - timedelta(days=random.randint(365, 3650)),
            is_primary=True,
            interest_rate=0.01,
            credit_limit=None,
            monthly_fee=0.0
        ))
        
        # Savings account (80% chance)
        if random.random() < 0.8:
            savings_balance = random.uniform(income * 0.5, income * 2.0)
            accounts.append(BankAccount(
                account_id=str(uuid.uuid4()),
                account_type=AccountType.SAVINGS,
                bank_name=primary_bank,
                account_number=f"****{random.randint(1000, 9999)}",
                routing_number=f"{random.randint(100000000, 999999999)}",
                balance=savings_balance,
                opened_date=datetime.now() - timedelta(days=random.randint(365, 2000)),
                is_primary=False,
                interest_rate=random.uniform(0.5, 2.5),
                credit_limit=None,
                monthly_fee=0.0
            ))
        
        # Investment account (if higher income)
        if income > 75000 and random.random() < 0.6:
            investment_balance = random.uniform(income * 0.5, income * 5.0)
            accounts.append(BankAccount(
                account_id=str(uuid.uuid4()),
                account_type=AccountType.INVESTMENT,
                bank_name=random.choice(["Fidelity", "Vanguard", "Charles Schwab", "E*TRADE"]),
                account_number=f"****{random.randint(1000, 9999)}",
                routing_number=f"{random.randint(100000000, 999999999)}",
                balance=investment_balance,
                opened_date=datetime.now() - timedelta(days=random.randint(365, 1825)),
                is_primary=False,
                interest_rate=None,
                credit_limit=None,
                monthly_fee=0.0
            ))
        
        return accounts

    def _generate_transactions(self, accounts: List[BankAccount], income: float, lifestyle: str) -> List[Transaction]:
        """Generate realistic transaction history for last 6 months"""
        transactions = []
        primary_account = next((acc for acc in accounts if acc.is_primary), accounts[0])
        
        # Generate transactions for last 6 months
        start_date = datetime.now() - timedelta(days=180)
        current_balance = primary_account.balance
        
        # Monthly recurring transactions
        for month in range(6):
            month_start = start_date + timedelta(days=30 * month)
            
            # Salary deposit
            salary_date = month_start + timedelta(days=random.randint(1, 5))
            transactions.append(Transaction(
                transaction_id=str(uuid.uuid4()),
                account_id=primary_account.account_id,
                date=salary_date,
                amount=income,
                transaction_type=TransactionType.DEPOSIT,
                method=TransactionMethod.DIRECT_DEPOSIT,
                category=TransactionCategory.SALARY,
                description="Salary Deposit",
                merchant_name="Employer",
                location=None,
                reference_number=f"DD{random.randint(100000, 999999)}",
                balance_after=current_balance + income,
                is_recurring=True
            ))
            current_balance += income
            
            # Monthly expenses
            monthly_transactions = self._generate_monthly_transactions(
                primary_account.account_id, month_start, income, lifestyle
            )
            
            for trans in monthly_transactions:
                current_balance -= trans.amount
                trans.balance_after = current_balance
                transactions.append(trans)
        
        return sorted(transactions, key=lambda x: x.date, reverse=True)

    def _generate_monthly_transactions(self, account_id: str, month_start: datetime, income: float, lifestyle: str) -> List[Transaction]:
        """Generate monthly transactions"""
        transactions = []
        
        # Base transaction counts by lifestyle
        transaction_counts = {
            "minimalist": 15,
            "average": 25,
            "luxury": 40
        }
        
        num_transactions = transaction_counts.get(lifestyle, 25) + random.randint(-5, 10)
        
        for i in range(num_transactions):
            # Random date in month
            trans_date = month_start + timedelta(days=random.randint(0, 29))
            
            # Select category and merchant
            category = random.choice(list(TransactionCategory))
            if category == TransactionCategory.SALARY:
                continue  # Skip salary here, handled separately
            
            merchant_name = self._get_merchant_for_category(category)
            amount = self._get_amount_for_category(category, income, lifestyle)
            
            transactions.append(Transaction(
                transaction_id=str(uuid.uuid4()),
                account_id=account_id,
                date=trans_date,
                amount=amount,
                transaction_type=TransactionType.PURCHASE,
                method=random.choice([TransactionMethod.CARD, TransactionMethod.ONLINE, TransactionMethod.MOBILE_APP]),
                category=category,
                description=f"Purchase at {merchant_name}",
                merchant_name=merchant_name,
                location=f"{random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston'])}, NY",
                reference_number=f"TXN{random.randint(100000, 999999)}",
                balance_after=0,  # Will be set later
                is_recurring=category in [TransactionCategory.UTILITIES, TransactionCategory.RENT_MORTGAGE]
            ))
        
        return transactions

    def _generate_investments(self, age: int, income: float, lifestyle: str) -> List[Investment]:
        """Generate investment portfolio"""
        investments = []
        
        # Investment likelihood based on income and age
        if income < 50000 or age < 25:
            investment_chance = 0.3
        elif income < 100000:
            investment_chance = 0.6
        else:
            investment_chance = 0.8
        
        if random.random() > investment_chance:
            return investments
        
        # Number of investments
        num_investments = random.randint(3, 8)
        
        for _ in range(num_investments):
            inv_type = random.choice(self.investment_types)
            symbol = random.choice(inv_type["symbols"])
            
            purchase_price = random.uniform(10, 500)
            current_price = purchase_price * random.uniform(0.7, 1.5)  # -30% to +50% change
            quantity = random.uniform(1, 100)
            
            total_value = current_price * quantity
            gain_loss = (current_price - purchase_price) * quantity
            gain_loss_percent = ((current_price - purchase_price) / purchase_price) * 100
            
            investments.append(Investment(
                investment_id=str(uuid.uuid4()),
                type=inv_type["type"],
                symbol=symbol,
                name=f"{symbol} Investment",
                quantity=round(quantity, 2),
                purchase_price=round(purchase_price, 2),
                current_price=round(current_price, 2),
                purchase_date=datetime.now() - timedelta(days=random.randint(30, 1095)),
                total_value=round(total_value, 2),
                gain_loss=round(gain_loss, 2),
                gain_loss_percent=round(gain_loss_percent, 1)
            ))
        
        return investments

    def _generate_loans(self, age: int, income: float, credit_score: int) -> List[Loan]:
        """Generate loans based on demographics"""
        loans = []
        
        # Mortgage (if age > 25 and income > 60k)
        if age > 25 and income > 60000 and random.random() < 0.4:
            mortgage_type = random.choice(self.loan_types)
            if mortgage_type["type"] == "mortgage":
                original_amount = random.uniform(200000, 800000)
                rate = random.uniform(*mortgage_type["rate_range"])
                term = random.choice([180, 240, 300, 360])
                
                loans.append(self._create_loan("mortgage", original_amount, rate, term))
        
        # Auto loan (60% chance if age > 18)
        if age > 18 and random.random() < 0.6:
            auto_loan = next(l for l in self.loan_types if l["type"] == "auto")
            original_amount = random.uniform(15000, 60000)
            rate = random.uniform(*auto_loan["rate_range"])
            term = random.choice([36, 48, 60, 72])
            
            loans.append(self._create_loan("auto", original_amount, rate, term))
        
        # Student loan (if age < 40)
        if age < 40 and random.random() < 0.3:
            student_loan = next(l for l in self.loan_types if l["type"] == "student")
            original_amount = random.uniform(20000, 100000)
            rate = random.uniform(*student_loan["rate_range"])
            term = random.choice([120, 180, 240])
            
            loans.append(self._create_loan("student", original_amount, rate, term))
        
        return loans

    def _create_loan(self, loan_type: str, original_amount: float, rate: float, term_months: int) -> Loan:
        """Create a loan with payment history"""
        start_date = datetime.now() - timedelta(days=random.randint(365, 1825))
        monthly_payment = self._calculate_monthly_payment(original_amount, rate / 100 / 12, term_months)
        
        # Calculate current balance
        months_paid = min(random.randint(6, 60), term_months)
        current_balance = self._calculate_remaining_balance(original_amount, rate / 100 / 12, term_months, months_paid)
        
        # Generate payment history
        payment_history = []
        for i in range(min(months_paid, 12)):  # Last 12 payments
            payment_date = start_date + timedelta(days=30 * (months_paid - i))
            payment_history.append({
                "date": payment_date.isoformat(),
                "amount": monthly_payment,
                "principal": monthly_payment * random.uniform(0.6, 0.8),
                "interest": monthly_payment * random.uniform(0.2, 0.4),
                "status": "paid"
            })
        
        return Loan(
            loan_id=str(uuid.uuid4()),
            type=loan_type,
            lender=random.choice(self.banks),
            original_amount=round(original_amount, 2),
            current_balance=round(max(0, current_balance), 2),
            interest_rate=round(rate, 2),
            monthly_payment=round(monthly_payment, 2),
            term_months=term_months,
            start_date=start_date,
            next_payment_date=start_date + timedelta(days=30 * (months_paid + 1)),
            payment_history=payment_history
        )

    def _generate_credit_cards(self, income: float, credit_score: int) -> List[CreditCard]:
        """Generate credit cards"""
        cards = []
        
        # Number of cards based on income and credit score
        if income < 50000 or credit_score < 650:
            num_cards = random.randint(1, 2)
        elif income < 100000:
            num_cards = random.randint(2, 3)
        else:
            num_cards = random.randint(2, 4)
        
        card_types = ["Visa", "Mastercard", "American Express", "Discover"]
        issuers = ["Chase", "Capital One", "Citi", "Bank of America", "American Express"]
        
        for _ in range(num_cards):
            credit_limit = self._calculate_credit_limit(income, credit_score)
            current_balance = credit_limit * random.uniform(0.1, 0.6)  # 10-60% utilization
            
            cards.append(CreditCard(
                card_id=str(uuid.uuid4()),
                issuer=random.choice(issuers),
                card_type=random.choice(card_types),
                last_four=f"{random.randint(1000, 9999)}",
                credit_limit=credit_limit,
                current_balance=round(current_balance, 2),
                minimum_payment=round(current_balance * 0.02, 2),  # 2% minimum
                due_date=datetime.now() + timedelta(days=random.randint(5, 25)),
                apr=random.uniform(15.0, 25.0),
                rewards_program=random.choice([None, "Cash Back", "Points", "Miles"]),
                annual_fee=random.choice([0, 95, 195, 450])
            ))
        
        return cards

    def _get_merchant_for_category(self, category: TransactionCategory) -> str:
        """Get merchant name for category"""
        category_key = category.value
        if category_key in self.merchants:
            return random.choice(self.merchants[category_key])
        return f"Generic {category.value.title()}"

    def _get_amount_for_category(self, category: TransactionCategory, income: float, lifestyle: str) -> float:
        """Get realistic amount for transaction category"""
        base_multiplier = {"minimalist": 0.7, "average": 1.0, "luxury": 1.5}.get(lifestyle, 1.0)
        
        category_ranges = {
            TransactionCategory.GROCERIES: (30, 150),
            TransactionCategory.UTILITIES: (80, 300),
            TransactionCategory.RENT_MORTGAGE: (income * 0.2, income * 0.4),
            TransactionCategory.TRANSPORTATION: (20, 100),
            TransactionCategory.ENTERTAINMENT: (15, 80),
            TransactionCategory.HEALTHCARE: (50, 300),
            TransactionCategory.SHOPPING: (25, 200),
            TransactionCategory.RESTAURANTS: (15, 100),
            TransactionCategory.INSURANCE: (100, 500),
            TransactionCategory.EDUCATION: (100, 1000),
            TransactionCategory.TRAVEL: (200, 2000),
            TransactionCategory.PERSONAL_CARE: (20, 100),
            TransactionCategory.OTHER: (10, 100)
        }
        
        min_amount, max_amount = category_ranges.get(category, (10, 100))
        amount = random.uniform(min_amount, max_amount) * base_multiplier
        return round(amount, 2)

    def _calculate_monthly_expenses(self, transactions: List[Transaction]) -> float:
        """Calculate average monthly expenses from transactions"""
        expense_transactions = [t for t in transactions if t.transaction_type == TransactionType.PURCHASE]
        if not expense_transactions:
            return 0
        
        total_expenses = sum(t.amount for t in expense_transactions)
        months = 6  # We generated 6 months of data
        return total_expenses / months

    def _generate_financial_goals(self, age: int, income: float, net_worth: float) -> List[str]:
        """Generate realistic financial goals"""
        goals = []
        
        if age < 30:
            goals.extend(["Build emergency fund", "Pay off student loans", "Start investing"])
        elif age < 50:
            goals.extend(["Save for house down payment", "Increase retirement savings", "Children's education fund"])
        else:
            goals.extend(["Maximize retirement savings", "Pay off mortgage", "Estate planning"])
        
        if net_worth < income * 2:
            goals.append("Increase net worth")
        
        return random.sample(goals, min(3, len(goals)))

    def _determine_risk_tolerance(self, age: int, income: float, lifestyle: str) -> str:
        """Determine investment risk tolerance"""
        if age < 35 and income > 75000:
            return random.choice(["moderate", "aggressive"])
        elif age > 55:
            return random.choice(["conservative", "moderate"])
        else:
            return "moderate"

    def _calculate_monthly_payment(self, principal: float, monthly_rate: float, num_payments: int) -> float:
        """Calculate monthly loan payment"""
        if monthly_rate == 0:
            return principal / num_payments
        
        return principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)

    def _calculate_remaining_balance(self, principal: float, monthly_rate: float, total_payments: int, payments_made: int) -> float:
        """Calculate remaining loan balance"""
        if monthly_rate == 0:
            return principal * (total_payments - payments_made) / total_payments
        
        monthly_payment = self._calculate_monthly_payment(principal, monthly_rate, total_payments)
        
        balance = principal
        for _ in range(payments_made):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment
        
        return balance

    def _calculate_credit_limit(self, income: float, credit_score: int) -> float:
        """Calculate credit card limit based on income and credit score"""
        base_limit = income * 0.2  # 20% of annual income
        
        # Adjust based on credit score
        if credit_score >= 750:
            multiplier = 1.5
        elif credit_score >= 700:
            multiplier = 1.2
        elif credit_score >= 650:
            multiplier = 1.0
        else:
            multiplier = 0.7
        
        return round(base_limit * multiplier * random.uniform(0.8, 1.2), 2)
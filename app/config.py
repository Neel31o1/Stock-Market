"""
Configuration file for Stock Market Investment Automation
Edit this file to customize your investment parameters
"""

import os
from datetime import datetime

# ============================================================================
# INVESTMENT CONFIGURATION
# ============================================================================

# Monthly investment amounts
MONTHLY_INVESTMENT = 15000  # Total monthly investment in INR
NIFTY50_ALLOCATION = 10000  # Amount for Nifty 50 stocks (67%)
DIVERSIFIED_ALLOCATION = 5000  # Amount for diversified investments (33%)

# Investment start date and schedule
START_DATE = "2025-11-01"  # Format: YYYY-MM-DD - When you'll start investing
INVESTMENT_DAY = 5  # Day of month to invest (5th is recommended)

# Investor details (customize this!)
INVESTOR_NAME = "Neel Shah"  # Your name
INVESTOR_AGE = 26  # Your current age
INVESTMENT_HORIZON = 20  # Investment period in years

# ============================================================================
# NIFTY 50 STOCK ROTATION (Top 12 blue-chip stocks)
# ============================================================================

NIFTY50_STOCKS = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy/Retail"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services", "sector": "IT Services"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Banking"},
    {"ticker": "INFY.NS", "name": "Infosys", "sector": "IT Services"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Banking"},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "FMCG"},
    {"ticker": "ITC.NS", "name": "ITC Limited", "sector": "FMCG"},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecom"},
    {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro", "sector": "Infrastructure"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank", "sector": "Banking"},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "NBFC"},
]

# ============================================================================
# ETF CONFIGURATION (Low-cost passive investment options)
# ============================================================================

CORE_ETF = {
    "ticker": "NIFTYBEES.NS",
    "name": "Nippon India ETF Nifty BeES",
    "allocation": 5000  # ₹5,000 monthly to core ETF
}

MID_CAP_ETF = {
    "ticker": "JUNIORBEES.NS",
    "name": "Nippon India ETF Junior BeES",  # Nifty Next 50
    "allocation": 2000
}

GOLD_ETF = {
    "ticker": "GOLDBEES.NS",
    "name": "Nippon India ETF Gold BeES",
    "allocation": 500  # Gold hedge
}

# ============================================================================
# EMAIL NOTIFICATION SETTINGS
# ============================================================================

# Email configuration
EMAIL_ENABLED = True  # Set to True to enable email reminders
EMAIL_FROM = "nealshah8888@gmail.com"  # Your email (sender)
EMAIL_TO = ["nealshah8888@gmail.com", "shahtirth547@gmail.com"]  # Recipients (you and your friend)
EMAIL_PASSWORD = ""  # Leave empty - stored in .env file for security

# Gmail SMTP settings (don't change these)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True

# ============================================================================
# REMINDER & NOTIFICATION SETTINGS
# ============================================================================

# Desktop notification settings
DESKTOP_NOTIFICATIONS = False  # Disabled for macOS compatibility

# Reminder schedule (days before investment day)
REMINDER_DAYS_BEFORE = [5, 3, 1]  # Send reminders 5, 3, and 1 day before
REMINDER_TIME = "09:00"  # Time to send reminder (24-hour format)

# ============================================================================
# FILE PATHS (automatically set based on project structure)
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
APP_DIR = os.path.join(BASE_DIR, "app")

# Data files
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.csv")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.csv")
MONTHLY_PLANS_FILE = os.path.join(DATA_DIR, "monthly_plans.json")

# ============================================================================
# PYSPARK CONFIGURATION
# ============================================================================

SPARK_APP_NAME = "Stock Market Investment Analyzer"
SPARK_MASTER = "local[*]"  # Use all available CPU cores
SPARK_MEMORY = "4g"  # Driver memory allocation

# ============================================================================
# RETURN ASSUMPTIONS (for projections)
# ============================================================================

EXPECTED_RETURNS = {
    "conservative": 0.11,  # 11% annual return
    "moderate": 0.12,      # 12% annual return (realistic)
    "optimistic": 0.14,    # 14% annual return
}

# ============================================================================
# COLORS FOR TERMINAL OUTPUT (makes CLI pretty!)
# ============================================================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.path.join(BASE_DIR, "logs", f"investment_{datetime.now().strftime('%Y%m%d')}.log")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

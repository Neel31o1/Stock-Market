"""
Date Utilities - Handle all date-related operations
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_next_investment_date(investment_day=5):
    """
    Calculate next investment date
    
    Args:
        investment_day: Day of month (default 5)
    
    Returns:
        datetime: Next investment date
    """
    today = datetime.now()
    
    # If we haven't passed investment day this month
    if today.day < investment_day:
        next_date = today.replace(day=investment_day)
    else:
        # Move to next month
        next_month = today + relativedelta(months=1)
        next_date = next_month.replace(day=investment_day)
    
    return next_date


def format_date(date, format_string="%Y-%m-%d"):
    """
    Format date object
    
    Args:
        date: datetime object
        format_string: Format string
    
    Returns:
        str: Formatted date
    """
    return date.strftime(format_string)


def format_date_display(date):
    """
    Format date for display (e.g., "November 5, 2025")
    
    Args:
        date: datetime object
    
    Returns:
        str: Formatted date string
    """
    return date.strftime("%B %d, %Y")


def days_until(target_date):
    """
    Calculate days until target date
    
    Args:
        target_date: datetime object
    
    Returns:
        int: Number of days
    """
    today = datetime.now()
    return (target_date - today).days

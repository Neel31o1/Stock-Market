"""
Formatters - Format data for display
"""


def format_currency(amount, decimals=0):
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
    
    Returns:
        str: Formatted currency
    """
    if decimals == 0:
        return f"₹{amount:,.0f}"
    return f"₹{amount:,.{decimals}f}"


def format_percentage(value, decimals=1):
    """
    Format value as percentage
    
    Args:
        value: Value to format
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage
    """
    return f"{value:.{decimals}f}%"


def format_lakhs(amount, decimals=2):
    """
    Format amount in lakhs
    
    Args:
        amount: Amount to format
        decimals: Number of decimal places
    
    Returns:
        str: Formatted amount in lakhs
    """
    lakhs = amount / 100000
    return f"{lakhs:.{decimals}f}"


def get_company_initials(company_name):
    """
    Get company initials for logo
    
    Args:
        company_name: Full company name
    
    Returns:
        str: Initials (2-3 letters)
    """
    words = company_name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return company_name[:2].upper()

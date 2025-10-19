"""Reminder Service - Premium Design"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import (
    INVESTMENT_DAY,
    REMINDER_DAYS_BEFORE,
    MONTHLY_PLANS_FILE,
    MONTHLY_INVESTMENT,
    INVESTMENT_HORIZON,
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_SERVER,
    SMTP_PORT,
    Colors
)
from services.email_service import EmailService
from utils.date_utils import get_next_investment_date, format_date, format_date_display, days_until
from utils.formatter import format_lakhs, format_percentage


COMPANY_LOGOS = {
    "NIFTYBEES.NS": "https://cdn.nseindia.com/images/logos/nifty50logo.png",
    "RELIANCE.NS": "https://logo.clearbit.com/ril.com",
    "TCS.NS": "https://logo.clearbit.com/tcs.com",
    "HDFCBANK.NS": "https://logo.clearbit.com/hdfcbank.com",
    "INFY.NS": "https://logo.clearbit.com/infosys.com",
    "ICICIBANK.NS": "https://logo.clearbit.com/icicibank.com",
    "HINDUNILVR.NS": "https://logo.clearbit.com/hul.co.in",
    "ITC.NS": "https://logo.clearbit.com/itcportal.com",
    "BHARTIARTL.NS": "https://logo.clearbit.com/airtel.in",
    "SBIN.NS": "https://logo.clearbit.com/sbi.co.in",
    "LT.NS": "https://logo.clearbit.com/larsentoubro.com",
    "AXISBANK.NS": "https://logo.clearbit.com/axisbank.com",
    "BAJFINANCE.NS": "https://logo.clearbit.com/bajajfinserv.in",
}


class ReminderService:
    """Handle investment reminders"""
    
    def __init__(self):
        self.plans = self.load_plans()
        
        email_password = os.getenv('EMAIL_PASSWORD')
        self.email_service = EmailService(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            email_from=EMAIL_FROM,
            email_password=email_password
        )
    
    def load_plans(self):
        """Load monthly plans from JSON"""
        try:
            if not os.path.exists(MONTHLY_PLANS_FILE):
                print(f"{Colors.FAIL}❌ Monthly plans not found!{Colors.ENDC}")
                return []
            
            with open(MONTHLY_PLANS_FILE, 'r') as f:
                plans = json.load(f)
            
            print(f"{Colors.OKGREEN}✅ Loaded {len(plans)} monthly plans{Colors.ENDC}")
            return plans
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error loading plans: {e}{Colors.ENDC}")
            return []
    
    def get_plan_for_date(self, target_date):
        """Get investment plan for specific date"""
        target_str = format_date(target_date)
        
        for plan in self.plans:
            if plan["investment_day"] == target_str:
                return plan
        
        return None
    
    def should_send_reminder(self):
        """Check if reminder should be sent today"""
        next_investment = get_next_investment_date(INVESTMENT_DAY)
        days_until_investment = days_until(next_investment)
        return days_until_investment in REMINDER_DAYS_BEFORE
    
    def build_email_data(self, plan):
        """Build data dictionary for email template"""
        months_invested = plan['month_number']
        total_invested = MONTHLY_INVESTMENT * months_invested
        
        monthly_rate = 0.12 / 12
        if months_invested > 0:
            current_value = MONTHLY_INVESTMENT * (((1 + monthly_rate) ** months_invested - 1) / monthly_rate) * (1 + monthly_rate)
            returns = current_value - total_invested
            return_pct = (returns / total_invested * 100) if total_invested > 0 else 0
        else:
            current_value = 0
            returns = 0
            return_pct = 0
        
        nifty50_rows = self._build_nifty50_rows(plan)
        diversified_rows = self._build_diversified_rows(plan)
        
        investment_date_obj = datetime.strptime(plan['investment_day'], "%Y-%m-%d")
        
        return {
            'investment_date': format_date_display(investment_date_obj),
            'month_number': plan['month_number'],
            'year_number': plan['year'],
            'age': plan['age'],
            'phase': plan['phase'],
            'total_invested': format_lakhs(total_invested),
            'current_value': format_lakhs(current_value),
            'returns': format_lakhs(returns),
            'return_pct': format_percentage(return_pct),
            'nifty50_total': f"₹{plan['nifty50']['total']:,}",
            'diversified_total': f"₹{plan['diversified']['total']:,}",
            'nifty50_rows': nifty50_rows,
            'diversified_rows': diversified_rows,
            'timestamp': datetime.now().strftime("%B %d, %Y at %I:%M %p EST")
        }
    
    def _build_nifty50_rows(self, plan):
        """Build premium HTML rows for Nifty 50 table"""
        rows = []
        
        # ETF row
        etf = plan['nifty50']['etf']
        logo_url = COMPANY_LOGOS.get(etf['ticker'], 'https://via.placeholder.com/48/3b82f6/ffffff?text=ETF')
        
        rows.append(f"""
            <tr style="border-top: 1px solid #f3f4f6;">
                <td style="padding: 16px;">
                    <table cellpadding="0" cellspacing="0" border="0">
                        <tr>
                            <td width="48" style="padding-right: 12px;">
                                <img src="{logo_url}" width="48" height="48" style="border-radius: 8px; display: block;" alt="{etf['name']}" />
                            </td>
                            <td>
                                <p style="margin: 0; color: #111827; font-size: 14px; font-weight: 600;">{etf['name']}</p>
                                <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 12px; font-weight: 500;">{etf['ticker']}</p>
                            </td>
                        </tr>
                    </table>
                </td>
                <td style="padding: 16px;">
                    <span style="background-color: #eff6ff; padding: 6px 10px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; color: #1e40af; font-weight: 600;">{etf['ticker']}</span>
                </td>
                <td style="padding: 16px; color: #6b7280; font-size: 13px; font-weight: 500;">Index ETF</td>
                <td align="right" style="padding: 16px; color: #059669; font-size: 15px; font-weight: 700;">₹{etf['amount']:,}</td>
            </tr>
        """)
        
        # Stock rows
        for stock in plan['nifty50']['stocks']:
            logo_url = COMPANY_LOGOS.get(stock['ticker'], f'https://via.placeholder.com/48/3b82f6/ffffff?text={stock["name"][:2]}')
            
            rows.append(f"""
                <tr style="border-top: 1px solid #f3f4f6;">
                    <td style="padding: 16px;">
                        <table cellpadding="0" cellspacing="0" border="0">
                            <tr>
                                <td width="48" style="padding-right: 12px;">
                                    <img src="{logo_url}" width="48" height="48" style="border-radius: 8px; display: block;" alt="{stock['name']}" />
                                </td>
                                <td>
                                    <p style="margin: 0; color: #111827; font-size: 14px; font-weight: 600;">{stock['name']}</p>
                                    <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 12px; font-weight: 500;">{stock['ticker']}</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                    <td style="padding: 16px;">
                        <span style="background-color: #eff6ff; padding: 6px 10px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; color: #1e40af; font-weight: 600;">{stock['ticker']}</span>
                    </td>
                    <td style="padding: 16px; color: #6b7280; font-size: 13px; font-weight: 500;">{stock['sector']}</td>
                    <td align="right" style="padding: 16px; color: #059669; font-size: 15px; font-weight: 700;">₹{stock['amount']:,}</td>
                </tr>
            """)
        
        return '\n'.join(rows)
    
    def _build_diversified_rows(self, plan):
        """Build premium HTML rows for diversified table"""
        rows = []
        
        for category, details in plan['diversified']['breakdown'].items():
            cat_name = category.replace('_', ' ').title()
            rows.append(f"""
                <tr style="border-top: 1px solid #f3f4f6;">
                    <td style="padding: 16px; color: #111827; font-size: 14px; font-weight: 600;">{cat_name}</td>
                    <td style="padding: 16px; color: #6b7280; font-size: 13px; font-weight: 500;">{details['instrument']}</td>
                    <td align="right" style="padding: 16px; color: #059669; font-size: 15px; font-weight: 700;">₹{details['amount']:,}</td>
                </tr>
            """)
        
        return '\n'.join(rows)
    
    def send_reminder(self, plan):
        """Send email reminder for given plan"""
        try:
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'templates', 'email', 'investment_reminder.html'
            )
            
            template = self.email_service.load_template(template_path)
            if not template:
                return False
            
            email_data = self.build_email_data(plan)
            html_content = self.email_service.render_template(template, email_data)
            
            subject = f"🔔 Investment Reminder - {email_data['investment_date']}"
            
            return self.email_service.send_email(
                recipients=EMAIL_TO,
                subject=subject,
                html_content=html_content
            )
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error sending reminder: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_test_email(self):
        """Send test email for next investment"""
        next_date = get_next_investment_date(INVESTMENT_DAY)
        plan = self.get_plan_for_date(next_date)
        
        if plan:
            print(f"\n{Colors.OKCYAN}📧 Sending premium Angel One-inspired email...{Colors.ENDC}")
            success = self.send_reminder(plan)
            if success:
                print(f"{Colors.OKGREEN}✅ Premium email sent!{Colors.ENDC}")
                print(f"{Colors.OKGREEN}📧 Check: neelshah3100@gmail.com & shahtirth547@gmail.com{Colors.ENDC}")
            return success
        else:
            print(f"{Colors.FAIL}❌ No plan found{Colors.ENDC}")
            return False


def main():
    """CLI for reminder service"""
    service = ReminderService()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        service.send_test_email()
    else:
        print("Usage: python reminder_service.py test")


if __name__ == "__main__":
    main()


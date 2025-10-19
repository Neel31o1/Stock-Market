"""
Reminder Service - Automated monthly investment reminders
Sends notifications 5, 3, and 1 days before investment day
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing notification library (optional dependency)
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

from config import (
    INVESTMENT_DAY,
    REMINDER_DAYS_BEFORE,
    DESKTOP_NOTIFICATIONS,
    MONTHLY_PLANS_FILE,
    Colors,
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_TO,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USE_TLS,
    INVESTOR_NAME
)


class ReminderService:
    """
    Automated reminder service for monthly investments
    
    Features:
    - Calculates next investment date
    - Sends reminders at scheduled intervals
    - Email notifications with beautiful HTML
    - Beautiful CLI output
    - Can run as background service
    """
    
    def __init__(self):
        """Initialize reminder service and load monthly plans"""
        self.load_monthly_plans()
    
    def load_monthly_plans(self):
        """Load pre-generated monthly plans from JSON file"""
        try:
            if not os.path.exists(MONTHLY_PLANS_FILE):
                print(f"{Colors.FAIL}❌ Monthly plans not found!{Colors.ENDC}")
                print(f"{Colors.WARNING}Run: python investment_planner.py first{Colors.ENDC}")
                self.plans = []
                return
            
            with open(MONTHLY_PLANS_FILE, 'r') as f:
                self.plans = json.load(f)
            
            print(f"{Colors.OKGREEN}✅ Loaded {len(self.plans)} monthly plans{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error loading plans: {e}{Colors.ENDC}")
            self.plans = []
    
    def get_next_investment_date(self):
        """
        Calculate next investment date
        
        Returns:
            datetime: Next investment date (5th of next month)
        """
        today = datetime.now()
        
        # If we haven't passed investment day this month
        if today.day < INVESTMENT_DAY:
            next_date = today.replace(day=INVESTMENT_DAY)
        else:
            # Move to next month
            next_month = today + relativedelta(months=1)
            next_date = next_month.replace(day=INVESTMENT_DAY)
        
        return next_date
    
    def get_plan_for_date(self, target_date):
        """
        Get investment plan for specific date
        
        Args:
            target_date: datetime object
        
        Returns:
            dict: Investment plan or None
        """
        target_str = target_date.strftime("%Y-%m-%d")
        
        for plan in self.plans:
            if plan["investment_day"] == target_str:
                return plan
        
        return None
    
    def should_send_reminder(self):
        """
        Check if reminder should be sent today
        
        Returns:
            bool: True if reminder should be sent
        """
        today = datetime.now()
        next_investment = self.get_next_investment_date()
        days_until = (next_investment - today).days
        
        return days_until in REMINDER_DAYS_BEFORE
    
    def format_investment_summary(self, plan):
        """
        Format investment plan as readable text
        
        Args:
            plan: Investment plan dictionary
        
        Returns:
            str: Formatted summary
        """
        summary = []
        summary.append("="*70)
        summary.append(f"🔔 INVESTMENT REMINDER - {plan['investment_day']}")
        summary.append("="*70)
        summary.append(f"Month {plan['month_number']} | Year {plan['year']} | Age {plan['age']}")
        summary.append(f"Phase: {plan['phase']}")
        summary.append("")
        summary.append(f"💰 TOTAL TO INVEST: ₹{plan['total_investment']:,}")
        summary.append("")
        
        # Nifty 50 section
        summary.append(f"📊 NIFTY 50 (₹{plan['nifty50']['total']:,})")
        summary.append("-" * 70)
        
        etf = plan['nifty50']['etf']
        summary.append(f"  ✓ ₹{etf['amount']:,} → {etf['name']}")
        summary.append(f"    Ticker: {etf['ticker']}")
        
        for stock in plan['nifty50']['stocks']:
            summary.append(f"  ✓ ₹{stock['amount']:,} → {stock['name']}")
            summary.append(f"    Ticker: {stock['ticker']} | Sector: {stock['sector']}")
        
        summary.append("")
        
        # Diversified section
        summary.append(f"🌈 DIVERSIFIED (₹{plan['diversified']['total']:,})")
        summary.append("-" * 70)
        
        for category, details in plan['diversified']['breakdown'].items():
            cat_name = category.replace('_', ' ').title()
            summary.append(f"  ✓ ₹{details['amount']:,} → {cat_name}")
            summary.append(f"    Instrument: {details['instrument']}")
        
        summary.append("")
        
        # Sectoral recommendation
        sectoral = plan['sectoral_fund']
        summary.append("🏭 SECTORAL FUND RECOMMENDATION")
        summary.append("-" * 70)
        summary.append(f"  Sector: {sectoral['sector']}")
        summary.append(f"  Recommended: {', '.join(sectoral['recommended_funds'])}")
        summary.append(f"  Rationale: {sectoral['rationale']}")
        
        # Notes
        if plan['notes']:
            summary.append("")
            summary.append("📝 NOTES:")
            for note in plan['notes']:
                summary.append(f"  {note}")
        
        summary.append("")
        summary.append("="*70)
        summary.append("⏰ Remember to invest on the 5th!")
        summary.append("="*70)
        
        return "\n".join(summary)
    
    def send_desktop_notification(self, plan):
        """
        Send desktop notification
        
        Args:
            plan: Investment plan dictionary
        """
        if not NOTIFICATIONS_AVAILABLE or not DESKTOP_NOTIFICATIONS:
            return
        
        try:
            title = f"🔔 Investment Reminder - {plan['investment_day']}"
            message = (
                f"Time to invest ₹{plan['total_investment']:,}!\n"
                f"Month {plan['month_number']} | Year {plan['year']}\n"
                f"Phase: {plan['phase']}"
            )
            
            notification.notify(
                title=title,
                message=message,
                app_name="Stock Market Investor",
                timeout=10  # Show for 10 seconds
            )
            
            print(f"{Colors.OKGREEN}✅ Desktop notification sent{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Could not send notification: {e}{Colors.ENDC}")
    
    def send_email_notification(self, plan):
        """
        Send email notification with investment details
        
        Args:
            plan: Investment plan dictionary
        """
        if not EMAIL_ENABLED:
            return
        
        try:
            # Get email password from environment
            email_password = os.getenv('EMAIL_PASSWORD')
            
            if not email_password:
                print(f"{Colors.FAIL}❌ EMAIL_PASSWORD not found in .env file{Colors.ENDC}")
                return
            
            # Prepare recipient list
            recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"🔔 Investment Reminder - {plan['investment_day']}"
            
            # Plain text version
            text_content = self.format_investment_summary(plan)
            
            # HTML version (prettier)
            html_content = self._format_email_html(plan)
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                
                server.login(EMAIL_FROM, email_password)
                server.send_message(msg)
            
            print(f"{Colors.OKGREEN}✅ Email notification sent to: {', '.join(recipients)}{Colors.ENDC}")
        
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error sending email: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}Check your .env file and Gmail App Password{Colors.ENDC}")
    
    def _format_email_html(self, plan):
        """
        Format investment plan as HTML email
        
        Args:
            plan: Investment plan dictionary
        
        Returns:
            str: HTML formatted email
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2E86AB; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .section {{ margin: 20px 0; padding: 15px; background-color: white; border-left: 4px solid #2E86AB; }}
                .section-title {{ color: #2E86AB; font-weight: bold; font-size: 18px; margin-bottom: 10px; }}
                .item {{ margin: 10px 0; padding: 10px; background-color: #f0f8ff; border-radius: 3px; }}
                .ticker {{ font-weight: bold; color: #1565C0; }}
                .amount {{ color: #2E7D32; font-weight: bold; }}
                .note {{ background-color: #FFF9C4; padding: 10px; margin: 5px 0; border-left: 3px solid #F9A825; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Investment Reminder</h1>
                    <h2>{plan['investment_day']}</h2>
                    <p>Hi {INVESTOR_NAME} & Tirth! Time to invest! 💰</p>
                </div>
                
                <div class="content">
                    <p><strong>Month:</strong> {plan['month_number']} | <strong>Year:</strong> {plan['year']} | <strong>Age:</strong> {plan['age']}</p>
                    <p><strong>Phase:</strong> {plan['phase']}</p>
                    <h2 class="amount">Total Investment: ₹{plan['total_investment']:,}</h2>
                    
                    <div class="section">
                        <div class="section-title">💼 Nifty 50 Allocation (₹{plan['nifty50']['total']:,})</div>
                        
                        <div class="item">
                            <strong class="amount">₹{plan['nifty50']['etf']['amount']:,}</strong> → {plan['nifty50']['etf']['name']}<br>
                            <span class="ticker">Ticker: {plan['nifty50']['etf']['ticker']}</span>
                        </div>
        """
        
        # Add stocks
        for stock in plan['nifty50']['stocks']:
            html += f"""
                        <div class="item">
                            <strong class="amount">₹{stock['amount']:,}</strong> → {stock['name']}<br>
                            <span class="ticker">Ticker: {stock['ticker']}</span> | Sector: {stock['sector']}
                        </div>
            """
        
        html += """
                    </div>
                    
                    <div class="section">
                        <div class="section-title">🌈 Diversified Allocation (₹{diversified_total})</div>
        """.format(diversified_total=plan['diversified']['total'])
        
        # Add diversified items
        for category, details in plan['diversified']['breakdown'].items():
            cat_name = category.replace('_', ' ').title()
            html += f"""
                        <div class="item">
                            <strong class="amount">₹{details['amount']:,}</strong> → {cat_name}<br>
                            Instrument: {details['instrument']}
                        </div>
            """
        
        html += """
                    </div>
                    
                    <div class="section">
                        <div class="section-title">🏭 Sectoral Fund Recommendation</div>
                        <p><strong>Sector:</strong> {sector}</p>
                        <p><strong>Recommended:</strong> {funds}</p>
                        <p><strong>Rationale:</strong> {rationale}</p>
                    </div>
        """.format(
            sector=plan['sectoral_fund']['sector'],
            funds=', '.join(plan['sectoral_fund']['recommended_funds']),
            rationale=plan['sectoral_fund']['rationale']
        )
        
        # Add notes
        if plan['notes']:
            html += '<div class="section"><div class="section-title">📝 Notes</div>'
            for note in plan['notes']:
                html += f'<div class="note">{note}</div>'
            html += '</div>'
        
        html += """
                    <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #E3F2FD; border-radius: 5px;">
                        <h3 style="color: #1565C0;">⏰ Remember to invest on the 5th!</h3>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated reminder from Stock Market Investment System</p>
                    <p>Sent to: Neel & Tirth</p>
                    <p>Happy Investing! 📈💰</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def print_reminder(self, plan):
        """
        Print reminder to console with colors
        
        Args:
            plan: Investment plan dictionary
        """
        summary = self.format_investment_summary(plan)
        
        # Print with green color
        print(f"\n{Colors.OKGREEN}{summary}{Colors.ENDC}\n")
    
    def check_and_send_reminder(self):
        """
        Check if reminder should be sent and send it
        
        Returns:
            bool: True if reminder was sent
        """
        if not self.should_send_reminder():
            return False
        
        next_date = self.get_next_investment_date()
        plan = self.get_plan_for_date(next_date)
        
        if not plan:
            print(f"{Colors.WARNING}⚠️  No plan found for next investment date{Colors.ENDC}")
            return False
        
        print(f"\n{Colors.OKBLUE}🔔 SENDING INVESTMENT REMINDER{Colors.ENDC}")
        
        # Print to console
        self.print_reminder(plan)
        
        # Send email notification
        self.send_email_notification(plan)
        
        # Send desktop notification (if available)
        self.send_desktop_notification(plan)
        
        return True
    
    def get_upcoming_reminder_info(self):
        """Display information about next reminder"""
        today = datetime.now()
        next_investment = self.get_next_investment_date()
        days_until = (next_investment - today).days
        
        print(f"\n{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📅 REMINDER SCHEDULE{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}")
        print(f"Next Investment Date: {Colors.BOLD}{next_investment.strftime('%Y-%m-%d')}{Colors.ENDC}")
        print(f"Days Until Investment: {Colors.BOLD}{days_until} days{Colors.ENDC}")
        
        if days_until in REMINDER_DAYS_BEFORE:
            print(f"\n{Colors.OKGREEN}🔔 Reminder will be sent TODAY!{Colors.ENDC}")
        else:
            # Find next reminder day
            for days_before in sorted(REMINDER_DAYS_BEFORE, reverse=True):
                if days_until > days_before:
                    reminder_date = next_investment - timedelta(days=days_before)
                    days_to_reminder = (reminder_date - today).days
                    print(f"\n{Colors.WARNING}🔔 Next Reminder: {reminder_date.strftime('%Y-%m-%d')}{Colors.ENDC}")
                    print(f"   ({days_to_reminder} days from now, {days_before} days before investment)")
                    break
        
        print(f"{Colors.OKCYAN}{'='*70}{Colors.ENDC}\n")
    
    def run_scheduler(self):
        """
        Run scheduled reminder checks
        Checks daily at 9:00 AM for reminders
        """
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}🤖 STARTING AUTOMATED REMINDER SERVICE{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"Checking for reminders daily at 09:00 AM...")
        print(f"{Colors.WARNING}Press Ctrl+C to stop{Colors.ENDC}\n")
        
        # Schedule daily check at 9 AM
        schedule.every().day.at("09:00").do(self.check_and_send_reminder)
        
        # Also check immediately on startup
        print(f"{Colors.OKCYAN}Running initial check...{Colors.ENDC}")
        self.check_and_send_reminder()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}🛑 Reminder service stopped{Colors.ENDC}\n")
    
    def manual_reminder_for_next_month(self):
        """Manually trigger reminder for next investment"""
        next_date = self.get_next_investment_date()
        plan = self.get_plan_for_date(next_date)
        
        if plan:
            print(f"\n{Colors.HEADER}📋 MANUAL REMINDER - NEXT INVESTMENT PLAN{Colors.ENDC}")
            self.print_reminder(plan)
            self.send_desktop_notification(plan)
        else:
            print(f"{Colors.WARNING}⚠️  No plan found for next investment{Colors.ENDC}")


def main():
    """Main reminder service function"""
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}🔔 INVESTMENT REMINDER SERVICE{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
    
    # Initialize service
    service = ReminderService()
    
    # Show upcoming reminder info
    service.get_upcoming_reminder_info()
    
    # Show manual reminder for next investment
    print(f"{Colors.OKCYAN}Displaying next investment plan...{Colors.ENDC}\n")
    service.manual_reminder_for_next_month()
    
    # Ask if user wants to start automated service
    print(f"\n{Colors.WARNING}{'='*70}{Colors.ENDC}")
    print(f"{Colors.WARNING}Would you like to start the automated reminder service?{Colors.ENDC}")
    print(f"{Colors.WARNING}It will check daily at 9:00 AM and send reminders.{Colors.ENDC}")
    print(f"{Colors.WARNING}{'='*70}{Colors.ENDC}")
    
    try:
        response = input(f"\n{Colors.BOLD}Start service? (y/n): {Colors.ENDC}").strip().lower()
        
        if response == 'y':
            service.run_scheduler()
        else:
            print(f"\n{Colors.OKGREEN}Service not started. Run manually anytime with:{Colors.ENDC}")
            print(f"  python reminder_service.py\n")
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Cancelled by user{Colors.ENDC}\n")


if __name__ == "__main__":
    main()

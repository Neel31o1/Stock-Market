"""
Main Application - Stock Market Investment Automation
Interactive menu system to access all features
"""

import os
import sys

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    Colors,
    MONTHLY_INVESTMENT,
    NIFTY50_ALLOCATION,
    DIVERSIFIED_ALLOCATION,
    INVESTMENT_HORIZON,
    INVESTOR_NAME,
    INVESTOR_AGE
)

from investment_planner import InvestmentPlanner
from reminder_service import ReminderService
from chart_generator import ChartGenerator

try:
    from pyspark_analyzer import PySparkAnalyzer
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False


def print_banner():
    """Print application banner"""
    banner = f"""
{Colors.HEADER}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        📈 STOCK MARKET INVESTMENT AUTOMATION SYSTEM 📈               ║
║                                                                      ║
║              Your 20-Year Wealth Building Companion                  ║
║                   Built with PySpark & Python                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}

{Colors.OKCYAN}Investor:{Colors.ENDC} {INVESTOR_NAME} (Age {INVESTOR_AGE})
{Colors.OKCYAN}Investment Strategy:{Colors.ENDC}
  • Total Monthly Investment: {Colors.OKGREEN}₹{MONTHLY_INVESTMENT:,}{Colors.ENDC}
  • Nifty 50 Allocation: {Colors.OKGREEN}₹{NIFTY50_ALLOCATION:,}{Colors.ENDC} (67%)
  • Diversified Allocation: {Colors.OKGREEN}₹{DIVERSIFIED_ALLOCATION:,}{Colors.ENDC} (33%)
  • Investment Horizon: {Colors.OKGREEN}{INVESTMENT_HORIZON} years{Colors.ENDC}
  • Expected Returns: {Colors.OKGREEN}11-14% annually{Colors.ENDC}
    """
    print(banner)


def main_menu():
    """Display main menu"""
    menu = f"""
{Colors.OKBLUE}═══════════════════════════════════════════════════════════════════
                        MAIN MENU
═══════════════════════════════════════════════════════════════════{Colors.ENDC}

1.  📅 Generate 20-Year Investment Plan (240 monthly plans)
2.  🔔 Show Next Month Investment Reminder
3.  📊 Generate Portfolio Charts (4 visualizations)
4.  💹 Run PySpark Analysis (portfolio projections)
5.  📈 Quick Portfolio Projection (all scenarios)
6.  ℹ️  System Information
7.  🚪 Exit

{Colors.WARNING}Enter your choice (1-7): {Colors.ENDC}"""
    
    return input(menu).strip()


def generate_investment_plan():
    """Generate 20-year investment plan"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}📅 GENERATING 20-YEAR INVESTMENT PLAN{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    try:
        planner = InvestmentPlanner()
        plans = planner.generate_20year_plan()
        planner.save_plans_to_file()
        
        # Show sample plans
        print(f"\n{Colors.OKGREEN}Sample Plans:{Colors.ENDC}")
        print(f"\n{Colors.BOLD}--- Month 1 (Start) ---{Colors.ENDC}")
        planner.display_plan_summary(plans[0])
        
        print(f"\n{Colors.BOLD}--- Month 120 (Year 10) ---{Colors.ENDC}")
        planner.display_plan_summary(plans[119])
        
        print(f"\n{Colors.BOLD}--- Month 240 (Year 20 - End) ---{Colors.ENDC}")
        planner.display_plan_summary(plans[239])
        
        print(f"\n{Colors.OKGREEN}✅ All 240 monthly plans generated successfully!{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📂 Saved to: data/monthly_plans.json{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def show_next_reminder():
    """Show next month's investment reminder"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🔔 NEXT MONTH INVESTMENT REMINDER{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    try:
        service = ReminderService()
        service.get_upcoming_reminder_info()
        
        next_date = service.get_next_investment_date()
        plan = service.get_plan_for_date(next_date)
        
        if plan:
            service.print_reminder(plan)
            
            # Ask if user wants to send email
            send_email = input(f"\n{Colors.WARNING}Send email reminder now? (y/n): {Colors.ENDC}").strip().lower()
            if send_email == 'y':
                service.send_email_notification(plan)
        else:
            print(f"{Colors.FAIL}❌ No plan found for next investment{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def generate_charts():
    """Generate all portfolio charts"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}📊 GENERATING PORTFOLIO CHARTS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    try:
        generator = ChartGenerator()
        charts = generator.generate_all_charts()
        
        print(f"\n{Colors.OKGREEN}✅ All charts generated successfully!{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Charts saved in: chart/ folder{Colors.ENDC}")
        print(f"{Colors.OKCYAN}You can view them now or open later.{Colors.ENDC}")
        
        # Ask if user wants to open chart folder
        open_folder = input(f"\n{Colors.WARNING}Open chart folder now? (y/n): {Colors.ENDC}").strip().lower()
        if open_folder == 'y':
            os.system('open chart/ 2>/dev/null || xdg-open chart/ 2>/dev/null || echo "Please open chart/ folder manually"')
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def run_pyspark_analysis():
    """Run PySpark analysis"""
    if not PYSPARK_AVAILABLE:
        print(f"\n{Colors.FAIL}❌ PySpark is not available{Colors.ENDC}")
        print(f"{Colors.WARNING}Install PySpark: pip install pyspark findspark{Colors.ENDC}")
        input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
        return
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}💹 RUNNING PYSPARK ANALYSIS{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    try:
        analyzer = PySparkAnalyzer()
        
        # Generate projections
        df_projections = analyzer.generate_sip_projection(MONTHLY_INVESTMENT, INVESTMENT_HORIZON)
        
        print(f"\n{Colors.OKBLUE}📊 Projection Results:{Colors.ENDC}")
        df_projections.show(truncate=False)
        
        # Generate year-by-year
        df_yearly = analyzer.generate_year_by_year_projection(MONTHLY_INVESTMENT, INVESTMENT_HORIZON)
        
        # Export to CSV
        analyzer.export_analysis_to_csv(df_projections, "sip_projections.csv")
        analyzer.export_yearly_projection_to_csv(df_yearly, "yearly_projection.csv")
        
        print(f"\n{Colors.OKGREEN}✅ Analysis complete!{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📂 Results saved to data/ folder{Colors.ENDC}")
        
        analyzer.stop_spark()
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def quick_projection():
    """Show quick portfolio projection"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}📈 QUICK PORTFOLIO PROJECTION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    from config import EXPECTED_RETURNS
    
    years = [5, 10, 15, 20]
    
    print(f"\n{Colors.OKCYAN}Monthly Investment: ₹{MONTHLY_INVESTMENT:,}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Investment Horizon: {INVESTMENT_HORIZON} years{Colors.ENDC}")
    print(f"\n{'='*80}")
    
    for scenario_name, annual_rate in EXPECTED_RETURNS.items():
        print(f"\n{Colors.BOLD}{scenario_name.upper()} SCENARIO ({annual_rate*100}% annual):{Colors.ENDC}")
        print("-" * 80)
        
        for year in years:
            months = year * 12
            total_invested = MONTHLY_INVESTMENT * months
            
            monthly_rate = annual_rate / 12
            fv = MONTHLY_INVESTMENT * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            
            returns = fv - total_invested
            return_pct = (returns / total_invested) * 100
            
            print(f"Year {year:2d}: Invested {Colors.OKCYAN}₹{total_invested/100000:5.1f}L{Colors.ENDC} " +
                  f"→ Value {Colors.OKGREEN}₹{fv/100000:6.1f}L{Colors.ENDC} " +
                  f"(↑{return_pct:5.1f}%)")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def show_system_info():
    """Show system information"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}ℹ️  SYSTEM INFORMATION{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    import sys
    
    print(f"\n{Colors.OKBLUE}System Details:{Colors.ENDC}")
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Working Directory: {os.getcwd()}")
    
    # Check installed packages
    print(f"\n{Colors.OKBLUE}Installed Packages:{Colors.ENDC}")
    
    try:
        import pyspark
        print(f"  ✅ PySpark: {pyspark.__version__}")
    except ImportError:
        print(f"  ❌ PySpark: Not installed")
    
    try:
        import pandas
        print(f"  ✅ Pandas: {pandas.__version__}")
    except ImportError:
        print(f"  ❌ Pandas: Not installed")
    
    try:
        import yfinance
        print(f"  ✅ yfinance: Available")
    except ImportError:
        print(f"  ❌ yfinance: Not installed")
    
    try:
        import matplotlib
        print(f"  ✅ Matplotlib: {matplotlib.__version__}")
    except ImportError:
        print(f"  ❌ Matplotlib: Not installed")
    
    try:
        from dotenv import load_dotenv
        print(f"  ✅ python-dotenv: Available")
    except ImportError:
        print(f"  ❌ python-dotenv: Not installed")
    
    # Check data files
    print(f"\n{Colors.OKBLUE}Data Files:{Colors.ENDC}")
    data_files = ['monthly_plans.json', 'portfolio.csv', 'transactions.csv', 
                  'sip_projections.csv', 'yearly_projection.csv']
    for file in data_files:
        path = os.path.join('..', 'data', file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Check charts
    print(f"\n{Colors.OKBLUE}Generated Charts:{Colors.ENDC}")
    chart_dir = os.path.join('..', 'chart')
    if os.path.exists(chart_dir):
        charts = [f for f in os.listdir(chart_dir) if f.endswith('.png')]
        print(f"  Total: {len(charts)} chart(s)")
        for chart in charts:
            print(f"    • {chart}")
    else:
        print(f"  ⚠️  No charts generated yet")
    
    # Investment configuration
    print(f"\n{Colors.OKBLUE}Investment Configuration:{Colors.ENDC}")
    print(f"  Investor: {INVESTOR_NAME}")
    print(f"  Age: {INVESTOR_AGE}")
    print(f"  Monthly Investment: ₹{MONTHLY_INVESTMENT:,}")
    print(f"  Investment Horizon: {INVESTMENT_HORIZON} years")
    print(f"  Total Investment: ₹{MONTHLY_INVESTMENT * INVESTMENT_HORIZON * 12:,}")
    
    input(f"\n{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


def main():
    """Main application loop"""
    
    # Clear screen (platform independent)
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print_banner()
    
    while True:
        try:
            choice = main_menu()
            
            if choice == '1':
                generate_investment_plan()
            elif choice == '2':
                show_next_reminder()
            elif choice == '3':
                generate_charts()
            elif choice == '4':
                run_pyspark_analysis()
            elif choice == '5':
                quick_projection()
            elif choice == '6':
                show_system_info()
            elif choice == '7':
                print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
                print(f"{Colors.OKGREEN}👋 Thank you for using Stock Market Investment Automation!{Colors.ENDC}")
                print(f"{Colors.OKGREEN}📈 Happy Investing! 🚀{Colors.ENDC}")
                print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}\n")
                break
            else:
                print(f"\n{Colors.FAIL}❌ Invalid choice. Please enter 1-7.{Colors.ENDC}")
                input(f"{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}⚠️  Interrupted by user{Colors.ENDC}")
            print(f"{Colors.OKGREEN}👋 Goodbye!{Colors.ENDC}\n")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            input(f"{Colors.WARNING}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    main()

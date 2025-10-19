"""
Investment Planner - Generates 20-year monthly investment plans
Uses intelligent stock rotation and phase-wise allocation strategy
"""

import json
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

try:
    import findspark
    findspark.init()
    from pyspark.sql import SparkSession
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    print("⚠️  PySpark not available. Using pandas fallback.")

from config import (
    MONTHLY_INVESTMENT,
    NIFTY50_ALLOCATION,
    DIVERSIFIED_ALLOCATION,
    START_DATE,
    INVESTMENT_DAY,
    NIFTY50_STOCKS,
    CORE_ETF,
    MID_CAP_ETF,
    GOLD_ETF,
    MONTHLY_PLANS_FILE,
    INVESTMENT_HORIZON,
    Colors
)


class InvestmentPlanner:
    """
    Generates and manages 20-year monthly investment plans
    
    Features:
    - Automatic stock rotation across 12 Nifty 50 stocks
    - Phase-wise allocation strategy
    - Sectoral fund rotation
    - JSON persistence
    """
    
    def __init__(self):
        """Initialize the investment planner"""
        self.start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
        self.plans = []
        
        # Initialize PySpark if available
        if PYSPARK_AVAILABLE:
            try:
                self.spark = SparkSession.builder \
                    .appName("Investment Planner") \
                    .master("local[*]") \
                    .getOrCreate()
                print(f"{Colors.OKGREEN}✅ PySpark session initialized{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.WARNING}⚠️  PySpark session failed: {e}{Colors.ENDC}")
                self.spark = None
        else:
            self.spark = None
    
    def generate_20year_plan(self):
        """
        Generate complete 20-year monthly investment plan
        
        Returns:
            list: List of 240 monthly investment plans
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}📅 GENERATING 20-YEAR MONTHLY INVESTMENT PLAN{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        total_months = INVESTMENT_HORIZON * 12
        current_date = self.start_date
        
        for month_num in range(1, total_months + 1):
            year_num = ((month_num - 1) // 12) + 1
            
            # Generate plan for this month
            plan = self._generate_monthly_plan(current_date, month_num, year_num)
            self.plans.append(plan)
            
            # Move to next month
            current_date = current_date + relativedelta(months=1)
            
            # Progress indicator every year
            if month_num % 12 == 0:
                print(f"  {Colors.OKGREEN}✓ Year {year_num} planned ({month_num} months){Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✅ Generated {len(self.plans)} monthly investment plans{Colors.ENDC}")
        return self.plans
    
    def _generate_monthly_plan(self, date, month_num, year_num):
        """
        Generate investment plan for a single month
        
        Args:
            date: Investment date
            month_num: Month number (1-240)
            year_num: Year number (1-20)
        
        Returns:
            dict: Monthly investment plan
        """
        # Determine current investment phase
        phase = self._get_investment_phase(year_num)
        
        # Calculate investor age
        age = 26 + year_num - 1
        
        # Generate Nifty 50 allocation
        nifty_plan = self._plan_nifty50_allocation(month_num)
        
        # Generate diversified allocation
        diversified_plan = self._plan_diversified_allocation(year_num, phase)
        
        # Get sectoral fund recommendation
        sectoral = self._get_sectoral_fund(year_num)
        
        # Create the plan
        plan = {
            "month_number": month_num,
            "year": year_num,
            "date": date.strftime("%Y-%m-%d"),
            "investment_day": date.replace(day=INVESTMENT_DAY).strftime("%Y-%m-%d"),
            "age": age,
            "phase": phase,
            "total_investment": MONTHLY_INVESTMENT,
            "nifty50": {
                "total": NIFTY50_ALLOCATION,
                "etf": nifty_plan["etf"],
                "stocks": nifty_plan["stocks"]
            },
            "diversified": {
                "total": DIVERSIFIED_ALLOCATION,
                "breakdown": diversified_plan
            },
            "sectoral_fund": sectoral,
            "notes": self._generate_notes(year_num, month_num)
        }
        
        return plan
    
    def _get_investment_phase(self, year_num):
        """
        Determine investment phase based on year
        
        Phases:
        - Years 1-5: Foundation Building (Conservative)
        - Years 6-10: Growth Acceleration (Moderate-High)
        - Years 11-15: Wealth Accumulation (Balanced)
        - Years 16-20: Consolidation (Risk Reduction)
        """
        if 1 <= year_num <= 5:
            return "Phase 1: Foundation Building"
        elif 6 <= year_num <= 10:
            return "Phase 2: Growth Acceleration"
        elif 11 <= year_num <= 15:
            return "Phase 3: Wealth Accumulation"
        else:
            return "Phase 4: Consolidation"
    
    def _plan_nifty50_allocation(self, month_num):
        """
        Plan Nifty 50 stock allocation for the month
        Uses rotation strategy to ensure diversification
        
        Args:
            month_num: Current month number (1-240)
        
        Returns:
            dict: Nifty 50 allocation with ETF and stocks
        """
        # ETF allocation (always ₹5,000)
        etf_allocation = {
            "ticker": CORE_ETF["ticker"],
            "name": CORE_ETF["name"],
            "amount": CORE_ETF["allocation"]
        }
        
        # Stock rotation algorithm
        # Month 1: Reliance + TCS
        # Month 2: TCS + HDFC Bank
        # Month 3: HDFC Bank + Infosys
        # ... and so on (rotates through all 12 stocks)
        
        stock_index = (month_num - 1) % len(NIFTY50_STOCKS)
        stock2_index = month_num % len(NIFTY50_STOCKS)
        
        primary_stock = NIFTY50_STOCKS[stock_index]
        secondary_stock = NIFTY50_STOCKS[stock2_index]
        
        stocks = [
            {
                "ticker": primary_stock["ticker"],
                "name": primary_stock["name"],
                "sector": primary_stock["sector"],
                "amount": 3000,
                "priority": "primary"
            },
            {
                "ticker": secondary_stock["ticker"],
                "name": secondary_stock["name"],
                "sector": secondary_stock["sector"],
                "amount": 2000,
                "priority": "secondary"
            }
        ]
        
        return {
            "etf": etf_allocation,
            "stocks": stocks
        }
    
    def _plan_diversified_allocation(self, year_num, phase):
        """
        Plan diversified allocation based on investment phase
        
        Strategy evolves over 30 years (extended timeline)
        """
        
        allocation = {}
        
        if 1 <= year_num <= 10:
            # Phase 1 (Age 26-36): Aggressive Growth
            allocation = {
                "mid_cap": {
                    "amount": 3500,
                    "instrument": MID_CAP_ETF["ticker"],
                    "name": MID_CAP_ETF["name"]
                },
                "small_cap": {
                    "amount": 1500,
                    "instrument": "Nifty Small Cap 250 Index Fund"
                },
                "sectoral": {
                    "amount": 1500,
                    "instrument": "Sectoral Fund (see recommendation)"
                },
                "international": {
                    "amount": 500,
                    "instrument": "Nasdaq 100 / Global Equity"
                }
            }
        elif 11 <= year_num <= 20:
            # Phase 2 (Age 36-46): Balanced Growth
            allocation = {
                "mid_cap": {
                    "amount": 3000,
                    "instrument": MID_CAP_ETF["ticker"],
                    "name": MID_CAP_ETF["name"]
                },
                "small_cap": {
                    "amount": 1000,
                    "instrument": "Nifty Small Cap 250 Index Fund"
                },
                "international": {
                    "amount": 1500,
                    "instrument": "Global Equity Fund"
                },
                "sectoral": {
                    "amount": 500,
                    "instrument": "Sectoral Fund (see recommendation)"
                }
            }
        elif 21 <= year_num <= 25:
            # Phase 3 (Age 46-51): Consolidation
            allocation = {
                "mid_cap": {
                    "amount": 2000,
                    "instrument": MID_CAP_ETF["ticker"],
                    "name": MID_CAP_ETF["name"]
                },
                "balanced": {
                    "amount": 2000,
                    "instrument": "Balanced Advantage Fund"
                },
                "international": {
                    "amount": 1500,
                    "instrument": "Global Equity Fund"
                },
                "debt": {
                    "amount": 500,
                    "instrument": "Liquid/Debt Fund"
                }
            }
        else:  # 26-30
            # Phase 4 (Age 51-56): Capital Preservation
            allocation = {
                "balanced": {
                    "amount": 2500,
                    "instrument": "Balanced Advantage Fund"
                },
                "debt": {
                    "amount": 2000,
                    "instrument": "Corporate Bond Fund"
                },
                "international": {
                    "amount": 500,
                    "instrument": "Global Equity Fund"
                }
            }
        
        return allocation

    
    def _get_sectoral_fund(self, year_num):
        """
        Get recommended sectoral fund based on economic cycle
        
        Rotation strategy:
        - Years 1-3: IT/Technology (Global tech boom)
        - Years 4-6: Pharma/Healthcare (Healthcare demand)
        - Years 7-9: Banking/Finance (Credit growth)
        - Years 10-12: Infrastructure (Government capex)
        - Years 13-15: Consumption/FMCG (Rising incomes)
        - Years 16-20: Balanced/Hybrid (Risk reduction)
        """
        sectoral_rotation = {
            (1, 3): {
                "sector": "IT/Technology",
                "recommended_funds": ["ICICI Pru Technology Fund", "SBI Technology Fund"],
                "rationale": "Global outsourcing, AI/Cloud growth"
            },
            (4, 6): {
                "sector": "Pharma/Healthcare",
                "recommended_funds": ["Nippon India Pharma Fund", "SBI Healthcare Fund"],
                "rationale": "Aging population, healthcare demand"
            },
            (7, 9): {
                "sector": "Banking/Finance",
                "recommended_funds": ["SBI Banking & Finance Fund", "ICICI Pru Banking Fund"],
                "rationale": "Credit expansion, NPA reduction"
            },
            (10, 12): {
                "sector": "Infrastructure",
                "recommended_funds": ["ICICI Pru Infrastructure Fund", "L&T Infrastructure Fund"],
                "rationale": "Government spending, PLI schemes"
            },
            (13, 15): {
                "sector": "Consumption/FMCG",
                "recommended_funds": ["ICICI Pru FMCG Fund", "Nippon India Consumer Fund"],
                "rationale": "Rising incomes, urban growth"
            },
            (16, 20): {
                "sector": "Balanced/Hybrid",
                "recommended_funds": ["Balanced Advantage Fund", "Dynamic Asset Allocation"],
                "rationale": "Risk reduction, capital protection"
            }
        }
        
        for year_range, sector_info in sectoral_rotation.items():
            if year_range[0] <= year_num <= year_range[1]:
                return sector_info
        
        return {
            "sector": "Balanced",
            "recommended_funds": ["Balanced Advantage Fund"],
            "rationale": "Capital protection"
        }
    
    def _generate_notes(self, year_num, month_num):
        """Generate helpful notes and reminders"""
        notes = []
        
        if month_num == 1:
            notes.append("🎯 Welcome! Start of your 20-year investment journey!")
            notes.append("💡 Tip: Set up automatic reminders for investment day")
        
        if month_num % 12 == 1:
            notes.append(f"📅 Year {year_num} begins - Review annual strategy")
        
        if month_num % 60 == 0:
            notes.append("⚖️  5-year milestone reached - Time for portfolio rebalancing")
        
        if year_num in [6, 11, 16]:
            notes.append("🔄 Phase transition - Adjust allocation strategy")
        
        if month_num == 240:
            notes.append("🎉 Congratulations! Final investment - You've reached 20 years!")
        
        return notes
    
    def save_plans_to_file(self):
        """Save all plans to JSON file"""
        try:
            with open(MONTHLY_PLANS_FILE, 'w') as f:
                json.dump(self.plans, f, indent=2)
            
            print(f"\n{Colors.OKGREEN}💾 Saved {len(self.plans)} monthly plans to:{Colors.ENDC}")
            print(f"   {MONTHLY_PLANS_FILE}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error saving plans: {e}{Colors.ENDC}")
    
    def get_next_investment_plan(self):
        """Get next upcoming investment plan"""
        today = datetime.now()
        
        for plan in self.plans:
            plan_date = datetime.strptime(plan["investment_day"], "%Y-%m-%d")
            if plan_date >= today:
                return plan
        
        return None
    
    def display_plan_summary(self, plan):
        """Display a formatted summary of an investment plan"""
        if not plan:
            print(f"{Colors.WARNING}⚠️  No plan available{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}📊 INVESTMENT PLAN - {plan['investment_day']}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"Month: {plan['month_number']} | Year: {plan['year']} | Age: {plan['age']}")
        print(f"Phase: {Colors.OKCYAN}{plan['phase']}{Colors.ENDC}")
        print(f"Total Investment: {Colors.OKGREEN}₹{plan['total_investment']:,}{Colors.ENDC}")
        
        # Nifty 50 section
        print(f"\n{Colors.OKBLUE}💼 NIFTY 50 ALLOCATION (₹{plan['nifty50']['total']:,}){Colors.ENDC}")
        print("-" * 80)
        
        etf = plan['nifty50']['etf']
        print(f"  ✓ ₹{etf['amount']:,} → {etf['name']}")
        print(f"    Ticker: {Colors.BOLD}{etf['ticker']}{Colors.ENDC}")
        
        for stock in plan['nifty50']['stocks']:
            print(f"  ✓ ₹{stock['amount']:,} → {stock['name']}")
            print(f"    Ticker: {Colors.BOLD}{stock['ticker']}{Colors.ENDC} | Sector: {stock['sector']}")
        
        # Diversified section
        print(f"\n{Colors.OKBLUE}🌈 DIVERSIFIED ALLOCATION (₹{plan['diversified']['total']:,}){Colors.ENDC}")
        print("-" * 80)
        
        for category, details in plan['diversified']['breakdown'].items():
            cat_name = category.replace('_', ' ').title()
            print(f"  ✓ ₹{details['amount']:,} → {cat_name}")
            print(f"    Instrument: {details['instrument']}")
        
        # Sectoral recommendation
        print(f"\n{Colors.OKBLUE}🏭 SECTORAL FUND RECOMMENDATION{Colors.ENDC}")
        print("-" * 80)
        sectoral = plan['sectoral_fund']
        print(f"  Sector: {Colors.BOLD}{sectoral['sector']}{Colors.ENDC}")
        print(f"  Recommended: {', '.join(sectoral['recommended_funds'])}")
        print(f"  Rationale: {sectoral['rationale']}")
        
        # Notes
        if plan['notes']:
            print(f"\n{Colors.WARNING}📝 NOTES:{Colors.ENDC}")
            for note in plan['notes']:
                print(f"  {note}")
        
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")


def main():
    """Main function to run investment planner"""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 STOCK MARKET INVESTMENT PLANNER{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
    
    # Create planner instance
    planner = InvestmentPlanner()
    
    # Generate 20-year plan
    plans = planner.generate_20year_plan()
    
    # Save to file
    planner.save_plans_to_file()
    
    # Display next month's plan
    print(f"\n{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}📅 YOUR NEXT INVESTMENT PLAN{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    
    next_plan = planner.get_next_investment_plan()
    if next_plan:
        planner.display_plan_summary(next_plan)
    else:
        print(f"{Colors.WARNING}⚠️  All investment dates are in the past{Colors.ENDC}")
    
    return planner


if __name__ == "__main__":
    main()
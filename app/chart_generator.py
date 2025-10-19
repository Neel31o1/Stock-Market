"""
Chart Generator - Create portfolio visualization charts
Saves charts to chart/ folder
"""

import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

from config import (
    CHART_DIR,
    EXPECTED_RETURNS,
    MONTHLY_INVESTMENT,
    INVESTMENT_HORIZON,
    Colors
)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


class ChartGenerator:
    """Generate and save portfolio charts"""
    
    def __init__(self):
        """Initialize chart generator"""
        # Create chart directory if it doesn't exist
        os.makedirs(CHART_DIR, exist_ok=True)
        print(f"{Colors.OKGREEN}✅ Chart directory ready: {CHART_DIR}{Colors.ENDC}")
    
    def generate_20year_projection_chart(self):
        """
        Generate 20-year portfolio growth projection chart
        
        Returns:
            str: Path to saved chart
        """
        print(f"\n{Colors.OKCYAN}📊 Generating 20-year projection chart...{Colors.ENDC}")
        
        # Calculate projections
        years = list(range(1, INVESTMENT_HORIZON + 1))
        data = {
            'Year': years,
            'Total Invested': [],
            'Conservative (11%)': [],
            'Moderate (12%)': [],
            'Optimistic (14%)': [],
        }
        
        for year in years:
            months = year * 12
            total_invested = MONTHLY_INVESTMENT * months
            data['Total Invested'].append(total_invested / 100000)  # in lakhs
            
            # Calculate FV for each scenario
            for scenario_name, annual_rate in EXPECTED_RETURNS.items():
                monthly_rate = annual_rate / 12
                fv = MONTHLY_INVESTMENT * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
                
                if scenario_name == 'conservative':
                    data['Conservative (11%)'].append(fv / 100000)
                elif scenario_name == 'moderate':
                    data['Moderate (12%)'].append(fv / 100000)
                elif scenario_name == 'optimistic':
                    data['Optimistic (14%)'].append(fv / 100000)
        
        df = pd.DataFrame(data)
        
        # Create chart
        fig, ax = plt.subplots(figsize=(16, 9))
        
        ax.plot(df['Year'], df['Conservative (11%)'], marker='o', linewidth=2.5, 
                label='Conservative (11%)', color='#3498db', markersize=6)
        ax.plot(df['Year'], df['Moderate (12%)'], marker='s', linewidth=2.5, 
                label='Moderate (12%)', color='#2ecc71', markersize=6)
        ax.plot(df['Year'], df['Optimistic (14%)'], marker='^', linewidth=2.5, 
                label='Optimistic (14%)', color='#e74c3c', markersize=6)
        ax.plot(df['Year'], df['Total Invested'], linestyle='--', linewidth=2, 
                label='Total Invested', color='#95a5a6', alpha=0.7)
        
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Portfolio Value (₹ Lakhs)', fontsize=14, fontweight='bold')
        ax.set_title('20-Year Portfolio Growth Projection (₹15,000/month SIP)', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Add annotations for key milestones
        for year_mark in [5, 10, 15, 20]:
            idx = year_mark - 1
            moderate_value = df.loc[idx, 'Moderate (12%)']
            ax.annotate(f'₹{moderate_value:.1f}L', 
                       xy=(year_mark, moderate_value),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        
        filename = os.path.join(CHART_DIR, 'portfolio_growth_projection.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✅ Saved: {filename}{Colors.ENDC}")
        
        return filename
    
    def generate_monthly_breakdown_chart(self):
        """
        Generate pie chart showing monthly investment breakdown
        
        Returns:
            str: Path to saved chart
        """
        print(f"\n{Colors.OKCYAN}📊 Generating monthly breakdown chart...{Colors.ENDC}")
        
        labels = ['NIFTYBEES ETF\n(₹5,000)', 'Nifty Stocks\n(₹5,000)', 
                  'Mid-Cap ETF\n(₹2,000)', 'Sectoral Fund\n(₹1,500)',
                  'International\n(₹1,000)', 'Gold\n(₹500)']
        
        sizes = [5000, 5000, 2000, 1500, 1000, 500]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#f1c40f']
        explode = (0.05, 0.05, 0, 0, 0, 0)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, explode=explode,
                                          textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        # Make percentage text more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        ax.set_title('Monthly Investment Allocation (₹15,000)', 
                    fontsize=18, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        filename = os.path.join(CHART_DIR, 'monthly_breakdown.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✅ Saved: {filename}{Colors.ENDC}")
        
        return filename
    
    def generate_allocation_evolution_chart(self):
        """
        Generate chart showing portfolio allocation evolution over 20 years
        
        Returns:
            str: Path to saved chart
        """
        print(f"\n{Colors.OKCYAN}📊 Generating allocation evolution chart...{Colors.ENDC}")
        
        # Define allocation by phase
        phases = ['Years 1-5\nFoundation', 'Years 6-10\nGrowth', 
                  'Years 11-15\nAccumulation', 'Years 16-20\nConsolidation']
        
        allocations = {
            'Nifty 50 ETF': [35, 30, 35, 40],
            'Nifty 50 Stocks': [30, 25, 20, 15],
            'Mid-Cap': [20, 20, 15, 10],
            'Sectoral': [10, 12, 10, 0],
            'International': [0, 8, 10, 10],
            'Dividend': [0, 0, 7, 10],
            'Debt/Hybrid': [0, 0, 0, 10],
            'Gold': [5, 5, 3, 5],
        }
        
        df = pd.DataFrame(allocations, index=phases)
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
                  '#9b59b6', '#1abc9c', '#34495e', '#f1c40f']
        
        df.plot(kind='bar', stacked=True, ax=ax, color=colors, width=0.7)
        
        ax.set_xlabel('Investment Phase', fontsize=14, fontweight='bold')
        ax.set_ylabel('Allocation (%)', fontsize=14, fontweight='bold')
        ax.set_title('Portfolio Allocation Strategy Evolution (20 Years)', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=11)
        ax.set_xticklabels(phases, rotation=0, ha='center')
        ax.set_ylim(0, 100)
        
        # Add grid
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        filename = os.path.join(CHART_DIR, 'allocation_evolution.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✅ Saved: {filename}{Colors.ENDC}")
        
        return filename
    
    def generate_compound_interest_chart(self):
        """
        Visualize the power of compounding
        
        Returns:
            str: Path to saved chart
        """
        print(f"\n{Colors.OKCYAN}📊 Generating compound interest visualization...{Colors.ENDC}")
        
        years = list(range(1, 21))
        invested_data = []
        moderate_data = []
        
        for year in years:
            months = year * 12
            invested = MONTHLY_INVESTMENT * months
            invested_data.append(invested / 100000)
            
            # Moderate returns
            monthly_rate = EXPECTED_RETURNS['moderate'] / 12
            fv = MONTHLY_INVESTMENT * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            moderate_data.append(fv / 100000)
        
        # Calculate interest earned (returns)
        interest_data = [moderate_data[i] - invested_data[i] for i in range(len(years))]
        
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Stacked area chart
        ax.fill_between(years, 0, invested_data, alpha=0.6, label='Principal Invested', color='#3498db')
        ax.fill_between(years, invested_data, moderate_data, alpha=0.6, label='Returns (Compounding)', color='#2ecc71')
        
        ax.set_xlabel('Year', fontsize=14, fontweight='bold')
        ax.set_ylabel('Amount (₹ Lakhs)', fontsize=14, fontweight='bold')
        ax.set_title('The Power of Compounding: Principal vs Returns (12% Annual)', 
                    fontsize=18, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=13, framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Add annotations
        for year_mark in [5, 10, 15, 20]:
            idx = year_mark - 1
            total = moderate_data[idx]
            principal = invested_data[idx]
            returns = interest_data[idx]
            
            ax.annotate(f'Total: ₹{total:.1f}L\nReturns: ₹{returns:.1f}L', 
                       xy=(year_mark, total),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        
        filename = os.path.join(CHART_DIR, 'compounding_power.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"{Colors.OKGREEN}✅ Saved: {filename}{Colors.ENDC}")
        
        return filename
    
    def generate_all_charts(self):
        """
        Generate all portfolio charts
        
        Returns:
            list: List of saved chart filenames
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}🎨 GENERATING ALL PORTFOLIO CHARTS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        charts = []
        
        charts.append(self.generate_20year_projection_chart())
        charts.append(self.generate_monthly_breakdown_chart())
        charts.append(self.generate_allocation_evolution_chart())
        charts.append(self.generate_compound_interest_chart())
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ Generated {len(charts)} charts in {CHART_DIR}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        for chart in charts:
            print(f"  • {os.path.basename(chart)}")
        
        return charts


def main():
    """Generate all charts"""
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🎨 STOCK MARKET CHART GENERATOR{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    generator = ChartGenerator()
    charts = generator.generate_all_charts()
    
    print(f"\n{Colors.OKGREEN}🎉 All charts generated successfully!{Colors.ENDC}")
    print(f"{Colors.OKCYAN}📂 Open the 'chart/' folder to view your charts{Colors.ENDC}\n")


if __name__ == "__main__":
    main()


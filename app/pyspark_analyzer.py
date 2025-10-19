"""
PySpark Analyzer - Advanced portfolio analysis using PySpark
Handles large-scale data processing and complex calculations
"""

import os
import pandas as pd
from datetime import datetime

try:
    import findspark
    findspark.init()
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        col, avg, sum as spark_sum, stddev, max as spark_max, 
        min as spark_min, count, lag, when, lit, expr
    )
    from pyspark.sql.window import Window
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    print("⚠️  PySpark not available. Some features will be limited.")

from config import (
    SPARK_APP_NAME,
    SPARK_MASTER,
    SPARK_MEMORY,
    EXPECTED_RETURNS,
    MONTHLY_INVESTMENT,
    INVESTMENT_HORIZON,
    Colors,
    DATA_DIR
)


class PySparkAnalyzer:
    """Advanced portfolio analysis using PySpark"""
    
    def __init__(self):
        """Initialize PySpark analyzer"""
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark is not available. Install: pip install pyspark findspark")
        
        try:
            self.spark = SparkSession.builder \
                .appName(SPARK_APP_NAME) \
                .master(SPARK_MASTER) \
                .config("spark.driver.memory", SPARK_MEMORY) \
                .config("spark.sql.shuffle.partitions", "4") \
                .getOrCreate()
            
            print(f"{Colors.OKGREEN}✅ PySpark session initialized: {SPARK_APP_NAME}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to initialize PySpark: {e}{Colors.ENDC}")
            raise
    
    def load_portfolio_data(self, portfolio_file):
        """
        Load portfolio data into Spark DataFrame
        
        Args:
            portfolio_file: Path to portfolio CSV file
        
        Returns:
            Spark DataFrame or None
        """
        try:
            if not os.path.exists(portfolio_file):
                print(f"{Colors.WARNING}⚠️  Portfolio file not found: {portfolio_file}{Colors.ENDC}")
                return None
            
            df_spark = self.spark.read.csv(portfolio_file, header=True, inferSchema=True)
            print(f"{Colors.OKGREEN}📥 Loaded {df_spark.count()} records from portfolio{Colors.ENDC}")
            return df_spark
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error loading portfolio data: {e}{Colors.ENDC}")
            return None
    
    def load_transactions(self, transactions_file):
        """
        Load transaction history into Spark DataFrame
        
        Args:
            transactions_file: Path to transactions CSV file
        
        Returns:
            Spark DataFrame or None
        """
        try:
            if not os.path.exists(transactions_file):
                print(f"{Colors.WARNING}⚠️  Transactions file not found: {transactions_file}{Colors.ENDC}")
                return None
            
            df = self.spark.read.csv(transactions_file, header=True, inferSchema=True)
            print(f"{Colors.OKGREEN}📥 Loaded {df.count()} transactions{Colors.ENDC}")
            return df
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error loading transactions: {e}{Colors.ENDC}")
            return None
    
    def calculate_portfolio_metrics(self, df_transactions):
        """
        Calculate comprehensive portfolio metrics using PySpark
        
        Args:
            df_transactions: Spark DataFrame of transactions
        
        Returns:
            dict: Portfolio metrics
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}📊 CALCULATING PORTFOLIO METRICS WITH PYSPARK{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        if df_transactions is None or df_transactions.count() == 0:
            print(f"{Colors.WARNING}⚠️  No transaction data available{Colors.ENDC}")
            return None
        
        # Calculate total investment
        total_invested = df_transactions.agg(spark_sum("Total_Investment")).collect()[0][0]
        
        # Calculate metrics
        metrics = {
            "total_invested": total_invested if total_invested else 0,
            "number_of_transactions": df_transactions.count(),
            "unique_holdings": df_transactions.select("Ticker").distinct().count(),
        }
        
        print(f"\n{Colors.OKGREEN}💰 Total Invested: ₹{metrics['total_invested']:,.2f}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}📝 Number of Transactions: {metrics['number_of_transactions']}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}🎯 Unique Holdings: {metrics['unique_holdings']}{Colors.ENDC}")
        
        return metrics
    
    def project_future_value(self, monthly_investment, months, annual_return):
        """
        Project future portfolio value using compound interest
        
        Args:
            monthly_investment: Amount invested per month
            months: Number of months
            annual_return: Annual return rate (e.g., 0.12 for 12%)
        
        Returns:
            dict: Projection results
        """
        monthly_return = annual_return / 12
        
        # Generate month sequence
        month_data = [(i, float(monthly_investment)) for i in range(1, months + 1)]
        
        schema = StructType([
            StructField("month", IntegerType(), False),
            StructField("investment", DoubleType(), False)
        ])
        
        df_projection = self.spark.createDataFrame(month_data, schema)
        
        # Calculate future value for each month's investment
        # FV = P * (1 + r)^n
        df_projection = df_projection \
            .withColumn("months_remaining", lit(months) - col("month")) \
            .withColumn("future_value", 
                       col("investment") * expr(f"power(1 + {monthly_return}, months_remaining)"))
        
        # Sum all future values
        total_fv = df_projection.agg(spark_sum("future_value")).collect()[0][0]
        total_invested = df_projection.agg(spark_sum("investment")).collect()[0][0]
        
        return {
            "total_invested": total_invested,
            "future_value": total_fv,
            "total_returns": total_fv - total_invested,
            "return_percentage": ((total_fv - total_invested) / total_invested) * 100
        }
    
    def generate_sip_projection(self, monthly_amount, years):
        """
        Generate SIP projection for multiple scenarios
        
        Args:
            monthly_amount: Monthly investment amount
            years: Investment period in years
        
        Returns:
            Spark DataFrame with projections
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}📈 SIP PROJECTION ANALYSIS (PYSPARK){Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        months = years * 12
        scenarios = []
        
        for scenario_name, annual_rate in EXPECTED_RETURNS.items():
            projection = self.project_future_value(monthly_amount, months, annual_rate)
            
            scenarios.append({
                "scenario": scenario_name.title(),
                "annual_return": f"{annual_rate * 100}%",
                "total_invested": projection["total_invested"],
                "future_value": projection["future_value"],
                "returns": projection["total_returns"],
                "return_pct": projection["return_percentage"]
            })
            
            print(f"\n{Colors.OKCYAN}{scenario_name.upper()} ({annual_rate*100}% annual):{Colors.ENDC}")
            print(f"  Invested: {Colors.OKGREEN}₹{projection['total_invested']:,.0f}{Colors.ENDC}")
            print(f"  Future Value: {Colors.OKGREEN}₹{projection['future_value']:,.0f}{Colors.ENDC}")
            print(f"  Returns: {Colors.OKGREEN}₹{projection['total_returns']:,.0f}{Colors.ENDC} ({Colors.BOLD}{projection['return_percentage']:.1f}%{Colors.ENDC})")
        
        # Create Spark DataFrame
        schema = StructType([
            StructField("scenario", StringType(), False),
            StructField("annual_return", StringType(), False),
            StructField("total_invested", DoubleType(), False),
            StructField("future_value", DoubleType(), False),
            StructField("returns", DoubleType(), False),
            StructField("return_pct", DoubleType(), False)
        ])
        
        df_scenarios = self.spark.createDataFrame(scenarios, schema)
        
        return df_scenarios
    
    def generate_year_by_year_projection(self, monthly_amount, years):
        """
        Generate year-by-year portfolio value projection
        
        Args:
            monthly_amount: Monthly investment
            years: Number of years
        
        Returns:
            Pandas DataFrame with year-by-year projections
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}📊 YEAR-BY-YEAR PORTFOLIO PROJECTION{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        projection_data = []
        
        for year in range(1, years + 1):
            months = year * 12
            total_invested = monthly_amount * months
            
            year_data = {
                'Year': year,
                'Age': 26 + year - 1,
                'Total Invested': total_invested
            }
            
            # Calculate for each scenario
            for scenario_name, annual_rate in EXPECTED_RETURNS.items():
                monthly_rate = annual_rate / 12
                fv = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
                year_data[f'{scenario_name.title()} ({int(annual_rate*100)}%)'] = fv
            
            projection_data.append(year_data)
        
        df = pd.DataFrame(projection_data)
        
        # Display key milestones
        print(f"\n{Colors.OKBLUE}Key Milestones:{Colors.ENDC}")
        print("-" * 80)
        
        for year in [5, 10, 15, 20]:
            if year <= years:
                row = df[df['Year'] == year].iloc[0]
                print(f"\n{Colors.BOLD}Year {year} (Age {int(row['Age'])}){Colors.ENDC}")
                print(f"  Invested: ₹{row['Total Invested']:,.0f}")
                for col in df.columns:
                    if '%' in col:
                        print(f"  {col}: ₹{row[col]:,.0f}")
        
        return df
    
    def calculate_monthly_breakdown(self, year):
        """
        Calculate what ₹15,000 monthly investment looks like over time
        
        Args:
            year: Specific year to analyze
        """
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.HEADER}💰 MONTHLY INVESTMENT BREAKDOWN - YEAR {year}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")
        
        monthly = MONTHLY_INVESTMENT
        months = year * 12
        total = monthly * months
        
        print(f"\nMonthly Investment: {Colors.OKGREEN}₹{monthly:,}{Colors.ENDC}")
        print(f"Total Months: {months}")
        print(f"Total Invested (Principal): {Colors.OKGREEN}₹{total:,}{Colors.ENDC}")
        
        print(f"\n{Colors.OKBLUE}With Returns:{Colors.ENDC}")
        for scenario_name, annual_rate in EXPECTED_RETURNS.items():
            projection = self.project_future_value(monthly, months, annual_rate)
            print(f"  {scenario_name.title()}: {Colors.OKGREEN}₹{projection['future_value']:,.0f}{Colors.ENDC} " +
                  f"(+₹{projection['total_returns']:,.0f} returns)")
    
    def export_analysis_to_csv(self, df, filename):
        """
        Export Spark DataFrame to CSV
        
        Args:
            df: Spark DataFrame
            filename: Output filename
        """
        try:
            # Convert to Pandas for easy CSV export
            pandas_df = df.toPandas()
            
            # Ensure data directory exists
            os.makedirs(DATA_DIR, exist_ok=True)
            
            filepath = os.path.join(DATA_DIR, filename)
            pandas_df.to_csv(filepath, index=False)
            
            print(f"\n{Colors.OKGREEN}💾 Exported analysis to: {filepath}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error exporting data: {e}{Colors.ENDC}")
    
    def export_yearly_projection_to_csv(self, df, filename="yearly_projection.csv"):
        """
        Export yearly projection DataFrame to CSV
        
        Args:
            df: Pandas DataFrame
            filename: Output filename
        """
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            filepath = os.path.join(DATA_DIR, filename)
            df.to_csv(filepath, index=False)
            print(f"\n{Colors.OKGREEN}💾 Exported yearly projection to: {filepath}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error exporting data: {e}{Colors.ENDC}")
    
    def stop_spark(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print(f"\n{Colors.WARNING}🛑 PySpark session stopped{Colors.ENDC}")


def main():
    """Demo PySpark analyzer functionality"""
    
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 PYSPARK PORTFOLIO ANALYZER{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    try:
        # Initialize analyzer
        analyzer = PySparkAnalyzer()
        
        # Generate SIP projections
        print(f"\n{Colors.OKCYAN}Generating 20-year SIP projections...{Colors.ENDC}")
        df_projections = analyzer.generate_sip_projection(MONTHLY_INVESTMENT, INVESTMENT_HORIZON)
        
        # Show results in table format
        print(f"\n{Colors.HEADER}📊 PROJECTION SUMMARY TABLE{Colors.ENDC}")
        df_projections.show(truncate=False)
        
        # Export to CSV
        analyzer.export_analysis_to_csv(df_projections, "sip_projections.csv")
        
        # Generate year-by-year projection
        df_yearly = analyzer.generate_year_by_year_projection(MONTHLY_INVESTMENT, INVESTMENT_HORIZON)
        
        # Export yearly projection
        analyzer.export_yearly_projection_to_csv(df_yearly, "yearly_projection.csv")
        
        # Show monthly breakdown for different years
        for year in [5, 10, 20]:
            analyzer.calculate_monthly_breakdown(year)
        
        # Stop Spark
        analyzer.stop_spark()
        
        print(f"\n{Colors.OKGREEN}✅ Analysis complete!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}📂 Check the 'data/' folder for exported CSV files{Colors.ENDC}\n")
    
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error: {e}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()

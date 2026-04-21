"""
Performance Graphs - Visual analytics of bot performance
Shows beautiful charts of daily performance, strategy comparison, etc.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from data.storage import DataStorage
import numpy as np

class PerformanceGraphs:
    """Generate performance visualization graphs"""
    
    def __init__(self):
        self.storage = DataStorage()
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_all_graphs(self, days=30):
        """Generate all performance graphs"""
        print("\n📊 Generating Performance Graphs...")
        print(f"📅 Period: Last {days} days\n")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('🤖 Trading Bot Performance Dashboard', fontsize=20, fontweight='bold')
        
        # 1. Daily P&L Chart
        ax1 = plt.subplot(3, 2, 1)
        self.plot_daily_pnl(ax1, days)
        
        # 2. Cumulative Returns
        ax2 = plt.subplot(3, 2, 2)
        self.plot_cumulative_returns(ax2, days)
        
        # 3. Strategy Performance Comparison
        ax3 = plt.subplot(3, 2, 3)
        self.plot_strategy_comparison(ax3)
        
        # 4. Win Rate Over Time
        ax4 = plt.subplot(3, 2, 4)
        self.plot_win_rate_trend(ax4, days)
        
        # 5. Trade Distribution
        ax5 = plt.subplot(3, 2, 5)
        self.plot_trade_distribution(ax5, days)
        
        # 6. Hourly Performance
        ax6 = plt.subplot(3, 2, 6)
        self.plot_hourly_performance(ax6, days)
        
        plt.tight_layout()
        
        # Save the figure
        filename = f'bot_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Graphs saved to: {filename}")
        
        # Show the graphs
        plt.show()
        
        print("\n📈 Generating individual detailed graphs...\n")
        
        # Generate additional detailed graphs
        self.plot_equity_curve(days)
        self.plot_strategy_heatmap()
        
        print("\n✅ All graphs generated successfully!")
    
    def plot_daily_pnl(self, ax, days):
        """Plot daily profit/loss"""
        query = f'''
            SELECT DATE(timestamp) as date, SUM(pnl) as daily_pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
            ax.set_title('📊 Daily P&L')
            return
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Color bars based on profit/loss
        colors = ['green' if x > 0 else 'red' for x in df['daily_pnl']]
        
        ax.bar(df['date'], df['daily_pnl'], color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_title('📊 Daily P&L', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('P&L (₹)')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    def plot_cumulative_returns(self, ax, days):
        """Plot cumulative returns over time"""
        query = f'''
            SELECT timestamp, pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
            ax.set_title('📈 Cumulative Returns')
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['cumulative_pnl'] = df['pnl'].cumsum()
        
        ax.plot(df['timestamp'], df['cumulative_pnl'], linewidth=2, color='blue', marker='o', markersize=3)
        ax.fill_between(df['timestamp'], df['cumulative_pnl'], alpha=0.3, color='blue')
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax.set_title('📈 Cumulative Returns', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative P&L (₹)')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Add final value annotation
        final_value = df['cumulative_pnl'].iloc[-1]
        ax.annotate(f'₹{final_value:,.0f}', 
                   xy=(df['timestamp'].iloc[-1], final_value),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   fontsize=10, fontweight='bold')
    
    def plot_strategy_comparison(self, ax):
        """Compare strategy performance"""
        df = self.storage.get_all_strategies_performance()
        
        if df.empty:
            ax.text(0.5, 0.5, 'No strategy data yet', ha='center', va='center', fontsize=12)
            ax.set_title('🎯 Strategy Comparison')
            return
        
        df = df[df['total_trades'] > 0].sort_values('win_rate', ascending=True)
        
        colors = ['green' if x >= 50 else 'red' for x in df['win_rate']]
        
        ax.barh(df['strategy_name'], df['win_rate'], color=colors, alpha=0.7, edgecolor='black')
        ax.axvline(x=50, color='black', linestyle='--', linewidth=1, label='50% Breakeven')
        ax.set_title('🎯 Strategy Win Rate Comparison', fontsize=14, fontweight='bold')
        ax.set_xlabel('Win Rate (%)')
        ax.set_ylabel('Strategy')
        ax.grid(True, alpha=0.3, axis='x')
        ax.legend()
        
        # Add value labels
        for i, (idx, row) in enumerate(df.iterrows()):
            ax.text(row['win_rate'] + 1, i, f"{row['win_rate']:.1f}%", 
                   va='center', fontweight='bold')
    
    def plot_win_rate_trend(self, ax, days):
        """Plot win rate trend over time"""
        query = f'''
            SELECT timestamp, pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty or len(df) < 10:
            ax.text(0.5, 0.5, 'Need more trades', ha='center', va='center', fontsize=12)
            ax.set_title('📊 Win Rate Trend')
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['win'] = (df['pnl'] > 0).astype(int)
        
        # Calculate rolling win rate (last 10 trades)
        df['rolling_win_rate'] = df['win'].rolling(window=10, min_periods=1).mean() * 100
        
        ax.plot(df['timestamp'], df['rolling_win_rate'], linewidth=2, color='purple', marker='o', markersize=3)
        ax.axhline(y=50, color='black', linestyle='--', linewidth=1, label='50% Breakeven')
        ax.fill_between(df['timestamp'], df['rolling_win_rate'], 50, 
                       where=(df['rolling_win_rate'] >= 50), alpha=0.3, color='green', label='Above 50%')
        ax.fill_between(df['timestamp'], df['rolling_win_rate'], 50, 
                       where=(df['rolling_win_rate'] < 50), alpha=0.3, color='red', label='Below 50%')
        ax.set_title('📊 Win Rate Trend (Rolling 10 trades)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Win Rate (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
    
    def plot_trade_distribution(self, ax, days):
        """Plot distribution of trade outcomes"""
        query = f'''
            SELECT pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
            ax.set_title('📊 Trade Distribution')
            return
        
        wins = df[df['pnl'] > 0]['pnl']
        losses = df[df['pnl'] <= 0]['pnl']
        
        ax.hist([wins, losses], bins=20, label=['Wins', 'Losses'], 
               color=['green', 'red'], alpha=0.7, edgecolor='black')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=2)
        ax.set_title('📊 Trade P&L Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('P&L (₹)')
        ax.set_ylabel('Number of Trades')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def plot_hourly_performance(self, ax, days):
        """Plot performance by hour of day"""
        query = f'''
            SELECT timestamp, pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
            ax.set_title('⏰ Hourly Performance')
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        hourly_pnl = df.groupby('hour')['pnl'].sum()
        
        colors = ['green' if x > 0 else 'red' for x in hourly_pnl.values]
        
        ax.bar(hourly_pnl.index, hourly_pnl.values, color=colors, alpha=0.7, edgecolor='black')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_title('⏰ Performance by Hour', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Total P&L (₹)')
        ax.set_xticks(range(9, 16))
        ax.grid(True, alpha=0.3)
    
    def plot_equity_curve(self, days):
        """Plot detailed equity curve"""
        query = f'''
            SELECT timestamp, pnl
            FROM trades
            WHERE timestamp >= datetime('now', '-{days} days')
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            print("⚠️  No data for equity curve")
            return
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['equity'] = 100000 + df['cumulative_pnl']  # Starting capital
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(df['timestamp'], df['equity'], linewidth=2, color='darkblue', label='Portfolio Value')
        ax.axhline(y=100000, color='gray', linestyle='--', linewidth=1, label='Starting Capital')
        ax.fill_between(df['timestamp'], df['equity'], 100000, 
                       where=(df['equity'] >= 100000), alpha=0.3, color='green')
        ax.fill_between(df['timestamp'], df['equity'], 100000, 
                       where=(df['equity'] < 100000), alpha=0.3, color='red')
        
        ax.set_title('💰 Portfolio Equity Curve', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value (₹)', fontsize=12)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        
        # Add statistics box
        final_equity = df['equity'].iloc[-1]
        roi = ((final_equity - 100000) / 100000) * 100
        max_equity = df['equity'].max()
        min_equity = df['equity'].min()
        
        stats_text = f"Final: ₹{final_equity:,.0f}\nROI: {roi:.2f}%\nMax: ₹{max_equity:,.0f}\nMin: ₹{min_equity:,.0f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        filename = f'equity_curve_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Equity curve saved to: {filename}")
        plt.show()
    
    def plot_strategy_heatmap(self):
        """Plot strategy performance heatmap"""
        query = '''
            SELECT strategy, DATE(timestamp) as date, SUM(pnl) as daily_pnl
            FROM trades
            GROUP BY strategy, DATE(timestamp)
            ORDER BY date, strategy
        '''
        df = pd.read_sql_query(query, self.storage.conn)
        
        if df.empty:
            print("⚠️  No data for strategy heatmap")
            return
        
        # Pivot table
        pivot = df.pivot_table(values='daily_pnl', index='strategy', columns='date', fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto')
        
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_yticks(range(len(pivot.index)))
        ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
        ax.set_yticklabels(pivot.index)
        
        ax.set_title('🔥 Strategy Performance Heatmap', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Strategy', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Daily P&L (₹)', rotation=270, labelpad=20)
        
        plt.tight_layout()
        filename = f'strategy_heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Strategy heatmap saved to: {filename}")
        plt.show()

def main():
    """Main function"""
    print("\n📊 Bot Performance Graphs Generator")
    print("="*50)
    
    graphs = PerformanceGraphs()
    
    print("\nChoose time period:")
    print("  1. Last 7 days")
    print("  2. Last 30 days")
    print("  3. Last 90 days")
    print("  4. All time")
    
    choice = input("\nEnter choice (1-4) [default: 2]: ").strip() or "2"
    
    days_map = {
        "1": 7,
        "2": 30,
        "3": 90,
        "4": 10000
    }
    
    days = days_map.get(choice, 30)
    
    graphs.generate_all_graphs(days)

if __name__ == "__main__":
    main()

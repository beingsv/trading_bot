"""
Data Storage - Store market data, trades, and learning data
"""
import sqlite3
import pandas as pd
from datetime import datetime
from config.config import DATABASE_PATH
import os
import shutil

class DataStorage:
    """Handle all database operations"""
    
    def __init__(self):
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        self.create_tables()
        self.backup_count = 0
        
        # Import config for backup settings
        from config.config import AUTO_BACKUP_ENABLED
        self.auto_backup_enabled = AUTO_BACKUP_ENABLED
    
    def create_tables(self):
        """Create necessary tables"""
        cursor = self.conn.cursor()
        
        # Historical price data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp DATETIME,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER
            )
        ''')
        
        # Trades log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                strategy TEXT,
                action TEXT,
                price REAL,
                quantity INTEGER,
                timestamp DATETIME,
                pnl REAL,
                reason TEXT
            )
        ''')
        
        # Strategy performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT,
                total_trades INTEGER,
                winning_trades INTEGER,
                losing_trades INTEGER,
                total_pnl REAL,
                win_rate REAL,
                avg_profit REAL,
                avg_loss REAL,
                sharpe_ratio REAL,
                last_updated DATETIME
            )
        ''')
        
        # Market conditions log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                condition TEXT,
                nifty_change REAL,
                volatility REAL,
                fii_activity TEXT,
                news_sentiment REAL
            )
        ''')
        
        self.conn.commit()
    
    def save_trade(self, symbol, strategy, action, price, quantity, pnl=0, reason=""):
        """Log a trade"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (symbol, strategy, action, price, quantity, timestamp, pnl, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, strategy, action, price, quantity, datetime.now(), pnl, reason))
        self.conn.commit()
        
        # Auto-backup every 10 trades (only if enabled)
        if self.auto_backup_enabled:
            self.backup_count += 1
            if self.backup_count >= 10:
                self.backup_database()
                self.backup_count = 0
    
    def backup_database(self, silent=False):
        """Create backup of database"""
        try:
            from config.config import BACKUP_KEEP_LAST_N
            
            backup_dir = 'data/backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'{backup_dir}/trading_bot_backup_{timestamp}.db'
            
            shutil.copy2(DATABASE_PATH, backup_file)
            
            # Keep only last N backups
            backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
            if len(backups) > BACKUP_KEEP_LAST_N:
                for old_backup in backups[:-BACKUP_KEEP_LAST_N]:
                    os.remove(os.path.join(backup_dir, old_backup))
            
            if not silent:
                print(f"💾 Database backed up: {backup_file}")
            return backup_file
        except Exception as e:
            if not silent:
                print(f"⚠️  Backup failed: {e}")
            return None
    
    def restore_from_backup(self, backup_file=None):
        """Restore database from backup"""
        try:
            backup_dir = 'data/backups'
            
            if backup_file is None:
                # Get latest backup
                backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
                if not backups:
                    print("No backups found")
                    return False
                backup_file = os.path.join(backup_dir, backups[-1])
            
            # Close current connection
            self.conn.close()
            
            # Restore backup
            shutil.copy2(backup_file, DATABASE_PATH)
            
            # Reconnect
            self.conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            
            print(f"✅ Database restored from: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def get_strategy_trades(self, strategy_name, days=30):
        """Get trades for a specific strategy"""
        query = '''
            SELECT * FROM trades 
            WHERE strategy = ? AND timestamp >= datetime('now', '-{} days')
        '''.format(days)
        return pd.read_sql_query(query, self.conn, params=(strategy_name,))
    
    def update_strategy_performance(self, strategy_name, metrics):
        """Update strategy performance metrics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO strategy_performance 
            (strategy_name, total_trades, winning_trades, losing_trades, total_pnl, 
             win_rate, avg_profit, avg_loss, sharpe_ratio, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (strategy_name, metrics['total_trades'], metrics['winning_trades'],
              metrics['losing_trades'], metrics['total_pnl'], metrics['win_rate'],
              metrics['avg_profit'], metrics['avg_loss'], metrics['sharpe_ratio'],
              datetime.now()))
        self.conn.commit()
    
    def get_all_strategies_performance(self):
        """Get performance of all strategies"""
        return pd.read_sql_query('SELECT * FROM strategy_performance', self.conn)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

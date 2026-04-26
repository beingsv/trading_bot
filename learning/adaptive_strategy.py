"""
Adaptive Strategy Manager - Automatically adjusts strategy parameters based on performance
"""
import json
import os
from datetime import datetime, timedelta

class AdaptiveStrategyManager:
    """
    Automatically adjusts strategy parameters based on learning
    - Modifies thresholds
    - Adjusts confidence requirements
    - Changes position sizing
    - Adapts to market conditions
    """
    
    def __init__(self, storage):
        self.storage = storage
        self.config_file = 'data/adaptive_config.json'
        self.load_adaptive_config()
        self.learning_history = []
    
    def load_adaptive_config(self):
        """Load or create adaptive configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default adaptive config
            self.config = {
                'momentum_threshold': 0.05,  # Start at 0.05%
                'confidence_threshold': 50,   # Start at 50%
                'position_size_percent': 40,  # Start at 40%
                'stop_loss_percent': 25,      # Start at 25%
                'take_profit_percent': 40,    # Start at 40%
                'min_votes_required': 1,      # Start at 1 vote
                'market_condition_filters': {
                    'SIDEWAYS': {'enabled': True, 'confidence_boost': 0},
                    'BULL_TRENDING': {'enabled': True, 'confidence_boost': 5},
                    'BEAR_TRENDING': {'enabled': True, 'confidence_boost': 5},
                    'HIGH_VOLATILITY': {'enabled': True, 'confidence_boost': -10}
                },
                'last_updated': datetime.now().isoformat(),
                'total_adjustments': 0
            }
            self.save_config()
    
    def save_config(self):
        """Save adaptive configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def analyze_and_adapt(self):
        """
        Analyze recent performance and automatically adjust parameters
        Called at end of each trading day
        """
        print("\n" + "="*60)
        print("🧠 ADAPTIVE LEARNING - Analyzing Performance...")
        print("="*60)
        
        # Get recent trades (last 7 days)
        trades_df = self.storage.conn.execute(
            "SELECT * FROM trades WHERE timestamp >= datetime('now', '-7 days')"
        ).fetchall()
        
        if len(trades_df) < 5:
            print("⏳ Not enough trades yet (need 5+). Keeping current settings.")
            return
        
        # Convert to dict for analysis
        trades = []
        for trade in trades_df:
            trades.append({
                'pnl': trade[7],
                'strategy': trade[2],
                'timestamp': trade[6]
            })
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = len([t for t in trades if t['pnl'] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum([t['pnl'] for t in trades])
        
        print(f"\n📊 Recent Performance (Last 7 Days):")
        print(f"   Total Trades: {total_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total P&L: ₹{total_pnl:.2f}")
        
        adjustments_made = []
        
        # ADAPTATION LOGIC
        
        # 1. Adjust Confidence Threshold based on Win Rate
        if win_rate < 40:
            # Poor performance - be more selective
            old_threshold = self.config['confidence_threshold']
            self.config['confidence_threshold'] = min(old_threshold + 5, 75)
            adjustments_made.append(
                f"📈 Confidence threshold: {old_threshold}% → {self.config['confidence_threshold']}% (Win rate too low)"
            )
        elif win_rate > 65:
            # Good performance - can be more aggressive
            old_threshold = self.config['confidence_threshold']
            self.config['confidence_threshold'] = max(old_threshold - 3, 45)
            adjustments_made.append(
                f"📉 Confidence threshold: {old_threshold}% → {self.config['confidence_threshold']}% (Win rate good)"
            )
        
        # 2. Adjust Position Size based on P&L
        if total_pnl < -500:
            # Losing money - reduce position size
            old_size = self.config['position_size_percent']
            self.config['position_size_percent'] = max(old_size - 5, 20)
            adjustments_made.append(
                f"📉 Position size: {old_size}% → {self.config['position_size_percent']}% (Reducing risk)"
            )
        elif total_pnl > 1000 and win_rate > 60:
            # Making money consistently - can increase size
            old_size = self.config['position_size_percent']
            self.config['position_size_percent'] = min(old_size + 5, 50)
            adjustments_made.append(
                f"📈 Position size: {old_size}% → {self.config['position_size_percent']}% (Increasing size)"
            )
        
        # 3. Adjust Stop Loss based on loss magnitude
        avg_loss = sum([t['pnl'] for t in trades if t['pnl'] < 0]) / losing_trades if losing_trades > 0 else 0
        if avg_loss < -300:
            # Losses too large - tighten stop loss
            old_sl = self.config['stop_loss_percent']
            self.config['stop_loss_percent'] = max(old_sl - 3, 15)
            adjustments_made.append(
                f"🛡️ Stop loss: {old_sl}% → {self.config['stop_loss_percent']}% (Losses too large)"
            )
        
        # 4. Adjust Momentum Threshold based on false signals
        if win_rate < 45 and total_trades > 10:
            # Too many false signals - increase threshold
            old_momentum = self.config['momentum_threshold']
            self.config['momentum_threshold'] = min(old_momentum + 0.02, 0.15)
            adjustments_made.append(
                f"📊 Momentum threshold: {old_momentum:.2f}% → {self.config['momentum_threshold']:.2f}% (Reducing noise)"
            )
        
        # 5. Adjust Voting Requirements
        if win_rate < 35:
            # Very poor - require more agreement
            old_votes = self.config['min_votes_required']
            self.config['min_votes_required'] = min(old_votes + 1, 2)
            adjustments_made.append(
                f"🗳️ Min votes required: {old_votes} → {self.config['min_votes_required']} (Need more consensus)"
            )
        elif win_rate > 70 and total_trades > 15:
            # Excellent - can be more aggressive
            old_votes = self.config['min_votes_required']
            self.config['min_votes_required'] = max(old_votes - 1, 1)
            adjustments_made.append(
                f"🗳️ Min votes required: {old_votes} → {self.config['min_votes_required']} (Can be aggressive)"
            )
        
        # 6. Market Condition Filters
        # Get market condition from recent trades
        market_condition = 'SIDEWAYS'  # Default, should be fetched from context
        
        if market_condition == 'SIDEWAYS' and win_rate < 40:
            # Struggling in sideways - reduce confidence boost
            self.config['market_condition_filters']['SIDEWAYS']['confidence_boost'] = -5
            adjustments_made.append(
                f"🌊 SIDEWAYS market filter: More cautious (boost: -5%)"
            )
        
        # Save adjustments
        if adjustments_made:
            self.config['last_updated'] = datetime.now().isoformat()
            self.config['total_adjustments'] += len(adjustments_made)
            self.save_config()
            
            print(f"\n✅ Made {len(adjustments_made)} automatic adjustments:")
            for adj in adjustments_made:
                print(f"   {adj}")
            
            # Log learning
            self.learning_history.append({
                'timestamp': datetime.now(),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'adjustments': adjustments_made
            })
        else:
            print("\n✅ Current settings are optimal. No changes needed.")
        
        print("\n" + "="*60)
        print("📋 CURRENT ADAPTIVE SETTINGS:")
        print("="*60)
        print(f"   Confidence Threshold: {self.config['confidence_threshold']}%")
        print(f"   Position Size: {self.config['position_size_percent']}%")
        print(f"   Stop Loss: {self.config['stop_loss_percent']}%")
        print(f"   Take Profit: {self.config['take_profit_percent']}%")
        print(f"   Momentum Threshold: {self.config['momentum_threshold']:.2f}%")
        print(f"   Min Votes Required: {self.config['min_votes_required']}")
        print(f"   Total Adjustments Made: {self.config['total_adjustments']}")
        print("="*60 + "\n")
    
    def get_current_config(self):
        """Get current adaptive configuration"""
        return self.config
    
    def apply_market_condition_filter(self, base_confidence, market_condition):
        """Apply market condition boost/penalty to confidence"""
        if market_condition in self.config['market_condition_filters']:
            boost = self.config['market_condition_filters'][market_condition]['confidence_boost']
            return base_confidence + boost
        return base_confidence
    
    def should_trade_in_condition(self, market_condition):
        """Check if trading is enabled for this market condition"""
        if market_condition in self.config['market_condition_filters']:
            return self.config['market_condition_filters'][market_condition]['enabled']
        return True
    
    def get_learning_summary(self):
        """Get summary of all learning adjustments"""
        return {
            'total_adjustments': self.config['total_adjustments'],
            'last_updated': self.config['last_updated'],
            'current_config': self.config,
            'learning_history': self.learning_history
        }

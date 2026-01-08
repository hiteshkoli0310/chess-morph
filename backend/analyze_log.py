import pandas as pd
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_log():
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game_log.csv")
    
    if not os.path.exists(log_file):
        print("No game log found.")
        return

    try:
        df = pd.read_csv(log_file)
    except Exception as e:
        print(f"Error reading log: {e}")
        return

    if df.empty:
        print("Log is empty.")
        return

    print("\n--- Game Log Analysis ---")
    print(f"Total Moves Recorded: {len(df)}")
    
    # 1. Persona Distribution
    print("\n[Bot Persona Distribution]")
    print(df['bot_persona'].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')

    # 2. User Performance
    print("\n[User Performance Stats]")
    print(f"Average CP Loss: {df['cp_loss'].mean():.2f}")
    print(f"Blunder Rate: {(df['is_blunder'].sum() / len(df) * 100):.1f}%")
    
    # 3. Correlation: Time vs CP Loss
    # Simple check: Do fast moves lead to more blunders?
    fast_moves = df[df['time_taken'] < 3.0]
    slow_moves = df[df['time_taken'] >= 3.0]
    
    print("\n[Time vs Performance]")
    if not fast_moves.empty:
        print(f"Fast Moves (<3s) Avg CP Loss: {fast_moves['cp_loss'].mean():.2f}")
    if not slow_moves.empty:
        print(f"Slow Moves (>3s) Avg CP Loss: {slow_moves['cp_loss'].mean():.2f}")

    # 4. Tuning Recommendations
    print("\n[Tuning Recommendations]")
    avg_cp_loss = df['cp_loss'].mean()
    median_cp_loss = df['cp_loss'].median()
    blunder_rate = (df['is_blunder'].sum() / len(df)) * 100
    assist_rate = (df['bot_persona'] == 'Assist Mode').mean() * 100
    mercy_rate = (df['bot_persona'] == 'Mercy Mode').mean() * 100
    defensive_rate = (df['bot_persona'] == 'Defensive Master').mean() * 100
    balanced_rate = (df['bot_persona'] == 'Balanced Challenger').mean() * 100
    
    # Time segments
    fast_moves = df[df['time_taken'] < 3.0]
    slow_moves = df[df['time_taken'] >= 3.0]
    fast_cp_loss = fast_moves['cp_loss'].mean() if not fast_moves.empty else None
    slow_cp_loss = slow_moves['cp_loss'].mean() if not slow_moves.empty else None
    
    # Difficulty banding suggestions
    if avg_cp_loss > 100:
        print("- User is struggling significantly (High CP Loss > 100).")
        print("  Action: Increase USER_LOSING_MARGIN (e.g. -200 -> -100) to trigger help sooner.")
    elif avg_cp_loss > 50:
        print(f"- User is making moderate mistakes (Avg CP Loss: {avg_cp_loss:.1f}).")
        print("  Action: This is a good 'Challenge' range. If you want an easier game, increase USER_LOSING_MARGIN slightly (e.g. -200 -> -150).")
    elif avg_cp_loss < 20:
        print("- User is playing very well (Low CP Loss < 20).")
        print("  Action: Decrease USER_WINNING_MARGIN (e.g. 200 -> 150) to challenge them sooner.")
    else:
        print(f"- User performance is balanced (Avg CP Loss: {avg_cp_loss:.1f}).")
        print("  Action: Current settings provide a fair match. No major changes needed.")
    
    # Persona balance
    if mercy_rate > 30:
        print(f"- Mercy Mode is frequent ({mercy_rate:.1f}%).")
        print("  Action: Raise MISTAKE_SEVERE_MIN (e.g. 300 -> 400) to give bigger swings only when necessary.")
    if assist_rate > 30 and balanced_rate < 50:
        print(f"- Assist Mode is high ({assist_rate:.1f}%) with limited Balanced play.")
        print("  Action: Lower MISTAKE_NATURAL_MIN (e.g. 150 -> 120) and cap MISTAKE_NATURAL_MAX (e.g. 250) to make assistance more subtle.")
    if defensive_rate > 10:
        print(f"- Defensive Master triggers often ({defensive_rate:.1f}%).")
        print("  Action: Increase USER_WINNING_MARGIN (e.g. 200 -> 250) to avoid over-defending too early.")

    # Time-awareness tuning
    if fast_cp_loss is not None and slow_cp_loss is not None:
        if slow_cp_loss - fast_cp_loss > 40:
            print("- Player's accuracy drops on slower moves.")
            print("  Action: Increase FAST_PLAY_LIMIT (e.g. 3.0 -> 4.0) so 'fast recovery' logic triggers less, keeping challenge consistent.")
        elif fast_cp_loss - slow_cp_loss > 20:
            print("- Player performs better when moving quickly.")
            print("  Action: Decrease FAST_PLAY_LIMIT (e.g. 3.0 -> 2.0) to reward quick play with rarer mercy moments.")

    # Blunder adaptivity
    if blunder_rate > 15:
        print(f"- Blunder rate is high ({blunder_rate:.1f}%).")
        print("  Action: Lower USER_LOSING_MARGIN (more negative, e.g. -200 -> -250) so mercy triggers earlier and lasts longer.")
        print("  Action: Also consider lowering MISTAKE_SEVERE_MIN (e.g. 300 -> 250) to provide bigger comeback chances.")
    elif blunder_rate < 5 and avg_cp_loss < 40:
        print(f"- Few blunders ({blunder_rate:.1f}%) and low CP loss.")
        print("  Action: Raise USER_WINNING_MARGIN (e.g. 200 -> 250) and reduce MISTAKE_NATURAL_MIN (e.g. 150 -> 130) to keep tension high.")

    # Median-based fine-tuning
    print(f"- Median CP Loss: {median_cp_loss:.1f} (useful for robust tuning vs outliers).")
    if median_cp_loss > 80:
        print("  Action: Consider a combined adjustment: USER_LOSING_MARGIN -> -120, MISTAKE_SEVERE_MIN -> 350, FAST_PLAY_LIMIT -> 3.5.")
    elif median_cp_loss < 25:
        print("  Action: Consider challenging settings: USER_WINNING_MARGIN -> 160, MISTAKE_NATURAL_MIN -> 170, FAST_PLAY_LIMIT -> 2.5.")

if __name__ == "__main__":
    analyze_log()

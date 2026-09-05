import os
import pandas as pd
import numpy as np

# ==============================================================================
# CONFIGURATION & FILE LOADING
# ==============================================================================
FILE_NAME = 'only_stake_dataall.csv'
POSSIBLE_PATHS = [
    FILE_NAME,
    f'/storage/emulated/0/Download/{FILE_NAME}',
    f'/sdcard/Download/{FILE_NAME}'
]

def load_dataset():
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            try:
                print(f"[INFO] Loading data from: {path}")
                return pd.read_csv(path)
            except Exception as e:
                print(f"[ERROR] Failed to read {path}: {e}")
    raise FileNotFoundError("Dataset file not found in provided paths.")

df = load_dataset()

# ==============================================================================
# DATA CLEANING & PARSING
# ==============================================================================
# Safe Numeric Parsing
df['TokenValue_Clean'] = pd.to_numeric(
    df['TokenValue'].astype(str).str.replace(',', ''), errors='coerce'
).fillna(0)

# Safe Datetime Parsing & Chronological Sorting
df['DateTime (UTC)'] = pd.to_datetime(df['DateTime (UTC)'], errors='coerce')
df = df.dropna(subset=['DateTime (UTC)']).sort_values('DateTime (UTC)')

# Period Grouping for Strict Chronological Order
df['YearMonth'] = df['DateTime (UTC)'].dt.to_period('M')

symbol = df['TokenSymbol'].value_counts().idxmax() if 'TokenSymbol' in df.columns else 'USDT'

# ==============================================================================
# METRICS COMPUTATION
# ==============================================================================
total_investment = df['TokenValue_Clean'].sum()
total_tx = len(df)
first_date = df['DateTime (UTC)'].min()
last_date = df['DateTime (UTC)'].max()
total_days = max((last_date - first_date).days, 1)

# Advanced Statistical Metrics
mean_stake = df['TokenValue_Clean'].mean()
median_stake = df['TokenValue_Clean'].median()  # Protects against whale skewness
max_stake = df['TokenValue_Clean'].max()
unique_investors = df['From'].nunique()

# 10% Multi-Wallet Referral Route Deduction Simulation
multi_wallet_cut = total_investment * 0.10
net_pool_liquidity = total_investment * 0.90
promised_liability_3x = total_investment * 3.00

# Monthly Aggregation
monthly_summary = df.groupby('YearMonth').agg(
    Total_Investment=('TokenValue_Clean', 'sum'),
    Tx_Count=('TokenValue_Clean', 'count')
).reset_index()
monthly_summary['Month'] = monthly_summary['YearMonth'].dt.strftime('%B %Y')

# Top Whales / Concentration Analysis
top_whales = df.groupby('From').agg(
    Total_Staked=('TokenValue_Clean', 'sum'),
    Tx_Count=('TokenValue_Clean', 'count')
).reset_index().sort_values('Total_Staked', ascending=False).head(10)

top_10_volume = top_whales['Total_Staked'].sum()
whales_share_pct = (top_10_volume / total_investment) * 100 if total_investment > 0 else 0

# Investment Brackets
bins = [-1, 10, 100, 1000, float('inf')]
labels = ['Micro (<10)', 'Small (10-100)', 'Medium (100-1k)', 'Whale (>1k)']
df['Bracket'] = pd.cut(df['TokenValue_Clean'], bins=bins, labels=labels)
bracket_summary = df.groupby('Bracket', observed=False).agg(
    Tx_Count=('TokenValue_Clean', 'count'),
    Total_Volume=('TokenValue_Clean', 'sum')
).reset_index()

# ==============================================================================
# PROFESSIONAL CONSOLE REPORT GENERATION
# ==============================================================================
print("\n" + "=" * 70)
print("      KAIRO TOKEN STAKING MANAGER TRANSACTIONS - RISK ANALYTICS      ")
print("=" * 70)

print("\n📌 SECTION 1: GLOBAL DATASET SUMMARY")
print("-" * 70)
print(f"📅 Audit Period          : {first_date.strftime('%d %b %Y')} to {last_date.strftime('%d %b %Y')} ({total_days} Days)")
print(f"📊 Total Transactions    : {total_tx:,}")
print(f"👥 Unique Depositors     : {unique_investors:,}")
print(f"💰 Total Inflow Volume   : {total_investment:,.2f} {symbol}")
print(f"📈 Mean Deposit Size     : {mean_stake:,.2f} {symbol}")
print(f"🎯 Median Deposit Size   : {median_stake:,.2f} {symbol}  (Typical Investor Deposit)")
print(f"🔝 Largest Single Deposit: {max_stake:,.2f} {symbol}")

print("\n⚠️ SECTION 2: SMART CONTRACT LIQUIDITY & DEDUCTION ARCHITECTURE")
print("-" * 70)
print(f"💸 Total Deposited (100%)    : {total_investment:,.2f} {symbol}")
print(f"🚨 Immediate 10% Cut Split   : -{multi_wallet_cut:,.2f} {symbol} (Distributed across 7 Uplines/Promoter Wallets)")
print(f"🏦 Net Contract Reserve (90%): {net_pool_liquidity:,.2f} {symbol}")
print(f"🔴 Total Promised Outflow    : {promised_liability_3x:,.2f} {symbol} (Fixed 300% Return Commitment)")
print(f"📉 Deficit / Insolvency Gap  : -{(promised_liability_3x - net_pool_liquidity):,.2f} {symbol}")

print("\n📅 SECTION 3: MONTHLY INFLOW DYNAMICS")
print("-" * 70)
monthly_table = monthly_summary[['Month', 'Tx_Count', 'Total_Investment']].copy()
monthly_table.columns = ['Month', 'Transactions', f'Volume ({symbol})']
monthly_table[f'Volume ({symbol})'] = monthly_table[f'Volume ({symbol})'].map(lambda x: f"{x:,.2f}")
print(monthly_table.to_string(index=False))

print("\n🐋 SECTION 4: TOP 10 WALLET CONCENTRATION (INSIDER RISK)")
print("-" * 70)
print(f"📊 Top 10 Concentration Share : {whales_share_pct:.2f}% of total deposits")
top_whales_disp = top_whales.copy()
top_whales_disp['Wallet Address'] = top_whales_disp['From'].apply(lambda x: f"{x[:6]}...{x[-4:]}")
top_whales_disp['Share (%)'] = (top_whales_disp['Total_Staked'] / total_investment * 100).map(lambda x: f"{x:.2f}%")
top_whales_disp['Total_Staked'] = top_whales_disp['Total_Staked'].map(lambda x: f"{x:,.2f} {symbol}")
print(top_whales_disp[['Wallet Address', 'Total_Staked', 'Tx_Count', 'Share (%)']].to_string(index=False))

print("\n📊 SECTION 5: DEPOSIT SIZE BREAKDOWN")
print("-" * 70)
bracket_summary['Share (%)'] = (bracket_summary['Total_Volume'] / total_investment * 100).map(lambda x: f"{x:.2f}%")
bracket_summary['Total_Volume'] = bracket_summary['Total_Volume'].map(lambda x: f"{x:,.2f} {symbol}")
print(bracket_summary[['Bracket', 'Tx_Count', 'Total_Volume', 'Share (%)']].to_string(index=False))

print("\n" + "=" * 70)
print("             CRITICAL AUDIT FINDINGS & STRUCTURAL WARNING            ")
print("=" * 70)
print("1. ZERO EXTERNAL YIELD GENERATION:")
print("   Smart contract audits confirm zero interaction with DEXs (Uniswap/PancakeSwap),")
print("   liquidity lending protocols (Aave), or automated trading algorithms.")
print("   The smart contract acts purely as a fund routing script (Crowdfunding).")
print("\n2. STRUCTURAL INSOLVENCY (PONZI ARCHITECTURE):")
print("   Every 100 USDT deposited generates 300 USDT in promised liability.")
print("   Since 10 USDT is instantly extracted into 7 multi-level referral wallets,")
print("   only 90 USDT remains in the pool to pay off a 300 USDT liability.")
print("\n3. EXPONENTIAL COLLAPSE GUARANTEE:")
print("   To pay out existing investors, the system relies 100% on new participant deposits.")
print("   When new deposit growth slows down, withdrawals WILL freeze completely.")
print("=" * 70 + "\n")

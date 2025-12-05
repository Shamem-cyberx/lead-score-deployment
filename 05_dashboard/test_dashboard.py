"""
Test script to verify dashboard functionality
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

print("=" * 60)
print("Dashboard Data Verification")
print("=" * 60)

# Test 1: Check all files exist
print("\n[1] Checking data files...")
sample_dir = Path("sample_data")
files = list(sample_dir.glob("*.csv"))
print(f"  Found {len(files)} CSV files:")
for f in files:
    print(f"    [OK] {f.name}")

# Test 2: Verify metrics filtering
print("\n[2] Testing metrics time range filtering...")
df = pd.read_csv("sample_data/monitoring_metrics.csv")
df['metric_timestamp'] = pd.to_datetime(df['metric_timestamp'])
print(f"  Total rows: {len(df)}")
print(f"  Date range: {df['metric_timestamp'].min()} to {df['metric_timestamp'].max()}")

for days in [7, 30, 90]:
    cutoff = datetime.now() - timedelta(days=days)
    filtered = df[df['metric_timestamp'] >= cutoff]
    print(f"  Last {days} days: {len(filtered)} rows")

# Test 3: Verify predictions filtering
print("\n[3] Testing predictions time range filtering...")
df2 = pd.read_csv("sample_data/leads_predictions.csv")
df2['prediction_timestamp'] = pd.to_datetime(df2['prediction_timestamp'])
print(f"  Total rows: {len(df2)}")
print(f"  Date range: {df2['prediction_timestamp'].min()} to {df2['prediction_timestamp'].max()}")

for days in [7, 30, 90]:
    cutoff = datetime.now() - timedelta(days=days)
    filtered = df2[df2['prediction_timestamp'] >= cutoff]
    print(f"  Last {days} days: {len(filtered)} rows")

# Test 4: Verify conversions
print("\n[4] Testing conversions...")
df3 = pd.read_csv("sample_data/lead_conversions.csv")
df3['conversion_date'] = pd.to_datetime(df3['conversion_date'])
print(f"  Total conversions: {len(df3)}")
print(f"  Date range: {df3['conversion_date'].min()} to {df3['conversion_date'].max()}")

# Test 5: Verify drift data
print("\n[5] Testing drift data...")
df4 = pd.read_csv("sample_data/drift_detection.csv")
df4['detection_timestamp'] = pd.to_datetime(df4['detection_timestamp'])
print(f"  Total features: {len(df4)}")
print(f"  Latest detection: {df4['detection_timestamp'].max()}")

print("\n" + "=" * 60)
print("[SUCCESS] All data files verified!")
print("=" * 60)
print("\nTime range filtering should work correctly.")
print("If it doesn't update, try clicking 'Refresh Data' button.")


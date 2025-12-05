"""
Generate 1 year of realistic sample data for the dashboard
All dates are relative to today, going back 1 year
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Get today's date
TODAY = datetime.now()
ONE_YEAR_AGO = TODAY - timedelta(days=365)

print(f"Generating data from {ONE_YEAR_AGO.date()} to {TODAY.date()}")
print(f"Today's date: {TODAY.date()}\n")

# Create sample_data directory if it doesn't exist
SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"
SAMPLE_DATA_DIR.mkdir(exist_ok=True)

# 1. Generate monitoring_metrics.csv (daily metrics for 1 year)
print("Generating monitoring_metrics.csv...")
dates = pd.date_range(start=ONE_YEAR_AGO, end=TODAY, freq='D')
metrics_data = []

for i, date in enumerate(dates):
    # Add some realistic variation and trends
    base_latency = 100 + np.sin(i / 30) * 20  # Seasonal variation
    base_throughput = 15 + np.cos(i / 45) * 5
    base_conversion = 10 + np.sin(i / 60) * 3
    
    metrics_data.append({
        'metric_timestamp': date,
        'p50_latency_ms': int(base_latency + np.random.normal(0, 5)),
        'p95_latency_ms': int(base_latency * 1.8 + np.random.normal(0, 10)),
        'p99_latency_ms': int(base_latency * 2.5 + np.random.normal(0, 15)),
        'mean_latency_ms': int(base_latency * 1.2 + np.random.normal(0, 5)),
        'requests_per_second': round(base_throughput + np.random.normal(0, 2), 1),
        'conversion_rate': round(base_conversion + np.random.normal(0, 1), 1),
        'error_rate': round(0.2 + np.random.normal(0, 0.1), 2),
        'auc': round(0.85 + np.random.normal(0, 0.03), 2),
        'f1_score': round(0.75 + np.random.normal(0, 0.03), 2),
        'precision': round(0.80 + np.random.normal(0, 0.03), 2),
        'recall': round(0.70 + np.random.normal(0, 0.03), 2)
    })

metrics_df = pd.DataFrame(metrics_data)
metrics_df.to_csv(SAMPLE_DATA_DIR / "monitoring_metrics.csv", index=False)
print(f"  [OK] Created {len(metrics_df)} rows of metrics data")

# 2. Generate leads_predictions.csv (multiple leads per day)
print("Generating leads_predictions.csv...")
predictions_data = []
lead_id_counter = 1

# Generate leads over the past year (more recent = more leads)
for i in range(365):
    date = ONE_YEAR_AGO + timedelta(days=i)
    # More leads in recent days
    num_leads = int(10 + (i / 365) * 40 + np.random.poisson(5))
    
    for _ in range(num_leads):
        company_sizes = ['Small', 'Medium', 'Large']
        industries = ['Technology', 'Finance', 'Retail', 'Healthcare', 'Manufacturing']
        referral_sources = ['Google', 'LinkedIn', 'Direct', 'Email', 'Social Media']
        
        # Lead score based on engagement
        page_views = np.random.poisson(15)
        time_on_site = np.random.gamma(3, 100)
        form_time = np.random.gamma(2, 20)
        
        # Calculate realistic lead score
        engagement = (page_views * 0.1 + time_on_site / 100 + (60 - form_time) / 60) / 3
        lead_score = min(0.99, max(0.1, engagement + np.random.normal(0, 0.15)))
        
        predictions_data.append({
            'lead_id': f'lead_{lead_id_counter:06d}',
            'lead_score': round(lead_score, 3),
            'prediction_timestamp': date + timedelta(hours=np.random.randint(0, 24), 
                                                     minutes=np.random.randint(0, 60)),
            'company_size': np.random.choice(company_sizes),
            'industry': np.random.choice(industries),
            'page_views': page_views,
            'time_on_site': round(time_on_site, 1),
            'form_completion_time': round(form_time, 1),
            'referral_source': np.random.choice(referral_sources)
        })
        lead_id_counter += 1

predictions_df = pd.DataFrame(predictions_data)
predictions_df.to_csv(SAMPLE_DATA_DIR / "leads_predictions.csv", index=False)
print(f"  [OK] Created {len(predictions_df)} rows of predictions data")

# 3. Generate lead_conversions.csv (conversions from predictions)
print("Generating lead_conversions.csv...")
conversions_data = []

# Convert some leads (higher score = more likely to convert)
for _, lead in predictions_df.iterrows():
    # Conversion probability based on score
    conversion_prob = lead['lead_score'] * 0.3  # 30% of score becomes conversion rate
    if np.random.random() < conversion_prob:
        # Conversion happens 1-30 days after prediction
        conversion_date = lead['prediction_timestamp'] + timedelta(
            days=np.random.randint(1, 31),
            hours=np.random.randint(0, 24)
        )
        # Only include if conversion date is before today
        if conversion_date <= TODAY:
            conversions_data.append({
                'lead_id': lead['lead_id'],
                'conversion_date': conversion_date,
                'conversion_value': round(np.random.uniform(1000, 10000), 2),
                'conversion_type': np.random.choice(['Purchase', 'Subscription', 'Trial', 'Demo'])
            })

conversions_df = pd.DataFrame(conversions_data)
conversions_df.to_csv(SAMPLE_DATA_DIR / "lead_conversions.csv", index=False)
print(f"  [OK] Created {len(conversions_df)} rows of conversions data")

# 4. Generate drift_detection.csv (weekly drift checks for 1 year)
print("Generating drift_detection.csv...")
drift_data = []

features = [
    'company_size', 'industry', 'page_views', 'time_on_site',
    'form_completion_time', 'referral_source', 'hour_of_day',
    'day_of_week', 'engagement_score'
]

# Weekly drift detection for 1 year (52 weeks)
for week in range(52):
    detection_date = ONE_YEAR_AGO + timedelta(weeks=week)
    
    for feature in features:
        # PSI values increase over time (simulating drift)
        base_psi = 0.05 + (week / 52) * 0.2 + np.random.normal(0, 0.05)
        psi = max(0.01, min(0.6, base_psi))
        
        is_numerical = feature in ['page_views', 'time_on_site', 'form_completion_time', 
                                   'hour_of_day', 'day_of_week', 'engagement_score']
        
        drift_data.append({
            'feature_name': feature,
            'psi': round(psi, 3),
            'kl_divergence': round(psi * 0.5 + np.random.normal(0, 0.02), 3),
            'feature_type': 'numerical' if is_numerical else 'categorical',
            'detection_timestamp': detection_date,
            'ks_statistic': round(np.random.uniform(0.05, 0.25), 2) if is_numerical else 0.0,
            'ks_pvalue': round(np.random.uniform(0.01, 0.5), 3) if is_numerical else 1.0,
            'ks_drift_detected': psi > 0.25 if is_numerical else False,
            'chi2_statistic': round(np.random.uniform(5, 15), 1) if not is_numerical else 0.0,
            'chi2_pvalue': round(np.random.uniform(0.01, 0.1), 3) if not is_numerical else 1.0,
            'chi2_drift_detected': psi > 0.25 if not is_numerical else False,
            'baseline_mean': round(np.random.uniform(10, 20), 1) if is_numerical else 0.0,
            'current_mean': round(np.random.uniform(12, 22), 1) if is_numerical else 0.0,
            'baseline_std': round(np.random.uniform(5, 10), 1) if is_numerical else 0.0,
            'current_std': round(np.random.uniform(6, 11), 1) if is_numerical else 0.0
        })

drift_df = pd.DataFrame(drift_data)
drift_df.to_csv(SAMPLE_DATA_DIR / "drift_detection.csv", index=False)
print(f"  [OK] Created {len(drift_df)} rows of drift detection data")

print("\n" + "="*60)
print("[SUCCESS] Data Generation Complete!")
print("="*60)
print(f"\nSummary:")
print(f"  • Metrics: {len(metrics_df)} days ({ONE_YEAR_AGO.date()} to {TODAY.date()})")
print(f"  • Predictions: {len(predictions_df)} leads")
print(f"  • Conversions: {len(conversions_df)} conversions")
print(f"  • Drift Detection: {len(drift_df)} feature checks")
print(f"\nAll data files saved to: {SAMPLE_DATA_DIR}")
print(f"\nToday's date: {TODAY.date()}")
print("Dashboard will automatically use today's date for filtering!")


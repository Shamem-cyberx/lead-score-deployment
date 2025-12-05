"""
RAKEZ Lead Scoring Model - Plotly Dash Monitoring Dashboard
Fast, modern, open-source dashboard using Plotly Dash

Features:
- Real-time monitoring with fast updates
- Modern UI with Bootstrap styling
- Drift detection visualization
- Performance metrics
- Conversion rate tracking
- Alert log viewer
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json
import requests

# Import Ollama integration
try:
    from ollama_integration import ollama_client
    OLLAMA_AVAILABLE = ollama_client.available
except:
    OLLAMA_AVAILABLE = False
    ollama_client = None

# Initialize Dash app with modern styling
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

app.title = "RAKEZ Lead Scoring Dashboard"

# Configuration
SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"

# Cache for data loading (in-memory, fast)
_data_cache = {}
_cache_timestamps = {}

def load_data_from_csv(filename, days=30):
    """Load and filter data from CSV files - uses TODAY's date for filtering"""
    cache_key = f"{filename}_{days}"
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Today at midnight
    
    # Check cache (30 second TTL - reduced to ensure fresh data when time range changes)
    if cache_key in _data_cache:
        cache_time = _cache_timestamps.get(cache_key, datetime.min)
        if (datetime.now() - cache_time).seconds < 30:
            cached_df = _data_cache[cache_key]
            # Verify cached data matches requested days (safety check)
            if not cached_df.empty:
                return cached_df
    
    filepath = SAMPLE_DATA_DIR / filename
    if not filepath.exists():
        print(f"[WARN] File not found: {filepath}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(filepath)
        
        if df.empty:
            print(f"[WARN] {filename} is empty")
            return df
        
        # Determine timestamp column
        timestamp_cols = [col for col in df.columns if 'timestamp' in col.lower() or 'date' in col.lower()]
        
        if timestamp_cols:
            ts_col = timestamp_cols[0]
            df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
            
            # Filter using TODAY's date (always filter relative to today)
            max_date = df[ts_col].max()
            min_date = df[ts_col].min()
            
            if pd.notna(max_date) and pd.notna(min_date):
                # Calculate cutoff date from TODAY
                cutoff_date = today - timedelta(days=days)
                
                # Filter data
                df = df[df[ts_col] >= cutoff_date].copy()
                
                # Log what we loaded
                if len(df) > 0:
                    date_range = f"{df[ts_col].min().strftime('%Y-%m-%d')} to {df[ts_col].max().strftime('%Y-%m-%d')}"
                    print(f"[OK] Loaded {len(df)} rows from {filename} ({date_range}) | Today: {today.date()}, Filter: last {days} days")
                else:
                    print(f"[WARN] No data in {filename} for last {days} days (cutoff: {cutoff_date.date()}, data range: {min_date.date()} to {max_date.date()})")
            else:
                # No valid dates - return all data
                print(f"[WARN] No valid dates in {filename}, returning all {len(df)} rows")
        else:
            # No timestamp column - return all data
            print(f"[OK] Loaded all {len(df)} rows from {filename} (no date filtering)")
        
        # Cache the result
        _data_cache[cache_key] = df
        _cache_timestamps[cache_key] = datetime.now()
        
        return df
    except Exception as e:
        print(f"[ERROR] Error loading {filename}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def load_metrics_data(days=7):
    """Load monitoring metrics"""
    return load_data_from_csv("monitoring_metrics.csv", days)

def load_drift_data(days=30):
    """Load drift detection results"""
    return load_data_from_csv("drift_detection.csv", days)

def load_predictions_data(days=30):
    """Load predictions data"""
    return load_data_from_csv("leads_predictions.csv", days)

def load_conversions_data(days=30):
    """Load conversions data"""
    return load_data_from_csv("lead_conversions.csv", days)

def clear_cache():
    """Clear data cache"""
    global _data_cache, _cache_timestamps
    _data_cache = {}
    _cache_timestamps = {}

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1([
                html.I(className="fas fa-chart-line me-2"),
                "RAKEZ Lead Scoring Model - Monitoring Dashboard"
            ], className="text-white mb-0"),
            html.P("Real-time monitoring and analytics", className="text-white-50 mb-0")
        ], className="col"),
        html.Div([
            html.Button([
                html.I(className="fas fa-sync-alt me-2"),
                "Refresh"
            ], id="refresh-btn", className="btn btn-light btn-sm", n_clicks=0)
        ], className="col-auto")
    ], className="row align-items-center bg-primary p-3 rounded mb-3"),
    
    # Filters
    html.Div([
        html.Div([
            html.Label("Time Range", className="form-label fw-bold"),
            dcc.Dropdown(
                id="time-range-dropdown",
                options=[
                    {"label": "Last 7 days", "value": 7},
                    {"label": "Last 30 days", "value": 30},
                    {"label": "Last 90 days", "value": 90}
                ],
                value=7,
                clearable=False,
                className="mb-3"
            )
        ], className="col-md-3"),
        html.Div([
            html.Label("Active Filter", className="form-label fw-bold"),
            html.Div(id="active-filter-display", className="p-2 bg-light rounded")
        ], className="col-md-9")
    ], className="row mb-4", id="filters-row"),
    
    # Standalone demo mode indicator
    html.Div([
        html.I(className="fas fa-info-circle text-primary me-2"),
        html.Strong("Standalone Demo Dashboard"),
        html.Span(" - This dashboard works independently using sample CSV data. Backend API is optional.", 
                 className="ms-2 text-muted")
    ], className="alert alert-info mb-3 py-2"),
    
    # Status indicator
    html.Div(id="status-indicator", className="mb-3"),
    
    # Backend status (optional - shown for info only)
    html.Div(id="backend-status", className="mb-2"),
    
    # Tabs
    dcc.Tabs(id="main-tabs", value="overview", children=[
        dcc.Tab(label="📈 Overview", value="overview", className="tab-style"),
        dcc.Tab(label="🔍 Drift Detection", value="drift", className="tab-style"),
        dcc.Tab(label="⚡ Performance", value="performance", className="tab-style"),
        dcc.Tab(label="💰 Business Metrics", value="business", className="tab-style"),
        dcc.Tab(label="🔬 Model Explainability", value="explainability", className="tab-style"),
        dcc.Tab(label="🚨 Alerts", value="alerts", className="tab-style"),
        dcc.Tab(label="🤖 AI Insights", value="ai", className="tab-style"),
    ], className="mb-3"),
    
    # Content area
    html.Div(id="tab-content", className="mt-3"),
    
    # Hidden div for refresh trigger
    html.Div(id="refresh-trigger", style={"display": "none"})
], className="container-fluid p-4")

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
            }
            .tab-style {
                font-weight: 500;
                padding: 10px 20px;
            }
            .metric-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #2c3e50;
            }
            .metric-label {
                color: #7f8c8d;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .delta-positive {
                color: #27ae60;
            }
            .delta-negative {
                color: #e74c3c;
            }
            .loading-spinner {
                text-align: center;
                padding: 40px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callbacks
@app.callback(
    [Output("refresh-trigger", "children"),
     Output("status-indicator", "children"),
     Output("backend-status", "children")],
    [Input("refresh-btn", "n_clicks"),
     Input("time-range-dropdown", "value")]
)
def handle_refresh(refresh_clicks, days):
    """Handle refresh and update status with data verification"""
    clear_cache()
    
    # Check backend status
    backend_status = check_backend_status()
    
    # Check if sample data exists and load to verify
    metrics_file = SAMPLE_DATA_DIR / "monitoring_metrics.csv"
    has_data = metrics_file.exists()
    
    if has_data:
        # Try to load data to verify it works
        try:
            test_df = load_metrics_data(days)
            row_count = len(test_df)
            
            if row_count > 0:
                status = html.Div([
                    html.I(className="fas fa-check-circle text-success me-2"),
                    html.Span(
                        f"Loaded {row_count} rows from sample data | Filter: Last {days} days | Today: {datetime.now().strftime('%Y-%m-%d')}",
                        className="text-success"
                    )
                ], className="alert alert-success mb-0")
            else:
                status = html.Div([
                    html.I(className="fas fa-exclamation-triangle text-warning me-2"),
                    html.Span(
                        f"Data file exists but no rows match filter (Last {days} days). Try a longer time range.",
                        className="text-warning"
                    )
                ], className="alert alert-warning mb-0")
        except Exception as e:
            status = html.Div([
                html.I(className="fas fa-times-circle text-danger me-2"),
                html.Span(f"Error loading data: {str(e)}", className="text-danger")
            ], className="alert alert-danger mb-0")
    else:
        status = html.Div([
            html.I(className="fas fa-exclamation-triangle text-warning me-2"),
            html.Span("No sample data found. Add CSV files to sample_data/ folder", className="text-warning")
        ], className="alert alert-warning mb-0")
    
    return str(refresh_clicks), status, backend_status

def check_backend_status():
    """Check if FastAPI backend is running (optional - dashboard works standalone)"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            return html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                html.Span("Backend API is running (optional)", className="text-success")
            ], className="alert alert-success mb-0 py-2")
        else:
            return html.Div([
                html.I(className="fas fa-info-circle text-info me-2"),
                html.Span("Backend API status unknown (dashboard works standalone)", className="text-info")
            ], className="alert alert-info mb-0 py-2")
    except:
        return html.Div([
            html.I(className="fas fa-info-circle text-info me-2"),
            html.Span("Standalone Demo Mode - Dashboard works without backend. Data loaded from CSV files.", className="text-info")
        ], className="alert alert-info mb-0 py-2")

@app.callback(
    Output("active-filter-display", "children"),
    Input("time-range-dropdown", "value")
)
def update_filter_display(days):
    """Update active filter display"""
    return html.Span([
        html.I(className="fas fa-filter me-2"),
        f"Showing data from last {days} days"
    ], className="text-muted")

@app.callback(
    Output("tab-content", "children"),
    [Input("main-tabs", "value"),
     Input("time-range-dropdown", "value"),
     Input("refresh-trigger", "children")]
)
def update_tab_content(active_tab, days, refresh_trigger):
    """Update content based on active tab - clears cache when time range changes"""
    # Clear cache when time range changes (cache key includes days, but clear to be safe)
    # The cache will be rebuilt with new days parameter automatically
    clear_cache()
    
    if active_tab == "overview":
        return render_overview_tab(days)
    elif active_tab == "drift":
        return render_drift_tab(days)
    elif active_tab == "performance":
        return render_performance_tab(days)
    elif active_tab == "business":
        return render_business_tab(days)
    elif active_tab == "explainability":
        return render_explainability_tab()
    elif active_tab == "alerts":
        return render_alerts_tab(days)
    elif active_tab == "ai":
        return render_ai_tab(days)
    return html.Div("Select a tab")

def render_overview_tab(days):
    """Render overview tab"""
    metrics_df = load_metrics_data(days)
    
    if metrics_df.empty:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"No metrics data available for last {days} days. ",
                html.A("Try a longer time range", href="#", className="alert-link")
            ], className="alert alert-warning"),
            html.Div([
                html.H5("Debug Info:"),
                html.P(f"Time range: Last {days} days"),
                html.P(f"Current date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                html.P(f"Sample data directory: {SAMPLE_DATA_DIR}"),
                html.P(f"File exists: {(SAMPLE_DATA_DIR / 'monitoring_metrics.csv').exists()}")
            ], className="mt-3 p-3 bg-light rounded")
        ])
    
    # Advanced metrics calculation - aggregate over time range for accurate, changing values
    if len(metrics_df) == 0:
        latest = {}
        avg_metrics = {}
        trend_metrics = {}
    else:
        latest = metrics_df.iloc[-1].to_dict()
        
        # Calculate aggregated metrics over the time range (this makes values change!)
        avg_metrics = {
            'p95_latency_ms': float(metrics_df['p95_latency_ms'].mean()) if 'p95_latency_ms' in metrics_df.columns else 0,
            'p50_latency_ms': float(metrics_df['p50_latency_ms'].mean()) if 'p50_latency_ms' in metrics_df.columns else 0,
            'p99_latency_ms': float(metrics_df['p99_latency_ms'].mean()) if 'p99_latency_ms' in metrics_df.columns else 0,
            'requests_per_second': float(metrics_df['requests_per_second'].mean()) if 'requests_per_second' in metrics_df.columns else 0,
            'conversion_rate': float(metrics_df['conversion_rate'].mean()) if 'conversion_rate' in metrics_df.columns else 0,
            'error_rate': float(metrics_df['error_rate'].mean()) if 'error_rate' in metrics_df.columns else 0,
        }
        
        # Calculate trends (comparing first half vs second half of time range)
        if len(metrics_df) > 1:
            mid_point = len(metrics_df) // 2
            first_half = metrics_df.iloc[:mid_point]
            second_half = metrics_df.iloc[mid_point:]
            
            trend_metrics = {
                'latency_trend': float(second_half['p95_latency_ms'].mean()) - float(first_half['p95_latency_ms'].mean()) if 'p95_latency_ms' in metrics_df.columns else 0,
                'throughput_trend': float(second_half['requests_per_second'].mean()) - float(first_half['requests_per_second'].mean()) if 'requests_per_second' in metrics_df.columns else 0,
                'conversion_trend': float(second_half['conversion_rate'].mean()) - float(first_half['conversion_rate'].mean()) if 'conversion_rate' in metrics_df.columns else 0,
                'error_trend': float(second_half['error_rate'].mean()) - float(first_half['error_rate'].mean()) if 'error_rate' in metrics_df.columns else 0,
            }
        else:
            trend_metrics = {'latency_trend': 0, 'throughput_trend': 0, 'conversion_trend': 0, 'error_trend': 0}
    
    # Add data info with statistics
    data_info = ""
    if 'metric_timestamp' in metrics_df.columns and len(metrics_df) > 0:
        date_range = f"{metrics_df['metric_timestamp'].min().strftime('%Y-%m-%d')} to {metrics_df['metric_timestamp'].max().strftime('%Y-%m-%d')}"
        data_info = html.Div([
            html.Small([
                html.I(className="fas fa-info-circle me-1"),
                f"Showing {len(metrics_df)} data points ({date_range}) | ",
                html.Strong("Metrics show averages over this period"),
                html.I(className="fas fa-chart-line ms-2 me-1"),
                "Trends calculated from period comparison"
            ], className="text-muted")
        ], className="mb-2")
    
    # Calculate deltas using AVERAGE values (changes with time range!)
    latency_avg = avg_metrics.get('p95_latency_ms', 0)
    latency_delta = latency_avg - 200
    latency_trend = trend_metrics.get('latency_trend', 0)
    
    throughput_avg = avg_metrics.get('requests_per_second', 0)
    throughput_delta = throughput_avg - 10
    throughput_trend = trend_metrics.get('throughput_trend', 0)
    
    conversion_avg = avg_metrics.get('conversion_rate', 0)
    conversion_delta = conversion_avg - 5
    conversion_trend = trend_metrics.get('conversion_trend', 0)
    
    error_avg = avg_metrics.get('error_rate', 0)
    error_delta = error_avg - 1
    error_trend = trend_metrics.get('error_trend', 0)
    
    # Build range info safely
    latency_range_info = html.Div() if metrics_df.empty or 'p95_latency_ms' not in metrics_df.columns else html.Div([
        html.Small([
            f"Range: {float(metrics_df['p95_latency_ms'].min()):.0f}-{float(metrics_df['p95_latency_ms'].max()):.0f} ms"
        ], className="text-muted")
    ], className="mt-1")
    
    throughput_range_info = html.Div() if metrics_df.empty or 'requests_per_second' not in metrics_df.columns else html.Div([
        html.Small([
            f"Range: {float(metrics_df['requests_per_second'].min()):.1f}-{float(metrics_df['requests_per_second'].max()):.1f} req/s"
        ], className="text-muted")
    ], className="mt-1")
    
    conversion_range_info = html.Div() if metrics_df.empty or 'conversion_rate' not in metrics_df.columns else html.Div([
        html.Small([
            f"Range: {float(metrics_df['conversion_rate'].min()):.2f}-{float(metrics_df['conversion_rate'].max()):.2f}%"
        ], className="text-muted")
    ], className="mt-1")
    
    error_range_info = html.Div() if metrics_df.empty or 'error_rate' not in metrics_df.columns else html.Div([
        html.Small([
            f"Range: {float(metrics_df['error_rate'].min()):.2f}-{float(metrics_df['error_rate'].max()):.2f}%"
        ], className="text-muted")
    ], className="mt-1")
    
    return html.Div([
        data_info,
        # Metrics cards
        html.Div([
            html.Div([
                html.Div([
                    html.Div("Latency (P95 Avg)", className="metric-label"),
                    html.Div(f"{latency_avg:.0f} ms", className="metric-value"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if latency_delta > 0 else 'down'} me-1"),
                        f"{latency_delta:+.0f} ms vs target"
                    ], className=f"small {'delta-positive' if latency_delta < 0 else 'delta-negative'}"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if latency_trend > 0 else 'down'} me-1"),
                        html.Span(f"Trend: {latency_trend:+.0f} ms", className="text-muted")
                    ], className="small mt-1") if len(metrics_df) > 1 else html.Div(),
                    latency_range_info
                ], className="metric-card")
            ], className="col-md-3"),
            html.Div([
                html.Div([
                    html.Div("Throughput (Avg)", className="metric-label"),
                    html.Div(f"{throughput_avg:.1f} req/s", className="metric-value"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if throughput_delta > 0 else 'down'} me-1"),
                        f"{throughput_delta:+.1f} vs min"
                    ], className=f"small {'delta-positive' if throughput_delta > 0 else 'delta-negative'}"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if throughput_trend > 0 else 'down'} me-1"),
                        html.Span(f"Trend: {throughput_trend:+.1f} req/s", className="text-muted")
                    ], className="small mt-1"),
                    throughput_range_info
                ], className="metric-card")
            ], className="col-md-3"),
            html.Div([
                html.Div([
                    html.Div("Conversion Rate (Avg)", className="metric-label"),
                    html.Div(f"{conversion_avg:.2f}%", className="metric-value"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if conversion_delta > 0 else 'down'} me-1"),
                        f"{conversion_delta:+.2f}% vs baseline"
                    ], className=f"small {'delta-positive' if conversion_delta > 0 else 'delta-negative'}"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if conversion_trend > 0 else 'down'} me-1"),
                        html.Span(f"Trend: {conversion_trend:+.2f}%", className="text-muted")
                    ], className="small mt-1") if len(metrics_df) > 1 else html.Div(),
                    conversion_range_info
                ], className="metric-card")
            ], className="col-md-3"),
            html.Div([
                html.Div([
                    html.Div("Error Rate (Avg)", className="metric-label"),
                    html.Div(f"{error_avg:.2f}%", className="metric-value"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if error_delta > 0 else 'down'} me-1"),
                        f"{error_delta:+.2f}% vs threshold"
                    ], className=f"small {'delta-positive' if error_delta < 0 else 'delta-negative'}"),
                    html.Div([
                        html.I(className=f"fas fa-arrow-{'up' if error_trend > 0 else 'down'} me-1"),
                        html.Span(f"Trend: {error_trend:+.2f}%", className="text-muted")
                    ], className="small mt-1") if len(metrics_df) > 1 else html.Div(),
                    error_range_info
                ], className="metric-card")
            ], className="col-md-3")
        ], className="row mb-4"),
        
        # Performance chart
        html.Div([
            html.H4("Model Performance Over Time", className="mb-3"),
            dcc.Graph(
                figure=create_performance_chart(metrics_df),
                config={'displayModeBar': True, 'responsive': True}
            )
        ], className="metric-card")
    ])

def render_drift_tab(days):
    """Render drift detection tab"""
    drift_df = load_drift_data(days)
    
    if drift_df.empty:
        return html.Div([
            html.Div("No drift detection data available", className="alert alert-warning")
        ])
    
    if 'psi' in drift_df.columns and 'feature_name' in drift_df.columns:
        latest_drift = drift_df.groupby('feature_name')['psi'].last().reset_index()
        latest_drift = latest_drift.sort_values('psi', ascending=False)
        latest_drift['status'] = latest_drift['psi'].apply(
            lambda x: 'Critical' if x > 0.5 else ('Warning' if x > 0.25 else 'Normal')
        )
        
        return html.Div([
            html.Div([
                html.H4("PSI (Population Stability Index) by Feature", className="mb-3"),
                dcc.Graph(
                    figure=create_psi_chart(latest_drift),
                    config={'displayModeBar': True, 'responsive': True}
                )
            ], className="metric-card mb-4"),
            html.Div([
                html.H4("Drift Detection Details", className="mb-3"),
                dash_table.DataTable(
                    data=latest_drift[['feature_name', 'psi', 'status']].to_dict('records'),
                    columns=[
                        {"name": "Feature", "id": "feature_name"},
                        {"name": "PSI", "id": "psi", "type": "numeric", "format": {"specifier": ".3f"}},
                        {"name": "Status", "id": "status"}
                    ],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{status} = Critical'},
                            'backgroundColor': '#fee',
                            'color': '#c00'
                        },
                        {
                            'if': {'filter_query': '{status} = Warning'},
                            'backgroundColor': '#ffeaa7',
                            'color': '#d63031'
                        }
                    ],
                    page_size=10
                )
            ], className="metric-card")
        ])
    
    return html.Div("Drift data structure incomplete", className="alert alert-warning")

def render_performance_tab(days):
    """Render performance metrics tab"""
    metrics_df = load_metrics_data(days)
    
    if metrics_df.empty:
        return html.Div([
            html.Div("No performance metrics available", className="alert alert-warning")
        ])
    
    return html.Div([
        html.Div([
            html.H4("Latency Over Time", className="mb-3"),
            dcc.Graph(
                figure=create_latency_chart(metrics_df),
                config={'displayModeBar': True, 'responsive': True}
            )
        ], className="metric-card mb-4"),
        html.Div([
            html.H4("Throughput Over Time", className="mb-3"),
            dcc.Graph(
                figure=create_throughput_chart(metrics_df),
                config={'displayModeBar': True, 'responsive': True}
            )
        ], className="metric-card")
    ])

def render_business_tab(days):
    """Render business metrics tab"""
    predictions_df = load_predictions_data(days)
    conversions_df = load_conversions_data(days)
    
    if predictions_df.empty:
        return html.Div([
            html.Div("No business metrics data available", className="alert alert-warning")
        ])
    
    return html.Div([
        html.Div([
            html.H4("Conversion Rate by Score Bucket", className="mb-3"),
            dcc.Graph(
                figure=create_conversion_chart(predictions_df, conversions_df),
                config={'displayModeBar': True, 'responsive': True}
            )
        ], className="metric-card mb-4"),
        html.Div([
            html.H4("Lead Score Distribution", className="mb-3"),
            dcc.Graph(
                figure=create_score_distribution_chart(predictions_df),
                config={'displayModeBar': True, 'responsive': True}
            )
        ], className="metric-card")
    ])

def render_alerts_tab(days):
    """Render alerts tab"""
    drift_df = load_drift_data(days)
    
    alerts = []
    if not drift_df.empty and 'psi' in drift_df.columns:
        critical = drift_df[drift_df['psi'] > 0.5]
        warnings = drift_df[(drift_df['psi'] > 0.25) & (drift_df['psi'] <= 0.5)]
        
        for _, row in critical.iterrows():
            alerts.append({
                "type": "Critical",
                "feature": row.get('feature_name', 'Unknown'),
                "psi": row.get('psi', 0),
                "message": f"Critical drift detected in {row.get('feature_name', 'Unknown')}"
            })
        
        for _, row in warnings.iterrows():
            alerts.append({
                "type": "Warning",
                "feature": row.get('feature_name', 'Unknown'),
                "psi": row.get('psi', 0),
                "message": f"Warning: Drift detected in {row.get('feature_name', 'Unknown')}"
            })
    
    if not alerts:
        return html.Div([
            html.Div([
                html.I(className="fas fa-check-circle text-success me-2"),
                "No alerts - All systems normal"
            ], className="alert alert-success")
        ])
    
    alert_cards = []
    for alert in alerts:
        alert_class = "alert-danger" if alert["type"] == "Critical" else "alert-warning"
        icon = "fas fa-exclamation-circle" if alert["type"] == "Critical" else "fas fa-exclamation-triangle"
        alert_cards.append(
            html.Div([
                html.I(className=f"{icon} me-2"),
                html.Strong(alert["type"]), f": {alert['message']} (PSI: {alert['psi']:.3f})"
            ], className=f"alert {alert_class} mb-2")
        )
    
    return html.Div(alert_cards)

def render_explainability_tab():
    """Render Model Explainability tab with SHAP/LIME integration"""
    API_URL = "http://127.0.0.1:8000"
    
    # Check if backend is available
    backend_available = check_backend_status()
    
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-microscope me-2"),
                "Model Explainability - SHAP & LIME"
            ], className="mb-4"),
            html.P("Understand how the model makes predictions by analyzing feature contributions.", 
                  className="text-muted mb-4")
        ], className="mb-4"),
        
        # Backend status
        html.Div([
            html.I(className=f"fas fa-{'check-circle' if backend_available else 'exclamation-triangle'} me-2"),
            html.Span(
                "Backend API is running" if backend_available else "Backend API is not running. Start the FastAPI server to use explainability features.",
                className="text-success" if backend_available else "text-warning"
            )
        ], className=f"alert {'alert-success' if backend_available else 'alert-warning'} mb-4"),
        
        # Input form
        html.Div([
            html.H4("Enter Lead Information", className="mb-3"),
            html.Div([
                html.Div([
                    html.Label("Lead ID", className="form-label"),
                    dcc.Input(
                        id="explain-lead-id",
                        type="text",
                        value="test_lead_001",
                        className="form-control",
                        placeholder="Enter lead ID"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Company Size", className="form-label"),
                    dcc.Dropdown(
                        id="explain-company-size",
                        options=[
                            {"label": "Small", "value": "Small"},
                            {"label": "Medium", "value": "Medium"},
                            {"label": "Large", "value": "Large"},
                            {"label": "Enterprise", "value": "Enterprise"}
                        ],
                        value="Medium",
                        className="form-select"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Industry", className="form-label"),
                    dcc.Dropdown(
                        id="explain-industry",
                        options=[
                            {"label": "Technology", "value": "Technology"},
                            {"label": "Finance", "value": "Finance"},
                            {"label": "Healthcare", "value": "Healthcare"},
                            {"label": "Retail", "value": "Retail"},
                            {"label": "Manufacturing", "value": "Manufacturing"},
                            {"label": "Education", "value": "Education"}
                        ],
                        value="Technology",
                        className="form-select"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Page Views", className="form-label"),
                    dcc.Input(
                        id="explain-page-views",
                        type="number",
                        value=15,
                        min=0,
                        className="form-control"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Time on Site (seconds)", className="form-label"),
                    dcc.Input(
                        id="explain-time-on-site",
                        type="number",
                        value=450.5,
                        min=0,
                        step=0.1,
                        className="form-control"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Form Completion Time (seconds)", className="form-label"),
                    dcc.Input(
                        id="explain-form-time",
                        type="number",
                        value=120.0,
                        min=0,
                        step=0.1,
                        className="form-control"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Referral Source", className="form-label"),
                    dcc.Dropdown(
                        id="explain-referral",
                        options=[
                            {"label": "Organic Search", "value": "Organic Search"},
                            {"label": "Paid Search", "value": "Paid Search"},
                            {"label": "Social Media", "value": "Social Media"},
                            {"label": "Direct", "value": "Direct"},
                            {"label": "Referral", "value": "Referral"},
                            {"label": "Email", "value": "Email"}
                        ],
                        value="Organic Search",
                        className="form-select"
                    )
                ], className="mb-3"),
                
                html.Div([
                    html.Label("Explanation Method", className="form-label"),
                    dcc.RadioItems(
                        id="explain-method",
                        options=[
                            {"label": " 🔬 SHAP", "value": "shap"},
                            {"label": " 🔍 LIME", "value": "lime"}
                        ],
                        value="shap",
                        className="form-check"
                    )
                ], className="mb-3"),
                
                html.Button([
                    html.I(className="fas fa-calculator me-2"),
                    "Generate Explanation"
                ], id="explain-btn", className="btn btn-primary btn-lg w-100", n_clicks=0)
            ], className="metric-card")
        ], className="row mb-4"),
        
        # Results area
        html.Div(id="explain-results", className="mt-4")
        
    ])

@app.callback(
    Output("explain-results", "children"),
    [Input("explain-btn", "n_clicks")],
    [State("explain-lead-id", "value"),
     State("explain-company-size", "value"),
     State("explain-industry", "value"),
     State("explain-page-views", "value"),
     State("explain-time-on-site", "value"),
     State("explain-form-time", "value"),
     State("explain-referral", "value"),
     State("explain-method", "value")]
)
def generate_explanation(n_clicks, lead_id, company_size, industry, page_views, 
                         time_on_site, form_time, referral, method):
    """Generate explanation from API"""
    if n_clicks == 0:
        return html.Div([
            html.Div([
                html.I(className="fas fa-info-circle me-2"),
                "Fill in the form above and click 'Generate Explanation' to see how the model makes predictions."
            ], className="alert alert-info")
        ])
    
    API_URL = "http://127.0.0.1:8000"
    
    # Prepare request data
    test_data = {
        "lead_id": lead_id or "test_001",
        "company_size": company_size or "Medium",
        "industry": industry or "Technology",
        "page_views": page_views or 15,
        "time_on_site": time_on_site or 450.5,
        "form_completion_time": form_time or 120.0,
        "referral_source": referral or "Organic Search",
        "created_at": datetime.now().isoformat()
    }
    
    try:
        # Call explainability API
        response = requests.post(
            f"{API_URL}/explain-prediction?method={method or 'shap'}",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract data
            prediction = result.get('prediction', 0)
            explanation_method = result.get('explanation_method', 'SHAP')
            feature_contributions = result.get('feature_contributions', {})
            base_value = result.get('base_value', 0.5)
            
            # Sort features by absolute contribution
            sorted_features = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            # Create feature contribution chart
            features = [f[0] for f in sorted_features]
            contributions = [f[1] for f in sorted_features]
            colors = ['#2ecc71' if c >= 0 else '#e74c3c' for c in contributions]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=features,
                    y=contributions,
                    marker_color=colors,
                    text=[f"{c:+.4f}" for c in contributions],
                    textposition='outside',
                    name='Contribution'
                )
            ])
            fig.update_layout(
                title=f"Feature Contributions ({explanation_method})",
                xaxis_title="Feature",
                yaxis_title="Contribution",
                height=500,
                template='plotly_white',
                xaxis={'tickangle': -45}
            )
            
            return html.Div([
                # Prediction summary
                html.Div([
                    html.H4("Prediction Summary", className="mb-3"),
                    html.Div([
                        html.Div([
                            html.Div("Prediction Score", className="metric-label"),
                            html.Div(f"{prediction:.4f}", className="metric-value"),
                            html.Div(f"({prediction*100:.2f}% conversion probability)", 
                                   className="text-muted small")
                        ], className="col-md-4"),
                        html.Div([
                            html.Div("Explanation Method", className="metric-label"),
                            html.Div(explanation_method, className="metric-value"),
                            html.Div("Method used for explanation", className="text-muted small")
                        ], className="col-md-4"),
                        html.Div([
                            html.Div("Base Value", className="metric-label"),
                            html.Div(f"{base_value:.4f}", className="metric-value"),
                            html.Div("Baseline prediction", className="text-muted small")
                        ], className="col-md-4")
                    ], className="row")
                ], className="metric-card mb-4"),
                
                # Feature contributions chart
                html.Div([
                    html.H4("Feature Contributions", className="mb-3"),
                    html.P("Positive values increase the prediction, negative values decrease it.", 
                          className="text-muted mb-3"),
                    dcc.Graph(figure=fig, config={'displayModeBar': True, 'responsive': True})
                ], className="metric-card mb-4"),
                
                # Feature contributions table
                html.Div([
                    html.H4("Detailed Feature Contributions", className="mb-3"),
                    dash_table.DataTable(
                        id="explain-table",
                        columns=[
                            {"name": "Feature", "id": "feature"},
                            {"name": "Contribution", "id": "contribution", "type": "numeric", "format": {"specifier": ".4f"}},
                            {"name": "Impact", "id": "impact"}
                        ],
                        data=[
                            {
                                "feature": feature,
                                "contribution": f"{contrib:.4f}",
                                "impact": "Increases prediction" if contrib > 0 else "Decreases prediction" if contrib < 0 else "Neutral"
                            }
                            for feature, contrib in sorted_features
                        ],
                        style_cell={'textAlign': 'left', 'padding': '10px'},
                        style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'},
                        style_data_conditional=[
                            {
                                'if': {'filter_query': '{contribution} > 0'},
                                'backgroundColor': '#d4edda',
                                'color': '#155724'
                            },
                            {
                                'if': {'filter_query': '{contribution} < 0'},
                                'backgroundColor': '#f8d7da',
                                'color': '#721c24'
                            }
                        ]
                    )
                ], className="metric-card")
            ])
            
        elif response.status_code == 503:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Model not loaded. Please start the FastAPI server and register a model.",
                    html.Br(),
                    html.Small("Run: python create_dummy_model.py", className="text-muted")
                ], className="alert alert-warning")
            ])
        else:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-times-circle me-2"),
                    f"Error: {response.status_code}",
                    html.Br(),
                    html.Small(response.text, className="text-muted")
                ], className="alert alert-danger")
            ])
            
    except requests.exceptions.ConnectionError:
        return html.Div([
            html.Div([
                html.I(className="fas fa-unlink me-2"),
                "Cannot connect to API. Make sure the FastAPI server is running on http://127.0.0.1:8000",
                html.Br(),
                html.Small("Start server: python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000", 
                          className="text-muted")
            ], className="alert alert-danger")
        ])
    except Exception as e:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Error: {str(e)}"
            ], className="alert alert-danger")
        ])

def render_ai_tab(days):
    """Render AI Insights tab with Ollama integration"""
    metrics_df = load_metrics_data(days)
    predictions_df = load_predictions_data(days)
    drift_df = load_drift_data(days)
    
    # Check Ollama availability
    ollama_status = html.Div([
        html.I(className="fas fa-robot me-2"),
        html.Span("Ollama AI is available" if OLLAMA_AVAILABLE else "Ollama AI is not available. Install Ollama to enable AI features.", 
                 className="text-success" if OLLAMA_AVAILABLE else "text-warning")
    ], className=f"alert {'alert-success' if OLLAMA_AVAILABLE else 'alert-warning'} mb-3")
    
    if not OLLAMA_AVAILABLE:
        return html.Div([
            ollama_status,
            html.Div([
                html.H4("Install Ollama for AI Features", className="mb-3"),
                html.P("Ollama provides AI-powered insights, anomaly detection, and natural language queries."),
                html.Hr(),
                html.H5("Installation Steps:"),
                html.Ol([
                    html.Li("Download Ollama from https://ollama.ai"),
                    html.Li("Install and start Ollama"),
                    html.Li("Pull a model: ollama pull llama3.2"),
                    html.Li("Refresh this page")
                ])
            ], className="metric-card")
        ])
    
    # Generate insights
    insights = []
    
    if not metrics_df.empty and ollama_client:
        # Performance recommendations
        try:
            recommendations = ollama_client.generate_recommendations(metrics_df, predictions_df)
            insights.append(html.Div([
                html.H4("Performance Recommendations", className="mb-3"),
                html.Div(recommendations, className="p-3 bg-light rounded")
            ], className="metric-card mb-3"))
        except Exception as e:
            insights.append(html.Div([
                html.H4("Performance Recommendations", className="mb-3"),
                html.Div(f"Error generating recommendations: {str(e)}", className="p-3 bg-light rounded text-danger")
            ], className="metric-card mb-3"))
        
        # Drift analysis
        if not drift_df.empty:
            try:
                drift_explanation = ollama_client.explain_drift(drift_df)
                insights.append(html.Div([
                    html.H4("Data Drift Analysis", className="mb-3"),
                    html.Div(drift_explanation, className="p-3 bg-light rounded")
                ], className="metric-card mb-3"))
            except Exception as e:
                insights.append(html.Div([
                    html.H4("Data Drift Analysis", className="mb-3"),
                    html.Div(f"Error analyzing drift: {str(e)}", className="p-3 bg-light rounded text-danger")
                ], className="metric-card mb-3"))
    
    if not insights:
        insights.append(html.Div([
            html.H4("No Insights Available", className="mb-3"),
            html.P("Load data to generate AI insights.")
        ], className="metric-card"))
    
    return html.Div([
        ollama_status,
        html.Div(insights)
    ])

# Chart creation functions
def create_performance_chart(df):
    """Create model performance chart"""
    if df.empty or 'metric_timestamp' not in df.columns:
        return go.Figure()
    
    df['metric_timestamp'] = pd.to_datetime(df['metric_timestamp'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['metric_timestamp'],
        y=df.get('auc', 0),
        mode='lines+markers',
        name='AUC',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df['metric_timestamp'],
        y=df.get('f1_score', 0),
        mode='lines+markers',
        name='F1 Score',
        line=dict(color='#ff7f0e', width=2)
    ))
    fig.update_layout(
        title="Model Performance Metrics",
        xaxis_title="Date",
        yaxis_title="Score",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    return fig

def create_psi_chart(df):
    """Create PSI bar chart"""
    if df.empty:
        return go.Figure()
    
    colors = df['status'].map({
        'Normal': '#2ecc71',
        'Warning': '#f39c12',
        'Critical': '#e74c3c'
    })
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['feature_name'],
            y=df['psi'],
            marker_color=colors,
            text=df['psi'].round(3),
            textposition='outside'
        )
    ])
    fig.add_hline(y=0.25, line_dash="dash", line_color="orange", annotation_text="Warning")
    fig.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="Critical")
    fig.update_layout(
        title="PSI by Feature",
        xaxis_title="Feature",
        yaxis_title="PSI Value",
        height=500,
        template='plotly_white'
    )
    return fig

def create_latency_chart(df):
    """Create latency chart"""
    if df.empty or 'metric_timestamp' not in df.columns:
        return go.Figure()
    
    df['metric_timestamp'] = pd.to_datetime(df['metric_timestamp'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['metric_timestamp'], y=df.get('p50_latency_ms', 0), name='P50', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df['metric_timestamp'], y=df.get('p95_latency_ms', 0), name='P95', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df['metric_timestamp'], y=df.get('p99_latency_ms', 0), name='P99', line=dict(color='red')))
    fig.add_hline(y=200, line_dash="dash", line_color="orange", annotation_text="Warning (200ms)")
    fig.add_hline(y=500, line_dash="dash", line_color="red", annotation_text="Critical (500ms)")
    fig.update_layout(title="Latency Percentiles", xaxis_title="Time", yaxis_title="Latency (ms)", height=400, template='plotly_white')
    return fig

def create_throughput_chart(df):
    """Create throughput chart"""
    if df.empty or 'metric_timestamp' not in df.columns:
        return go.Figure()
    
    df['metric_timestamp'] = pd.to_datetime(df['metric_timestamp'])
    fig = px.line(df, x='metric_timestamp', y='requests_per_second', title="Requests per Second")
    fig.add_hline(y=10, line_dash="dash", line_color="orange", annotation_text="Minimum")
    fig.update_layout(height=300, template='plotly_white')
    return fig

def create_conversion_chart(predictions_df, conversions_df):
    """Create conversion rate chart"""
    if predictions_df.empty:
        return go.Figure()
    
    predictions_df['score_bucket'] = pd.cut(
        predictions_df['lead_score'],
        bins=[0, 0.3, 0.5, 0.7, 1.0],
        labels=['Low (0-0.3)', 'Medium (0.3-0.5)', 'High (0.5-0.7)', 'Very High (0.7-1.0)']
    )
    
    if not conversions_df.empty:
        merged = predictions_df.merge(conversions_df[['lead_id']], on='lead_id', how='left', indicator=True)
        merged['converted'] = (merged['_merge'] == 'both').astype(int)
        conversion_by_bucket = merged.groupby('score_bucket').agg({'converted': ['sum', 'count']}).reset_index()
        conversion_by_bucket.columns = ['score_bucket', 'conversions', 'total']
        conversion_by_bucket['conversion_rate'] = (conversion_by_bucket['conversions'] / conversion_by_bucket['total'] * 100)
        
        fig = px.bar(conversion_by_bucket, x='score_bucket', y='conversion_rate', title="Conversion Rate by Score Bucket",
                    labels={'conversion_rate': 'Conversion Rate (%)', 'score_bucket': 'Score Bucket'},
                    color='conversion_rate', color_continuous_scale='Greens')
        fig.update_layout(height=400, template='plotly_white')
        return fig
    
    return go.Figure()

def create_score_distribution_chart(df):
    """Create score distribution histogram"""
    if df.empty or 'lead_score' not in df.columns:
        return go.Figure()
    
    fig = px.histogram(df, x='lead_score', nbins=20, title="Lead Score Distribution",
                      labels={'lead_score': 'Lead Score', 'count': 'Frequency'})
    fig.update_layout(height=400, template='plotly_white')
    return fig

if __name__ == "__main__":
    today = datetime.now()
    print("\n" + "="*60)
    print("🚀 RAKEZ Lead Scoring Dashboard - STANDALONE DEMO MODE")
    print("="*60)
    print(f"\n📅 Today's Date: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Dashboard URL: http://localhost:8050")
    print(f"📊 Alternative: http://127.0.0.1:8050")
    print("\n✅ STANDALONE MODE: Dashboard works without backend!")
    print("   - Data loaded from CSV files in sample_data/")
    print("   - No backend connection required")
    print("   - Perfect for demos and presentations")
    print("\n💡 Data filtering uses TODAY's date automatically")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=8050)


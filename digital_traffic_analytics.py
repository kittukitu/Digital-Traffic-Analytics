import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import timedelta

# --- Step 1: Generate synthetic website traffic data (daily sessions) ---
np.random.seed(42)
days = 730  # Two years
dates = pd.date_range(start="2023-01-01", periods=days, freq='D')

# Simulate traffic with weekly seasonality + yearly trend + random noise
base_traffic = 1000 + np.linspace(0, 500, days)  # growing trend
weekly_seasonality = 200 * np.where(dates.dayofweek < 5, 1, 0.5)  # weekdays have 2x traffic than weekends
yearly_seasonality = 150 * np.sin(2 * np.pi * dates.dayofyear / 365)
random_noise = np.random.normal(0, 50, days)

sessions = base_traffic + weekly_seasonality + yearly_seasonality + random_noise
sessions = np.maximum(0, sessions).astype(int)

# Additional features
avg_session_duration = 5 + 2 * np.sin(2 * np.pi * dates.dayofyear / 365) + np.random.normal(0, 0.5, days)
bounce_rate = np.clip(0.4 - 0.1 * np.sin(2 * np.pi * dates.dayofweek / 7) + np.random.normal(0, 0.05, days), 0, 1)
conversion_rate = np.clip(0.05 + 0.01 * np.cos(2 * np.pi * dates.dayofyear / 365) + np.random.normal(0, 0.005, days), 0, 1)

data = pd.DataFrame({
    'date': dates,
    'sessions': sessions,
    'avg_session_duration_min': avg_session_duration,
    'bounce_rate': bounce_rate,
    'conversion_rate': conversion_rate
})

data.to_csv("synthetic_website_traffic.csv", index=False)
print("Synthetic website traffic dataset saved as 'synthetic_website_traffic.csv'.")

# --- Prepare timeseries ---
ts = data.set_index('date')['sessions']
ts.index.freq = 'D'  # Set frequency to suppress warnings

# --- User inputs ---
while True:
    try:
        start_forecast_str = input(f"Enter forecast start date (YYYY-MM-DD) between {ts.index.min().date()} and {ts.index.max().date()}: ")
        forecast_start_date = pd.to_datetime(start_forecast_str)
        if forecast_start_date < ts.index.min() or forecast_start_date > ts.index.max():
            print("Date out of range. Try again.")
            continue
        break
    except Exception:
        print("Invalid date format. Try again.")

while True:
    try:
        forecast_days = int(input("Enter number of days to forecast (e.g., 30): "))
        if forecast_days <= 0:
            print("Must be positive number.")
            continue
        break
    except Exception:
        print("Invalid number. Try again.")

# Optional marketing campaign intensity input (0 to 2 scale)
while True:
    try:
        marketing_intensity = float(input("Enter marketing campaign intensity (0 - 2, where 1 is normal): "))
        if not (0 <= marketing_intensity <= 2):
            print("Must be between 0 and 2.")
            continue
        break
    except Exception:
        print("Invalid input. Try again.")

# --- Adjust traffic based on marketing intensity ---
ts_adjusted = ts.copy()
if marketing_intensity != 1.0:
    ts_adjusted.loc[forecast_start_date:] = ts_adjusted.loc[forecast_start_date:] * marketing_intensity
    ts_adjusted = ts_adjusted.astype(int)

# Subset timeseries for modeling
ts_sub = ts_adjusted.loc[:forecast_start_date]
ts_sub.index.freq = 'D'

# --- Forecast using Holt-Winters ---
model = ExponentialSmoothing(ts_sub, trend='add', seasonal='add', seasonal_periods=7)
fit = model.fit()

forecast = fit.forecast(forecast_days)
forecast_dates = pd.date_range(ts_sub.index[-1] + timedelta(days=1), periods=forecast_days)

# --- Behavior insights and marketing recommendations ---
avg_forecast = forecast.mean()
if avg_forecast > 2500:
    marketing_rec = "Increase ad spend and server capacity to handle high traffic."
elif avg_forecast > 1500:
    marketing_rec = "Maintain current marketing budget; monitor peak times."
else:
    marketing_rec = "Consider campaigns to boost traffic during low volume periods."

print("\nForecasted sessions for the next", forecast_days, "days:")
print(pd.DataFrame({'date': forecast_dates, 'predicted_sessions': forecast.values}))

print(f"\nMarketing Recommendation: {marketing_rec}")

# --- Visualizations ---
plt.figure(figsize=(14,6))
plt.plot(ts.index, ts, label='Historical Sessions')
plt.plot(forecast_dates, forecast, 'r--', label='Forecast')
plt.title('Website Traffic (Sessions) Forecast')
plt.xlabel('Date')
plt.ylabel('Sessions')
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,7))
sns.lineplot(data=data, x='date', y='avg_session_duration_min', label='Avg Session Duration (min)')
sns.lineplot(data=data, x='date', y='bounce_rate', label='Bounce Rate')
sns.lineplot(data=data, x='date', y='conversion_rate', label='Conversion Rate')
plt.title('Website Behavior Metrics Over Time')
plt.legend()
plt.tight_layout()
plt.show()

# Data Analytics Service

## Purpose
This service performs:
- Descriptive Analytics: Current state analysis
- Diagnostic Analytics: Correlation analysis
- Predictive Analytics: ML-based forecasting

## ML Models

### Soil Dryness Prediction
- **Algorithm**: Linear Regression
- **Features**: Current moisture, temperature, humidity, time-of-day
- **Target**: Time to reach critical moisture (30%)
- **Update Frequency**: Every hour

### Plant Health Score
- **Algorithm**: Random Forest
- **Features**: All sensor readings
- **Target**: Health classification (excellent, good, fair, poor)
- **Update Frequency**: Every 30 minutes

## Files

- `main.py`: Entry point
- `predictor.py`: ML model predictions
- `analyzer.py`: Data analysis
- `requirements.txt`: Dependencies

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Predictions Output

### Soil Dryness Forecast
```json
{
  "timestamp": 1702400000000,
  "current_moisture": 61,
  "critical_moisture": 30,
  "eta_hours": 12.5,
  "confidence": 0.87,
  "recommendation": "Water in 12 hours"
}
```

## Monitoring

- Model accuracy metrics
- Prediction confidence scores
- Anomaly detection alerts

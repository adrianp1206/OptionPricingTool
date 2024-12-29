# Option Pricing Calculator

The **Option Pricing Calculator** is a web application that allows users to calculate the prices of financial options using different pricing models, generate heatmaps of option prices based on varying parameters, and visualize profit/loss (P/L) charts for different trading strategies. This project supports multiple option types, including European and American options, and allows users to toggle between the **Black-Scholes** and **Monte Carlo** pricing models.

---

## Features

### 1. Pricing Models
- **Black-Scholes Model**: A closed-form solution for European option pricing.
- **Monte Carlo Simulation**: A flexible approach that supports European and American options.

### 2. Option Types
- **European Options**: Can only be exercised at maturity.
- **American Options**: Can be exercised at any time before maturity (Monte Carlo simulation with Least Squares Method).

### 3. Visualizations
- **Heatmaps**:
  - Display call and put option prices based on spot price and volatility.
  - Color-coded from red (low prices) to green (high prices).
  - Numerical values displayed in each heatmap cell.
- **Profit/Loss Charts**:
  - Show the P/L across different spot prices for strategies like long/short calls and puts.

### 4. Interactive Toggles
- Switch between **Black-Scholes** and **Monte Carlo** models.
- Toggle between **European** and **American** options when using Monte Carlo.

### 5. Dynamic Updates
- Parameters and visualizations update automatically when toggles are changed or recalculations are triggered.

---

## Technology Stack

### Frontend
- **HTML5**
- **CSS (Bootstrap)**: Provides a responsive and clean UI.
- **JavaScript (Plotly.js)**: Generates interactive heatmaps and P/L charts.

### Backend
- **Flask (Python)**: Handles option pricing calculations and API endpoints.
- **NumPy**: Performs numerical computations for pricing models.
- **SciPy**: Implements statistical functions used in the Black-Scholes formula.

---

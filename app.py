from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.stats import norm

app = Flask(__name__)

# Black-Scholes formula
def black_scholes(S, K, T, r, sigma):
    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return call_price, put_price
    except Exception as e:
        return None, None

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Calculate route
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Extract data from the form
        S = float(request.form['stock_price'])
        K = float(request.form['strike_price'])
        T = float(request.form['time_to_maturity'])
        r = float(request.form['risk_free_rate'])
        sigma = float(request.form['volatility'])

        # Perform Black-Scholes calculation
        call_price, put_price = black_scholes(S, K, T, r, sigma)

        # Return JSON response
        return jsonify({
            'call_price': f"${call_price:.2f}",
            'put_price': f"${put_price:.2f}"
        })
    except ValueError:
        return jsonify({'error': 'Invalid input. Please enter numeric values.'})
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"})
    
@app.route('/heatmap', methods=['POST'])
def heatmap():
    try:
        data = request.get_json()
        min_spot = float(data.get('min_spot'))
        max_spot = float(data.get('max_spot'))
        min_volatility = float(data.get('min_volatility'))
        max_volatility = float(data.get('max_volatility'))
        strike_price = float(data.get('strike_price'))
        time_to_maturity = float(data.get('time_to_maturity'))
        risk_free_rate = float(data.get('risk_free_rate'))

        # Generate ranges for spot price and volatility (10 x 10 grid)
        spot_prices = np.linspace(min_spot, max_spot, 10)
        volatilities = np.linspace(min_volatility, max_volatility, 10)

        call_prices = []
        put_prices = []

        for sigma in volatilities:
            call_row = []
            put_row = []
            for S in spot_prices:
                call_price, put_price = black_scholes(S, strike_price, time_to_maturity, risk_free_rate, sigma)
                call_row.append(call_price)
                put_row.append(put_price)
            call_prices.append(call_row)
            put_prices.append(put_row)

        return jsonify({
            'spot_prices': spot_prices.tolist(),
            'volatilities': volatilities.tolist(),
            'call_prices': call_prices,
            'put_prices': put_prices
        })
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


@app.route('/pl', methods=['POST'])
def calculate_pl():
    try:
        data = request.get_json()
        strategy = data.get('strategy')  # E.g., 'long_call', 'short_put'
        min_spot = float(data.get('min_spot'))
        max_spot = float(data.get('max_spot'))
        strike_price = float(data.get('strike_price'))
        premium = float(data.get('premium'))  # Use the premium from the frontend

        # Generate a range of spot prices
        spot_prices = np.linspace(min_spot, max_spot, 50)

        # Calculate P/L
        pl_values = []
        for S in spot_prices:
            if strategy == 'long_call':
                pl = max(S - strike_price, 0) - premium
            elif strategy == 'long_put':
                pl = max(strike_price - S, 0) - premium
            elif strategy == 'short_call':
                pl = premium - max(S - strike_price, 0)
            elif strategy == 'short_put':
                pl = premium - max(strike_price - S, 0)
            pl_values.append(pl)

        return jsonify({
            'spot_prices': spot_prices.tolist(),
            'pl_values': pl_values
        })
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

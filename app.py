from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.stats import norm

app = Flask(__name__)

def black_scholes(S, K, T, r, sigma):
    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return call_price, put_price
    except Exception as e:
        return None, None

def monte_carlo_option_pricing(S, K, T, r, sigma, num_simulations=10000):
    Z = np.random.standard_normal(num_simulations)
    
    ST = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    
    call_payoffs = np.maximum(ST - K, 0)
    put_payoffs = np.maximum(K - ST, 0)
    
    call_price = np.exp(-r * T) * np.mean(call_payoffs)
    put_price = np.exp(-r * T) * np.mean(put_payoffs)
    
    return call_price, put_price

def monte_carlo_american_option(S, K, T, r, sigma, num_simulations=10000, num_steps=50):
    dt = T / num_steps
    discount_factor = np.exp(-r * dt)

    prices = np.zeros((num_simulations, num_steps + 1))
    prices[:, 0] = S
    for t in range(1, num_steps + 1):
        Z = np.random.standard_normal(num_simulations)
        prices[:, t] = prices[:, t - 1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)

    call_values = np.maximum(prices - K, 0)
    put_values = np.maximum(K - prices, 0)

    call_option = call_values[:, -1]
    put_option = put_values[:, -1]

    for t in range(num_steps - 1, 0, -1):
        in_the_money_call = call_values[:, t] > 0
        in_the_money_put = put_values[:, t] > 0

        if np.any(in_the_money_call):
            X_call = prices[in_the_money_call, t]
            Y_call = call_option[in_the_money_call] * discount_factor
            continuation_call = np.polyval(np.polyfit(X_call, Y_call, 2), X_call)
            exercise_call = call_values[in_the_money_call, t]
            call_option[in_the_money_call] = np.maximum(exercise_call, continuation_call)

        if np.any(in_the_money_put):
            X_put = prices[in_the_money_put, t]
            Y_put = put_option[in_the_money_put] * discount_factor
            continuation_put = np.polyval(np.polyfit(X_put, Y_put, 2), X_put)
            exercise_put = put_values[in_the_money_put, t]
            put_option[in_the_money_put] = np.maximum(exercise_put, continuation_put)

        call_option *= discount_factor
        put_option *= discount_factor

    call_price = np.mean(call_option) * np.exp(-r * dt)
    put_price = np.mean(put_option) * np.exp(-r * dt)

    return call_price, put_price


# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Calculate route
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        S = float(request.form['stock_price'])
        K = float(request.form['strike_price'])
        T = float(request.form['time_to_maturity'])
        r = float(request.form['risk_free_rate'])
        sigma = float(request.form['volatility'])
        option_type = request.form.get('option_type', 'European') 
        exotic_type = request.form.get('exotic_type', None)
        barrier_level = request.form.get('barrier_level', None)

        print(f"Inputs: S={S}, K={K}, T={T}, r={r}, sigma={sigma}, option_type={option_type}, exotic_type={exotic_type}, barrier_level={barrier_level}")

        if option_type == 'European':
            call_price, put_price = monte_carlo_option_pricing(S, K, T, r, sigma)
        elif option_type == 'American':
            call_price, put_price = monte_carlo_american_option(S, K, T, r, sigma)
        else:
            return jsonify({'error': 'Invalid exotic option type'})

        print(f"Prices: Call={call_price}, Put={put_price}")

        return jsonify({
            'call_price': f"${call_price:.2f}" if call_price is not None else "Error",
            'put_price': f"${put_price:.2f}" if put_price is not None else "Error"
        })
    except ValueError:
        return jsonify({'error': 'Invalid input. Please enter numeric values.'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"})




@app.route('/pl', methods=['POST'])
def calculate_pl():
    try:
        data = request.get_json()
        strategy = data.get('strategy') 
        min_spot = float(data.get('min_spot'))
        max_spot = float(data.get('max_spot'))
        strike_price = float(data.get('strike_price'))
        premium = float(data.get('premium')) 

        spot_prices = np.linspace(min_spot, max_spot, 50)

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
        option_type = data.get('option_type', 'European')
        exotic_type = data.get('exotic_type', None)
        barrier_level = float(data.get('barrier_level', 0)) if data.get('barrier_level') else None
        
        spot_prices = np.linspace(min_spot, max_spot, 10)
        volatilities = np.linspace(min_volatility, max_volatility, 10)

        call_prices = []
        put_prices = []

        for sigma in volatilities:
            call_row = []
            put_row = []
            for S in spot_prices:
                if option_type == 'European':
                    call_price, put_price = black_scholes(S, strike_price, time_to_maturity, risk_free_rate, sigma)
                elif option_type == 'American':
                    call_price, put_price = monte_carlo_american_option(S, strike_price, time_to_maturity, risk_free_rate, sigma)
                else:
                    call_price, put_price = None, None
                call_row.append(call_price)
                put_row.append(put_price)
            call_prices.append(call_row)
            put_prices.append(put_row)

        return jsonify({
            'spot_prices': spot_prices.tolist(),
            'volatilities': volatilities.tolist(),
            'call_prices': call_prices,
            'put_prices': put_prices,
        })
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

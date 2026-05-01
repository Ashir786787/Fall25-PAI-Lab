from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os
import random
import warnings
import urllib3
from typing import Dict, Any, Optional, List
import requests
from dotenv import load_dotenv

warnings.filterwarnings('ignore', category=FutureWarning)

try:
    import google.generativeai as ai_module
    LIB_FOUND = True
except ImportError:
    ai_module = None
    LIB_FOUND = False

load_dotenv()

os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_NO_VERIFY'] = '1'
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings()

my_ai = None
my_model = None
AI_STATUS = False
MY_KEY = os.getenv('GEMINI_API_KEY', '').strip()

STOCK_LIST = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics', 'price': 180.50},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'price': 140.30},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software', 'price': 420.75},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail', 'price': 190.45},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Automotive', 'price': 248.90},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'industry': 'Internet Services', 'price': 520.30},
    'NFLX': {'name': 'Netflix Inc.', 'sector': 'Communication Services', 'industry': 'Entertainment', 'price': 450.10},
}

def make_seed_val(symbol):
    val = 0
    for char in symbol:
        val = (val * 31 + ord(char)) & 0xFFFFFFFF
    return val

def get_info_for_stock(symbol):
    if symbol not in STOCK_LIST:
        return None
    
    info = STOCK_LIST[symbol]
    base = info['price']
    
    random.seed(make_seed_val(symbol))
    
    tm_offset = (datetime.now().minute * 60 + datetime.now().second) // 30 
    random.seed(make_seed_val(symbol) + tm_offset)
    
    return {
        'symbol': symbol,
        'name': info['name'],
        'sector': info['sector'],
        'industry': info['industry'],
        'price': base * (1 + random.uniform(-0.02, 0.02)),
        'prev': base,
        'market_cap': random.randint(1000000000000, 3000000000000),
        'vol': random.randint(10000000, 100000000),
        'pe': random.uniform(15, 35),
        'high': base * 1.25,
        'low': base * 0.75,
        'avg_v': random.randint(20000000, 80000000),
    }

def get_history_for_stock(symbol, time_period='1mo'):
    if symbol not in STOCK_LIST:
        return []
    
    base = STOCK_LIST[symbol]['price']
    random.seed(make_seed_val(symbol))
    
    my_map = {'1d': 1, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
    total_days = my_map.get(time_period, 30)
    
    history_data = []
    now = datetime.now()
    tmp_price = base
    
    for i in range(total_days, 0, -1):
        dt_str = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        tmp_price *= (1 + random.uniform(-0.015, 0.015))
        history_data.append({'date': dt_str, 'price': round(tmp_price, 2)})
    
    return history_data

app = Flask(__name__)

def setup_my_ai():
    global my_ai, my_model, AI_STATUS
    if not MY_KEY or not LIB_FOUND:
        AI_STATUS = False
        return
    try:
        ai_module.configure(api_key=MY_KEY)
        my_model = ai_module.GenerativeModel('gemini-1.5-flash')
        my_ai = ai_module
        AI_STATUS = True
    except:
        AI_STATUS = False

setup_my_ai()

def ask_my_ai(p_text):
    if AI_STATUS and my_model:
        try:
            res = my_model.generate_content(p_text)
            if hasattr(res, 'text'):
                return res.text
            return str(res)
        except:
            pass
    
    my_responses = {
        'prediction': "The stock price might go up by 5% in the next few weeks.",
        'analysis': "The stock is looking strong with good market support.",
        'news': "Positive news in the tech sector is helping this stock.",
        'advice': "It is a good idea to hold this stock for long term.",
        'query': "This stock has a very good historical performance."
    }
    
    p_lower = p_text.lower()
    if 'prediction' in p_lower: return my_responses['prediction']
    if 'analysis' in p_lower: return my_responses['analysis']
    if 'news' in p_lower: return my_responses['news']
    if 'advice' in p_lower: return my_responses['advice']
    return my_responses['query']

@app.route('/favicon.ico')
def get_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stock/<s_symbol>')
def stock_api(s_symbol):
    try:
        s_symbol = s_symbol.upper()
        data = get_info_for_stock(s_symbol)
        if not data:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        
        c_val = data['price']
        p_val = data['prev']
        diff = c_val - p_val
        percent = (diff / p_val * 100) if p_val else 0
        
        return jsonify({
            'success': True,
            'symbol': s_symbol,
            'name': data['name'],
            'price': round(c_val, 2),
            'change': round(diff, 2),
            'changePercent': round(percent, 2),
            'previousClose': round(p_val, 2),
            'marketCap': data['market_cap'],
            'volume': data['vol'],
            'peRatio': round(data['pe'], 2),
            'week52High': round(data['high'], 2),
            'week52Low': round(data['low'], 2),
            'avgVolume': data['avg_v'],
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock-history/<s_symbol>')
def history_api(s_symbol):
    try:
        p = request.args.get('period', '1mo')
        s_symbol = s_symbol.upper()
        h_data = get_history_for_stock(s_symbol, p)
        if not h_data:
            return jsonify({'success': False, 'error': 'No data'}), 404
        
        return jsonify({
            'success': True,
            'dates': [x['date'] for x in h_data],
            'prices': [x['price'] for x in h_data]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_api():
    try:
        req_data = request.get_json(silent=True) or {}
        syms = req_data.get('symbols', [])
        if not syms:
            return jsonify({'success': False, 'error': 'No symbols'}), 400
        
        out = []
        for s in syms:
            s = s.upper()
            d = get_info_for_stock(s)
            if d:
                c = d['price']
                p = d['prev']
                pct = ((c - p) / p * 100) if p else 0
                out.append({
                    'symbol': s,
                    'name': d['name'],
                    'price': round(c, 2),
                    'changePercent': round(pct, 2),
                    'volume': d['vol']
                })
        return jsonify({'success': True, 'data': out})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/prediction/<s_symbol>')
def ai_pred(s_symbol):
    s_symbol = s_symbol.upper()
    d = get_info_for_stock(s_symbol)
    if not d: return jsonify({'success': False}), 404
    p = f"Predict the price for {s_symbol} ({d['name']}) at ${d['price']:.2f}. Be brief."
    txt = ask_my_ai(p)
    return jsonify({'success': True, 'symbol': s_symbol, 'prediction': txt})

@app.route('/api/ai/analysis/<s_symbol>')
def ai_anal(s_symbol):
    s_symbol = s_symbol.upper()
    d = get_info_for_stock(s_symbol)
    if not d: return jsonify({'success': False}), 404
    p = f"Analyze {s_symbol} at ${d['price']:.2f}. High is {d['high']}. Be brief."
    txt = ask_my_ai(p)
    return jsonify({'success': True, 'symbol': s_symbol, 'analysis': txt})

@app.route('/api/ai/news-summary/<s_symbol>')
def ai_nws(s_symbol):
    s_symbol = s_symbol.upper()
    d = get_info_for_stock(s_symbol)
    if not d: return jsonify({'success': False}), 404
    p = f"News summary for {s_symbol}. 4 bullets. Be brief."
    txt = ask_my_ai(p)
    return jsonify({'success': True, 'symbol': s_symbol, 'news': txt})

@app.route('/api/ai/investment-advice/<s_symbol>')
def ai_adv(s_symbol):
    s_symbol = s_symbol.upper()
    d = get_info_for_stock(s_symbol)
    if not d: return jsonify({'success': False}), 404
    p = f"Advice for {s_symbol} at ${d['price']:.2f}. Be brief."
    txt = ask_my_ai(p)
    return jsonify({'success': True, 'symbol': s_symbol, 'advice': txt})

@app.route('/api/ai/ask', methods=['POST'])
def ai_ask_api():
    try:
        req = request.get_json(silent=True) or {}
        s = req.get('symbol', '').upper()
        q = req.get('question', '')
        d = get_info_for_stock(s)
        if not d: return jsonify({'success': False, 'error': 'Not found'}), 400
        p = f"Answer about {s}: {q}"
        txt = ask_my_ai(p)
        return jsonify({'success': True, 'symbol': s, 'question': q, 'answer': txt})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Hardcoded query results
hardcoded_results = {
    "Show me all suppliers from the USA": {
        'sql_query': "SELECT * FROM Suppliers WHERE country = 'USA'",
        'result': [
            {'id': 1, 'name': 'ABC Corp', 'country': 'USA', 'city': 'New York'},
            {'id': 3, 'name': 'XYZ Inc', 'country': 'USA', 'city': 'Los Angeles'}
        ],
        'insights': "There are 2 suppliers from the USA in our database. They are located in different cities, suggesting a diverse geographical presence."
    },
    "What's the total inventory for product ID 5?": {
        'sql_query': "SELECT SUM(quantity) as total_quantity FROM Inventory WHERE product_id = 5",
        'result': [
            {'total_quantity': 1500}
        ],
        'insights': "The total inventory for product ID 5 is 1500 units. This might indicate a high-demand product or a recent restocking."
    },
    "List all orders with a total value over $1000": {
        'sql_query': "SELECT * FROM Orders WHERE total > 1000",
        'result': [
            {'id': 101, 'customer_name': 'John Doe', 'order_date': '2024-07-15', 'total': 1200.50},
            {'id': 102, 'customer_name': 'Jane Smith', 'order_date': '2024-07-16', 'total': 1500.75}
        ],
        'insights': "There are 2 orders with a total value over $1000. These high-value orders might be from key customers or include bulk purchases."
    },
    "How many products are below the reorder point?": {
        'sql_query': "SELECT COUNT(*) as low_stock_count FROM Inventory WHERE quantity < reorder_point",
        'result': [
            {'low_stock_count': 5}
        ],
        'insights': "5 products are below their reorder point. This suggests that restocking may be necessary soon to avoid stockouts."
    },
    "What's the average order value?": {
        'sql_query': "SELECT AVG(total) as avg_order_value FROM Orders",
        'result': [
            {'avg_order_value': 750.25}
        ],
        'insights': "The average order value is $750.25. This metric can be useful for understanding customer spending patterns and setting sales targets."
    }
}

@app.route('/')
def index():
    logging.info("Accessed home page")
    return render_template('chat.html')

@app.route('/query', methods=['POST'])
def execute_query():
    if not request.is_json:
        error_msg = 'Invalid content type, expected JSON'
        logging.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 400
    
    data = request.get_json()
    if 'query' not in data:
        error_msg = 'Missing query parameter'
        logging.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 400
    
    natural_language_query = data['query']
    logging.info(f"Received query: {natural_language_query}")
    
    if natural_language_query in hardcoded_results:
        result = hardcoded_results[natural_language_query]
        logging.info(f"Returning hardcoded result for query: {natural_language_query}")
        return jsonify({'success': True, **result})
    else:
        error_msg = "Query not found in hardcoded results"
        logging.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
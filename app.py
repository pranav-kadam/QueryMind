from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import google.generativeai as genai
import os
import logging
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Pranav\\Desktop\\WP\\Employees.db'  # Ensure this path is correct
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

api_responses = []

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def query_gemini(prompt):
    if not GEMINI_API_KEY:
        error_msg = "Gemini API key is not set. Please set the GEMINI_API_KEY."
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        result = response.text.strip()
        logging.info(f"Gemini API response: {result}")
        return result
    except Exception as e:
        error_msg = f"Gemini API request failed: {str(e)}"
        logging.error(error_msg)
        raise Exception(error_msg)

def clean_sql_query(sql_query):
    sql_query = re.sub(r'^[^a-zA-Z]*(select|insert|update|delete)', r'\1', sql_query, flags=re.IGNORECASE)
    
    sql_query_lines = sql_query.split('\n')
    sql_query_lines = [line.strip() for line in sql_query_lines if line.strip()]
    cleaned_sql_query = ' '.join(sql_query_lines)
    
    logging.info(f"Cleaned SQL query: {cleaned_sql_query}")
    return cleaned_sql_query

@app.route('/')
def index():
    logging.info("Accessed home page")
    return render_template('Home.html')

@app.route('/config')
def config():
    logging.info("Accessed config page")
    return render_template('setDB.html')

@app.route('/chat')
def chat():
    logging.info("Accessed chat page")
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

    try:
        prompt = f"Convert the following natural language query to SQL. Also the sql code should not have ``` in beginning or end and sql word or SQL word in output. Respond only with the SQL query and no other text: '{natural_language_query}'."
        sql_query = query_gemini(prompt)
        sql_query = clean_sql_query(sql_query)
        logging.info(f"Generated SQL query: {sql_query}")
        
        logging.debug(f"Executing SQL query: {sql_query}")
        result = db.session.execute(text(sql_query))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        logging.info(f"Query result: {rows}")

        insights_prompt = f"Given the following SQL query: '{sql_query}' and its result: {rows}, provide insights and analysis about the data. Keep the response concise and focused on the most important findings."
        insights = query_gemini(insights_prompt)
        logging.info(f"Generated insights: {insights}")

        response_data = {
            'success': True,
            'sql_query': sql_query,
            'result': rows,
            'insights': insights
        }

        # Store the API response
        api_responses.append(response_data)

        return jsonify(response_data)
    except ValueError as e:
        error_msg = f"Value error: {str(e)}"
        logging.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 400
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logging.error(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/get_api_responses', methods=['GET'])
def get_api_responses():
    return jsonify({'api_responses': api_responses})

if __name__ == '__main__':
    app.run(debug=True)
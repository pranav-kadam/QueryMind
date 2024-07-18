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

logging.basicConfig(level=logging.DEBUG)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def query_gemini(prompt):
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not set. Please set the GEMINI_API_KEY.")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        app.logger.error(f"Gemini API request failed: {str(e)}")
        raise Exception(f"Gemini API request failed: {str(e)}")

def clean_sql_query(sql_query):
    # Remove leading non-alphabetic characters
    sql_query = re.sub(r'^[^a-zA-Z]*(select|insert|update|delete)', r'\1', sql_query, flags=re.IGNORECASE)
    
    # Clean up the response
    sql_query_lines = sql_query.split('\n')
    sql_query_lines = [line.strip() for line in sql_query_lines if line.strip()]
    cleaned_sql_query = ' '.join(sql_query_lines)
    
    return cleaned_sql_query

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def execute_query():
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Invalid content type, expected JSON'}), 400
    
    data = request.get_json()
    if 'query' not in data:
        return jsonify({'success': False, 'error': 'Missing query parameter'}), 400

    natural_language_query = data['query']
    try:
        app.logger.info(f"Received query: {natural_language_query}")
        prompt = f"Convert the following natural language query to SQL. Also the sql code should not have ``` in beginning or end and sql word or SQL word in output. Respond only with the SQL query and no other text: '{natural_language_query}'."
        sql_query = query_gemini(prompt)
        sql_query = clean_sql_query(sql_query)
        app.logger.info(f"Generated SQL query: {sql_query}")

     

        # Log and execute the SQL query
        app.logger.debug(f"Executing SQL query: {sql_query}")
        result = db.session.execute(text(sql_query))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        # Generate insights based on the query result
        insights_prompt = f"Given the following SQL query: '{sql_query}' and its result: {rows}, provide insights and analysis about the data. Keep the response concise and focused on the most important findings."
        insights = query_gemini(insights_prompt)

        return jsonify({'success': True, 'sql_query': sql_query, 'result': rows, 'insights': insights})
    except ValueError as e:
        app.logger.error(f"Value error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
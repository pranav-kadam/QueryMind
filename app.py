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
# Define the schema
schema_info = """
Tables:
1. dept (Department):
   - DEPTNO (integer, primary key)
   - DNAME (string)
   - LOC (string)

2. emp (Employee):
   - EMPNO (integer, primary key)
   - MGR (integer, foreign key)
   - DEPTNO (integer, foreign key referencing dept table)
   - ENAME (string)
   - JOB (string)
   - HIREDATE (datetime)
   - SAL (integer)
   - COMM (integer)

3. proj (Project):
   - PROJID (integer, primary key)
   - EMPNO (integer, foreign key referencing emp table)
   - STARTDATE (datetime)
   - ENDDATE (datetime)

4. Managers (view or derived table):
   - Manager (string)
   - Employee (string)
"""

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
    sql_query = re.sub(r'^[^a-zA-Z]*(?:sql\s*)?', '', sql_query, flags=re.IGNORECASE)
    sql_query = sql_query.replace('```', '')
    sql_query_lines = [line.strip() for line in sql_query.split('\n') if line.strip()]
    cleaned_sql_query = ' '.join(sql_query_lines)
    app.logger.info(f"Cleaned SQL query: {cleaned_sql_query}")
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
        prompt = f"""
            Database Schema:
            {schema_info}
            Task: Convert the following natural language query to SQL:
            "{natural_language_query}"
            Instructions:
            Analyze the given schema and natural language query carefully.
            Write a precise and efficient SQL query that accurately represents the natural language query.
            Ensure the SQL query is compatible with the provided schema.
            Use appropriate JOIN operations, WHERE clauses, and aggregate functions as needed.
            Include any necessary subqueries or Common Table Expressions (CTEs) if required.
            Optimize the query for performance where possible.
            Use consistent and clear formatting for readability.
            Double-check that all referenced tables and columns exist in the schema.

            Output Requirements:

            Provide ONLY the SQL query without any additional text or explanations.
            Do not include any markdown formatting, such as backticks or SQL language specifiers.
            The response should begin and end with the SQL query itself.

            SQL Query: """
        
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
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import google.generativeai as genai
import os
import logging
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# PostgreSQL connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:pp@localhost:5432/postgres')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Store API responses
api_responses = []

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

def clean_sql_query(sql_query, available_tables):
    # Remove any leading or trailing whitespace
    sql_query = sql_query.strip()
    
    # Remove any code block markers
    sql_query = re.sub(r'```sql|```', '', sql_query)
    
    # Ensure the query starts with a valid SQL command
    if not re.match(r'^(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)', sql_query, re.IGNORECASE):
        raise ValueError("Invalid SQL query: must start with a valid SQL command")
    
    # Check if the query references only available tables
    table_pattern = r'\bFROM\s+(\w+)|JOIN\s+(\w+)'
    referenced_tables = set(re.findall(table_pattern, sql_query, re.IGNORECASE))
    referenced_tables = {table for group in referenced_tables for table in group if table}  # Flatten and remove empty strings
    
    invalid_tables = referenced_tables - set(available_tables)
    if invalid_tables:
        raise ValueError(f"Query references non-existent tables: {', '.join(invalid_tables)}")
    
    logging.info(f"Cleaned SQL query: {sql_query}")
    return sql_query

def get_table_names():
    inspector = inspect(engine)
    return inspector.get_table_names()

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
    
    try:
        available_tables = get_table_names()
        prompt = f"""
        Convert the following natural language query to SQL for PostgreSQL.
        Available tables: {', '.join(available_tables)}
        Rules:
        1. Use ONLY the tables mentioned above.
        2. If the query cannot be satisfied with the available tables, respond with 'ERROR: Required information not available in the database.'
        3. Do not include any explanations or notes, just the SQL query.
        4. Do not use backticks or 'sql' markers in your response.

        Natural language query: '{natural_language_query}'
        """
        sql_query = query_gemini(prompt)
        sql_query = clean_sql_query(sql_query, available_tables)
        logging.info(f"Generated SQL query: {sql_query}")
        
        # Execute the SQL query
        logging.debug(f"Executing SQL query: {sql_query}")
        with Session() as session:
            result = session.execute(text(sql_query))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
        logging.info(f"Query result: {rows}")
        
        # Generate insights based on the query result
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
    logging.info("Fetched API responses")
    return jsonify({'api_responses': api_responses})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
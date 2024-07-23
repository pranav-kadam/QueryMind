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
    
    return sql_query

def get_table_names():
    inspector = inspect(engine)
    return inspector.get_table_names()

@app.route('/')
def index():
    return render_template('chat.html')

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
        app.logger.info(f"Generated SQL query: {sql_query}")
        
        # Execute the SQL query
        app.logger.debug(f"Executing SQL query: {sql_query}")
        with Session() as session:
            result = session.execute(text(sql_query))
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
    app.run(debug=True, port=5001)

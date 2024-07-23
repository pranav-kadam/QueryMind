# QueryMind
**Any database, effortlessly managed.**

## Overview
QueryMind is a chat-based text-to-SQL database assistant designed to interact with any SQL database. The chatbot converts user's questions into SQL queries, executes the query on the database retrieves relevant data. Additionally, it generates insights about the data that the user might need.

## Features
- **Natural Language Queries:** Chat with your database in plain English.
- **SQL Query Translation:** QueryMind's innovative text-to-SQL feature translates user input into SQL queries.
- **Multi-Database Support:** QueryMind is compatible with databases such as PostgreSQL, SQLite, and more.
- **Intuitive UI:** QueryMind's intuitive UI allows you to easily connect to your database with just a few clicks.
- **Insights:** Receive not just the relevant tables but also data-driven insights about your query.
- **Save Conversations:** With one click, save your conversations offline.

## Technologies and Libraries Utilized
- **Flask:** Used for implementing backend logic.
- **Google Gemini API:** Leverages generative AI for processing natural language queries.
- **SQLAlchemy:** Employed for database interaction.
- **Tailwind CSS:** Applied for designing and styling the user interface.

## Installation
1. Clone the repository
  ```bash
   git clone https://github.com/pranav-kadam/QueryMind.git
   cd Querymind
   ```
3. Navigate to the repository's directory and install the dependencies from `requirements.txt`.
    ```bash
   pip install requirements.txt
   ```
5. Enter your Gemini API Key in `app.py` either directly or via a `.env` file.
6. If using a SQLite database, enter your database URL in `app.py` located in the root directory.
7. If using a PostgreSQL database, enter your database URL in `app.py` located in `./templates/app.py`.

## Usage
1. Execute `run.py`.
2. Open the application in your browser at `localhost:5000`.
3. Select your database type.
4. Query your database in plain English.

## Prerequisites
- Users must know the schema of the database they are querying.


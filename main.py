import openai
import pymysql.cursors
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

db = pymysql.connect(
    host="localhost",
    user="insert_user",
    passwd="insert_password",
    database="insert_database"
)
mycursor = db.cursor()


openai.api_key = "OpenAI_API_KEY"


# Function to interact with OpenAI's GPT
def chat_with_gpt(prompt, role="user"):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": role, "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Function to execute a query and return results as a pandas DataFrame
def execute_query(query):
    try:
        mycursor.execute(query)
        results = mycursor.fetchall()
        columns = [desc[0] for desc in mycursor.description]
        df = pd.DataFrame(results, columns=columns)
        return df
    except Exception as e:
        return str(e)

# Function to extract SQL query from the response
def extract_query(response):
    # List of SQL keywords to recognize as the start of a query
    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE"]
    query_start = -1
    for keyword in sql_keywords:
        query_start = response.upper().find(keyword)
        if query_start != -1:
            break
    if query_start == -1:
        return "Invalid query generated."
    query_end = response.find(";", query_start) + 1
    return response[query_start:query_end]

if __name__ == "__main__":
    database_name = "mydatabase"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        if "query" in user_input.lower() or "database" in user_input.lower() or "table" in user_input.lower():
            query_prompt = f"Generate a MySQL query for the following request in the database '{database_name}': {user_input}"
            response = chat_with_gpt(query_prompt, role="system")
            print("OpenAI Response:", response)
            query = extract_query(response)
            print("Extracted Query:", query)
            dataset = execute_query(query)
            print("Query Results:")
            print(dataset)
        else:
            response = chat_with_gpt(user_input)
            print("Bot:", response)
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler
import re
import json
import markdown


# Define a callback handler to stream tokens
# class StreamHandler(BaseCallbackHandler):
#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         print(token, end='', flush=True)

class StreamCaptureHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end='', flush=True)
        self.tokens.append(token)  # Accumulate token

    def get_response_text(self):
        return ''.join(self.tokens)



template_1 = """ You are an expert in Snowflake and SQL and database testing. Your task is to analyze the given database schema and stored procedure, then generate a comprehensive set of test cases to validate its correctness, efficiency, and robustness.

Instructions:
Understand the Schema: Carefully examine the structure of the database, including tables, columns, data types, constraints (e.g., primary keys, foreign keys, unique constraints), and relationships.
Analyze the Stored Procedure: Identify its purpose, inputs, outputs, logic, and any dependencies on other database objects.
Generate Test Cases: Create well-defined test cases covering a variety of scenarios, including:
Basic Functionality: Ensure the procedure produces expected results for valid inputs.
Boundary Conditions: Test edge cases such as minimum/maximum values and empty inputs.
Error Handling: Validate how the procedure handles invalid inputs, missing parameters, or constraint violations.
Performance Considerations: Check execution time with different data volumes.
Security Aspects: Verify if the procedure prevents SQL injection and enforces proper access controls.
Provide Snowflake SQL Test Scripts: Generate Snowflake statements to execute the test cases, insert necessary sample data, and verify expected results.

Database Schema:
{schema}

Stored Procedure:
{procedure}
 
Now, generate a detailed set of test cases in the specified format, including the test case number, purpose, preconditions, expected result, and corresponding 
Snowflake SQL scripts to validate the stored procedure’s behavior under various conditions. Ensure each test case follows the given structure:  

**Test Case X: [Descriptive Title]**  

* Purpose: [Briefly describe the objective of the test case.]  
* Preconditions:  
  + [Specify any required setup or input parameters.]  
* Expected Result:  
  + [Describe the expected behavior or output of the stored procedure.]  

Example test case:-
```sql  
-- Test Case X: [Descriptive Title]  

-- [Include Snowflake SQL commands to execute the test case]  
CALL [Stored_Procedure_Name]([Test Parameters]);  
```"  

This ensures all test cases follow the desired template. Please generate the test cases accordingly.
"""


# Read schema from dataset.txt
with open('schema.txt', 'r') as f:
    schema_text = f.read()



sp_1 = """ 
ALTER PROCEDURE [dbo].[GetCustomerRentals]
    @customer_id INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT r.rental_id, f.title AS film_title, r.rental_date, r.return_date
    FROM sakila.rental r
    INNER JOIN sakila.inventory i ON r.inventory_id = i.inventory_id
    INNER JOIN sakila.film f ON i.film_id = f.film_id
    WHERE r.customer_id = @customer_id
    ORDER BY r.rental_date DESC;
END;

 """



#Convert and export response test cases to json format
def parse_test_cases(response_text):
    # Extract stored procedure name
    stored_proc_match = re.search(r"stored procedure `([\w\d_]+)`", response_text)
    stored_procedure = stored_proc_match.group(1) if stored_proc_match else "Unknown"

    # Split test cases using "**Test Case X:**" pattern
    test_cases_raw = re.split(r"\*\*Test Case (\d+):\s*(.*?)\*\*", response_text)[1:]

    test_cases = []
    for i in range(0, len(test_cases_raw), 3):
        test_case_id = int(test_cases_raw[i])
        title = test_cases_raw[i+1].strip()
        details = test_cases_raw[i+2]

        # Extract Purpose
        purpose_match = re.search(r"\* Purpose:\s*(.*?)\n", details, re.DOTALL)
        purpose = purpose_match.group(1).strip() if purpose_match else "N/A"

        # Extract Preconditions
        preconditions_match = re.search(r"\* Preconditions:\s*(.*?)\* Expected Result:", details, re.DOTALL)
        preconditions = preconditions_match.group(1).strip().split("\n") if preconditions_match else []

        # Extract Expected Result
        expected_result_match = re.search(r"\* Expected Result:\s*(.*?)```sql", details, re.DOTALL)
        expected_result = expected_result_match.group(1).strip().split("\n") if expected_result_match else []

        # Extract SQL commands
        sql_commands_match = re.findall(r"```sql(.*?)```", details, re.DOTALL)
        sql_commands = sql_commands_match[0].strip().split("\n") if sql_commands_match else []

        # Extract CALL statement
        call_statement = next((cmd for cmd in sql_commands if "CALL" in cmd), "N/A")

        # Extract verification SQL
        verify_test_case = next((cmd for cmd in sql_commands if "SELECT" in cmd), "N/A")

        test_cases.append({
            "test_case_id": test_case_id,
            "title": title,
            "purpose": purpose,
            "preconditions": [p.strip("+ ") for p in preconditions if p.strip()],
            "expected_result": [e.strip("+ ") for e in expected_result if e.strip()],
            "sql_commands": [cmd.strip() for cmd in sql_commands if "CALL" not in cmd and "SELECT" not in cmd],
            "CALL statement": call_statement.strip(),
            "Verify_test_case": verify_test_case.strip()
        })

    return {
        "stored_procedure": stored_procedure,
        "test_cases": test_cases
    }



# Stream handler
handler = StreamCaptureHandler()

# Model
model = OllamaLLM(model="spapp", streaming=True, callbacks=[handler])

prompt = ChatPromptTemplate.from_template(template_1)
chain = prompt | model

# Invoke the chain with both schema and procedure
response = chain.invoke({
    "schema": schema_text,
    "procedure": sp_1
})

# Get final response text
response_text = handler.get_response_text()

# To Export in Json format
# parsed_json = parse_test_cases(response_text) # Convert and export response test cases to json format

# # Save JSON to a file
# json_filename = "test_cases_1.json"
# with open(json_filename, "w", encoding="utf-8") as json_file:
#     json.dump(parsed_json, json_file, indent=4)

# print(f"JSON data has been successfully exported to {json_filename}")



# Convert Markdown to HTML
formatted_html = markdown.markdown(response_text, extensions=['tables', 'fenced_code'])

# Now, inject into the HTML template
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Stored Procedure Test Cases</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f9f9f9;
        }}
        h1 {{
            color: #333;
        }}
        pre {{
            background-color: #eee;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .response {{
            background-color: #fff;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        table, th, td {{
            border: 1px solid #ccc;
            border-collapse: collapse;
            padding: 8px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <h1>Stored Procedure Test Cases</h1>
    <h2>Stored Procedure:</h2>
    <pre>{sp_1}</pre>
    <h2>Test Cases & Explanation:</h2>
    <div class="response">
        {formatted_html}
    </div>
</body>
</html>
"""

# Save to file
with open("test_cases.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("HTML with formatted content saved!")
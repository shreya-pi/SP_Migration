from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler
import re
import json




class StreamCaptureHandler(BaseCallbackHandler):
    def __init__(self):
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end='', flush=True)
        self.tokens.append(token)  # Accumulate token

    def get_response_text(self):
        return ''.join(self.tokens)



template_1 = """ You are a SQL expert.  

Here is a stored procedure:  

{procedure}  

Analyze the stored procedure and provide a detailed explanation in the following format:  

Stored Procedure Name:  
- Provide the exact name of the stored procedure.  

Database & Schema Information:  
- Identify the database and schema it belongs to.  

Purpose & Description:  
- Clearly explain the procedure's objective and functionality in simple terms.  

Input Parameters:  
- List all input parameters along with their data types and purpose.  

Output (Return Values or Result Set):  
- Describe the structure and meaning of the returned results or output values.  

Step-by-Step Execution Breakdown:  
- Provide a detailed breakdown of the execution flow, including key SQL operations.  

Dependencies (Tables, Views, Other SPs, Functions):  
- Identify the database objects (tables, views, stored procedures, or functions) used within this procedure.  

Example Execution:  
- Show an example of how this stored procedure can be executed, including sample inputs and expected results.  

Error Handling & Logging:  
- Mention any error-handling mechanisms, logging features, or potential failure scenarios.  

Ensure the explanation is clear, precise, and suitable for both beginners and experienced SQL developers.  """

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

sp_2 = """ ALTER PROCEDURE [dbo].[AddRental]
    @customer_id INT,
    @inventory_id INT,
    @staff_id INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @rental_id INT;
    DECLARE @rental_date DATETIME = GETDATE();

    -- Insert rental record
    INSERT INTO sakila.rental (rental_date, inventory_id, customer_id, staff_id, return_date)
    VALUES (@rental_date, @inventory_id, @customer_id, @staff_id, NULL);

    -- Return the last inserted rental ID
    SET @rental_id = SCOPE_IDENTITY();

    -- Return the new rental ID
    SELECT @rental_id AS NewRentalID;
END;
"""


def parse_stored_procedure_explanation(explanation_text, output_filename):

    # Define the expected sections with regex patterns
    sections = [
        r"\*\*Stored Procedure Name:\*\*",
        r"\*\*Database & Schema Information:\*\*",
        r"\*\*Purpose & Description:\*\*",
        r"\*\*Input Parameters:\*\*",
        r"\*\*Output \(Return Values or Result Set\):\*\*",
        r"\*\*Step-by-Step Execution Breakdown:\*\*",
        r"\*\*Dependencies \(Tables, Views, Other SPs, Functions\):\*\*",
        r"\*\*Example Execution:\*\*",
        r"\*\*Error Handling & Logging:\*\*"
    ]

    parsed_data = {}

    # Construct regex pattern for section extraction
    pattern = r"(?P<section>" + "|".join(sections) + r")\s*(?P<content>(.*?))(?=\n\*\*[A-Z][a-zA-Z &()]+:\*\*|\Z)"
    
    matches = re.finditer(pattern, explanation_text, re.DOTALL)

    for match in matches:
        section = match.group("section").strip()
        content = match.group("content").strip()
        section = re.sub(r"\*\*", "", section)
        parsed_data[section] = content

    # Export to JSON file
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(parsed_data, json_file, indent=4)

    return parsed_data



# Stream handler
handler = StreamCaptureHandler()

# Model
model = OllamaLLM(model="spapp", streaming=True, callbacks=[handler])

prompt = ChatPromptTemplate.from_template(template_1)
chain = prompt | model

# Invoke the chain with both schema and procedure
response = chain.invoke({
    "schema": schema_text,
    "procedure": sp_2
})

# Get final response text
response_text = handler.get_response_text()
output_filename="sp_exp.json"
parsed_json = parse_stored_procedure_explanation(response_text,output_filename) # Convert and export response test cases to json format




# Save JSON to a file
# json_filename = "test_cases_1.json"
# with open(json_filename, "w", encoding="utf-8") as json_file:
#     json.dump(parsed_json, json_file, indent=4)

# print(f"JSON data has been successfully exported to {json_filename}")





from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import re


class GenerateQuery:

    def extract_table_name(self,schema_chunk):
        match = re.match(r'"([\w]+)\.([\w]+)"', schema_chunk)
        if match:
            return f"{match.group(1)}.{match.group(2)}"  # => sakila.rental
        return None
    
    
    
    
    def generate_query(self,input_parameters, filtered_schema, schema_name):
        table_name = self.extract_table_name(filtered_schema)
        print("Table Name:", table_name)
        
        question = f"""Generate an SQL query to retrieve `{input_parameters}` 
                    from the relevant database table `{table_name}`. Ensure:    
                    - Only use the column names specified in the list above. Do NOT add any extra columns.
                    - The correct table and column selection from the provided schema only.
                    - Use `DISTINCT` if uniqueness is implied.
                    -Don't use unnecessary JOINS"""
        
        
        model_path = 'gaussalgo/T5-LM-Large-text2sql-spider'
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # input_text = " ".join(["Question: ",question, "Schema:", schema_text])
        input_text = " ".join(["Question: ",question, "Schema:", "\n".join(filtered_schema)])
        
        
        model_inputs = tokenizer(input_text, return_tensors="pt")
        outputs = model.generate(**model_inputs, max_length=512)
        
        response_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        
        print("SQL Query:")
        print(response_text)
        
        # Clean SQL output
        response_text = self.clean_sql_output(response_text, schema_name)
        print("\n Cleaned SQL Query:-", response_text)
        return response_text
    
    
    
    def clean_sql_output(self,llm_output, schema_name):
        llm_output = llm_output[0] if isinstance(llm_output, list) else llm_output
        # Step 1: Remove any text before the first occurrence of "SELECT" (case-insensitive)
        # cleaned_output = re.sub(r"^.*?(?=SELECT)", "", llm_output, flags=re.IGNORECASE | re.DOTALL)
        cleaned_output = re.sub(r"^.*?(?=SELECT|WITH|INSERT|UPDATE|DELETE)", "", llm_output, flags=re.IGNORECASE | re.DOTALL)
    
        # Step 2: Remove all square brackets
        cleaned_output = re.sub(r"[\[\]]", "", cleaned_output)
        cleaned_output = re.sub(r"```", "", cleaned_output)
        cleaned_output = re.sub(r"@", "", cleaned_output)
        cleaned_output = re.sub(r"'", "", cleaned_output)
    
        cleaned_output = re.sub(r"JOIN\s+\w+\s+AS\s+\w+\s+ON\s+[^;]+", "", cleaned_output, flags=re.IGNORECASE)
    
        # This regex matches FROM/UPDATE/INTO/JOIN <table_name> (not already qualified)
        # def qualify_tables(match):
        #     keyword = match.group(1)
        #     table = match.group(2)
        #     if "." not in table:
        #         return f"{keyword} {schema_name}.{table}"
        #     return match.group(0)
    
        # cleaned_output = re.sub(r"\b(FROM|JOIN|UPDATE|INTO)\s+([a-zA-Z_][\w]*)", qualify_tables, cleaned_output, flags=re.IGNORECASE)
    
        cleaned_output = re.sub(r"sakila",f"{schema_name}", cleaned_output, flags=re.IGNORECASE)
    
        # Step 3: Ensure the query ends with a semicolon
        cleaned_output = cleaned_output.strip()
        if not cleaned_output.endswith(";"):
            cleaned_output += ";"
    
        return cleaned_output
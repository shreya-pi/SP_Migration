import re

def convert_column_names_to_strings(sql_file_path, output_file_path):
    with open(sql_file_path, 'r') as file:
        sql_content = file.read()
    
    # Regular expression to match column references like c.customer_id but not procedure names
    column_pattern = re.compile(r'(?<!\bPROCEDURE\s)(?<!\bFUNCTION\s)(?<!\bTABLE\s)(?<!\bVIEW\s)(?<!\bINDEX\s)([a-zA-Z_]+)\.([a-zA-Z_]+)')
    # Replace column names with quoted versions
    modified_sql = column_pattern.sub(lambda m: f"{m.group(1)}.\"{m.group(2)}\"", sql_content)
    
    with open(output_file_path, 'w') as output_file:
        output_file.write(modified_sql)
    
    return modified_sql

# Example usage
sql_file_path = 'sp_1.sql'  # Update this with your SQL file path
output_file_path = 'modified_procedure_1.sql'
modified_sql = convert_column_names_to_strings(sql_file_path, output_file_path)
print(f"Modified SQL saved to {output_file_path}")

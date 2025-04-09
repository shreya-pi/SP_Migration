import pyodbc
from config import SQL_SERVER_CONFIG 


def get_table_schema(cursor, database_name):
    query = f'''
    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
    FROM {database_name}.INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION;
    '''
    cursor.execute(query)
    return cursor.fetchall()

def preprocess_schema(schema_details):
    processed_schema = []
    table_columns = {}
    
    for row in schema_details:
        schema, table, column, data_type, is_nullable, max_length = row
        
        null_status = "NOT NULL" if is_nullable == "NO" else "NULL"
        length_info = f'({max_length})' if max_length else ''
        column_entry = f'{column} ({data_type.lower()}{length_info}, {null_status})'

        table= f'{schema}.{table}'
        
        if table not in table_columns:
            table_columns[table] = []
        table_columns[table].append(f'- {column_entry}')
    
    for table, columns in table_columns.items():
        processed_schema.append(f'Table: {table}')
        processed_schema.append('Columns:')
        processed_schema.extend(columns)
        processed_schema.append('')
    
    return processed_schema

def save_schema_to_file(schema_details, output_file):
    processed_schema = preprocess_schema(schema_details)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(processed_schema))


def main():
    server = SQL_SERVER_CONFIG["server"]  
    database = SQL_SERVER_CONFIG["database"] 
    username = SQL_SERVER_CONFIG["username"]  
    password =  SQL_SERVER_CONFIG["password"] 
    output_file = "schema.txt"  # Output file name
    
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        schema_details = get_table_schema(cursor, database)
        save_schema_to_file(schema_details, output_file)
        print(f"Schema details saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()

import re


class SchemaConverter:
    def convert_schema_format(self, file_path):
        with open("schema_1.txt", "r") as f:
            schema = f.read()
        
        
        # Split the schema into blocks for each table
        table_blocks = schema.strip().split("Table: ")
        formatted_output = []
        
        for block in table_blocks:
            if not block.strip():
                continue
        
            lines = block.strip().splitlines()
            table_name = f'"{lines[0].strip()}"'
            # table_name = lines[0].strip()
            output = [table_name]
        
            for line in lines[2:]:  # skip "Columns:" and table name line
                if not line.strip():
                    continue
                match = re.match(r"- (\w+)\s+\(([^,]+)", line.strip())
                if match:
                    col_name, col_type = match.groups()
                    # output.extend([col_name, col_type.strip()])
                    output.extend([f'"{col_name}"', col_type.strip()])
        
            formatted_output.append(" ".join(output))
        
        # Add [SEP] between tables
        final_output = " [SEP]\n".join(formatted_output)
        
        # Write to file
        with open(file_path, "w") as f:
            f.write(final_output)
        
        print("Schema has been written to 'formatted_schema.txt'")
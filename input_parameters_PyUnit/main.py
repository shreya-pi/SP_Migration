from filtered_schema import FilterSchema
from generate_query import GenerateQuery    
from execute_query import ExecuteQuery
from convert_schema_format import SchemaConverter
import json
import re


class AutomateTestInputs:

    def convert_schema_format(self, schema_text, converted_file_path):
        convert_schema_obj = SchemaConverter()
        convert_schema_obj.convert_schema_format(schema_text, converted_file_path)


    def filter_schema(self,input_parameters, schema_text):
        # input_parameters = "`customer_id`"       
        filter_schema_obj = FilterSchema()
        filtered_schema = filter_schema_obj.filter_schema(input_parameters, schema_text)
        return filtered_schema
    


    def generate_query(self, schema_name, input_parameters, filtered_schema):   
        generate_query_obj = GenerateQuery()    
        generated_query = generate_query_obj.generate_query(input_parameters, filtered_schema, schema_name)

        return generated_query



    def execute_query(self, generated_query, input_parameters, sf_schema, stored_procedure_name, file_name, call_statements):       
        execute_query_obj = ExecuteQuery()
        execute_query_obj.run(generated_query, input_parameters, file_name, call_statements, sf_schema, stored_procedure_name)



    def main(self):
        with open("sp_exp_1.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        schema_name = "dbo"

        file_name = "call_statements.json"

        call_statements = []

        sf_schema = "DB_SCHEMA"

        # Read schema from dataset.txt
        with open('schema.txt', 'r') as f:
            original_schema_text = f.read()

        converted_file_path = "formatted_schema.txt"
        # Convert schema format
        self.convert_schema_format(original_schema_text, converted_file_path)
  

        # Read schema from dataset.txt
        with open(converted_file_path, 'r') as f:
            schema_text = f.read()
        

        for sp_exp in data:
            stored_procedure_name = sp_exp["Stored Procedure Name:"]
            input_parameters = sp_exp["Input Parameters:"]
            input_parameters = re.findall(r"@(\w+)", input_parameters)
    
            filtered_schema = self.filter_schema(input_parameters, schema_text)

            generated_query = self.generate_query(schema_name, input_parameters, filtered_schema)

            self.execute_query(generated_query, input_parameters, sf_schema, stored_procedure_name, file_name, call_statements)




if __name__ == "__main__":
    pipeline = AutomateTestInputs()
    pipeline.main()




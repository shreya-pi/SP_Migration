import subprocess
from .log import log_info,log_error

class SnowConvertRunner:
    def __init__(self, input_path, output_path, schema_name, log_file):
        self.input_path = input_path
        self.output_path = output_path
        self.schema_name = schema_name
        self.log_file = log_file

    def run_snowct_command(self):
        """Executes the SnowConvert CLI command and logs the output."""
        command = [
            "snowct", "sql-server",
            "--input", self.input_path,
            "--output", self.output_path,
            "flag --assessment"
            # "--customschema", self.schema_name
            # "--database", database_name
        ]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self._write_log("Command executed successfully:\n" + result.stdout)
            log_info(f"Command executed successfully. Log saved to: {self.log_file}")
        except subprocess.CalledProcessError as e:
            self._write_log("Error executing command:\n" + e.stderr)
            log_error(f"Error executing command. Check log file: {self.log_file}")

    def _write_log(self, content):
        """Writes logs to the specified log file."""
        with open(self.log_file, "w") as log:
            log.write(content)




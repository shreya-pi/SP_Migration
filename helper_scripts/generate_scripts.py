import os
import subprocess
import time
from config import SQL_SERVER_CONFIG 
from .log import log_info,log_error

class SQLServerScripter:
    # def __init__(self, server, database, output_dir):
    #     """
    #     Initializes the SQL Server scripter with server details and output directory.
    #     """
    #     self.server = server
    #     self.database = database
    #     self.output_dir = output_dir
    #     os.makedirs(self.output_dir, exist_ok=True)  # Ensure output directory exists

    def __init__(self, output_dir):
        """
        Initializes the SQL Server scripter using config details.
        """
        self.server = SQL_SERVER_CONFIG["server"]
        self.database = SQL_SERVER_CONFIG["database"]
        self.username = SQL_SERVER_CONFIG["username"]
        self.password = SQL_SERVER_CONFIG["password"]

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)  # Ensure output directory exists

    def generate_powershell_script(self):
        """
        Generates the PowerShell script for scripting stored procedures.
        """
        return f"""
        try {{
        
            [System.Reflection.Assembly]::LoadWithPartialName('Microsoft.SqlServer.Smo') | Out-Null
            $srv = New-Object Microsoft.SqlServer.Management.Smo.Server "{self.server}"
            $srv.ConnectionContext.LoginSecure = $false
            $srv.ConnectionContext.Login = "{self.username}"
            $srv.ConnectionContext.Password = "{self.password}"
        
            
            if (-not $srv) {{
                throw "Could not connect to SQL Server instance: {self.server}"
            }}

            $db = $srv.Databases["{self.database}"]
            if (-not $db) {{
                throw "Database '{self.database}' not found on server '{self.server}'"
            }}

            $scripter = New-Object Microsoft.SqlServer.Management.Smo.Scripter($srv)

            # Configure scripting options
            $scripter.Options.ScriptDrops = $false
            $scripter.Options.WithDependencies = $false
            $scripter.Options.IncludeIfNotExists = $true
            $scripter.Options.Indexes = $false
            $scripter.Options.Triggers = $false
            $scripter.Options.ExtendedProperties = $false
            $scripter.Options.DriAllConstraints = $false
            $scripter.Options.IncludeHeaders = $false
            $scripter.Options.SchemaQualify = $true
            $scripter.Options.AnsiPadding = $true
            $scripter.Options.AnsiFile = $true  # Ensure ANSI format

            $path = "{self.output_dir}\\{self.database}"
            mkdir $path -ErrorAction SilentlyContinue

            $errorCount = 0

            # Script Stored Procedures
            foreach ($sp in $db.StoredProcedures) {{
                try {{
                    if (-not $sp.IsSystemObject) {{
                        $filename = "$path\\$($sp.Schema)_$($sp.Name).sql"

                        # Generate the script
                        $script = $scripter.Script($sp) -join "`r`n"

                        # Split script into lines
                        $lines = $script -split "`r`n"

                        # Find the index where the actual SQL procedure starts
                        $startIndex = ($lines | Select-String -Pattern "^(CREATE|ALTER)\s+PROCEDURE").LineNumber
                        if (-not $startIndex) {{
                            throw "Could not find CREATE or ALTER PROCEDURE statement in $($sp.Name)"
                        }}

                        # Extract everything from the first relevant SQL line onwards
                        $cleanScript = $lines[($startIndex - 1)..($lines.Length - 1)] -join "`r`n"

                        # Write to file in ANSI encoding
                        $cleanScript | Out-File -FilePath $filename -Encoding Default
                    }}
                }} catch {{
                    $errorCount += 1
                    Write-Error "Failed to generate script for stored procedure: $($sp.Name) - Error: $_"
                }}
            }}

            if ($errorCount -gt 0) {{
                throw "Some scripts failed to generate. Check the errors above."
            }}

            Write-Output "Scripts successfully generated at: $path"
        }} catch {{
            Write-Error "Script execution failed: $_"
        }}
        """

    def run_powershell_script(self):
        """Runs PowerShell script with a countdown and stops it after 60 seconds if it runs too long."""
        script = self.generate_powershell_script()
        log_info(f"⚡ Running PowerShell script")

        process = subprocess.Popen(["powershell", "-Command", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        start_time = time.time()
        timeout = 60  # ⏳ Max runtime in seconds

        while process.poll() is None:  # While process is running
            elapsed_time = int(time.time() - start_time)
            remaining_time = timeout - elapsed_time

            if remaining_time <= 0:
                process.terminate()  # 🔴 Gracefully stop the process
                log_info("\n⏳ Timeout: PowerShell script stopped after 60 seconds.")
                return

            print(f"⏳ Time remaining: {remaining_time}s", end="\r", flush=True)
            time.sleep(1)  # Wait before checking again

        stdout, stderr = process.communicate()
        if process.returncode == 0:
            log_info("\n✅ PowerShell script completed successfully!")
            log_info(stdout)
        else:
            # print(f"\n❌ PowerShell script failed. Error:\n{stderr}")
            log_error(f"\n❌ PowerShell script failed")
            log_error(stdout)

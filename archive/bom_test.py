
with open(r"processed_sp_1.sql", "rb") as file:
    raw = file.read()  # Read first 4 bytes

# Check for common BOM signatures
if raw.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
    print("File has a UTF-8 BOM")

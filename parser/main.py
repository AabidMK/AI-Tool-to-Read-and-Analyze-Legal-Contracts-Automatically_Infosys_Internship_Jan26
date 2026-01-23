print("MAIN FILE STARTED")

from file_parser import parse_file

print("IMPORT SUCCESS")

input_file = r"C:\Users\HP\Desktop\springboard\parser\basic-text.pdf"
output_file = "parsed_output/sample_file.txt"

parse_file(input_file, output_file)

print("File parsed and saved successfully")

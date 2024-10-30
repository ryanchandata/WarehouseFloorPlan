import csv

# Prompt the user to input the group name
group_name = input("Enter the group name: ")

# Define the CSV file path
csv_file = 'locations1.csv'

# Initialize the SQL update string
update_sql = ""

# Read the CSV file and generate individual SQL UPDATE statements
with open(csv_file, newline='') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        cell_code = row['cell_code']
        x = row['X']
        y = row['Y']
        z = row['Z']
        
        # Generate individual update statements without filtering by group
        update_sql += f"UPDATE cell_info SET x_coordinate = {x}, y_coordinate = {y}, z_coordinate = {z} WHERE cell_code = '{cell_code}';\n"

# Write the generated SQL to the output .sql file
with open('locations_update.sql', 'w') as sql_file:
    sql_file.write(update_sql)

print(f"Batch update SQL (for x, y, z) has been written to locations_update.sql")

import yaml
import requests

# Step 1: Fetch YAML content from the URL
url = "https://www.hepdata.net/download/table/ins2705044/Object%20Cut%20Flow%20Short%20Tracks/2/yaml"
response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"Failed to fetch YAML data. Status code: {response.status_code}")

yaml_content = response.text  # Get YAML content as text

# Step 2: Parse the YAML content
data = yaml.safe_load(yaml_content)

# Extract dependent variable (Efficiency or event count) and its name from YAML
dependent_variable_name = data["dependent_variables"][0]["header"]["name"].replace(" ", "_")  # Use YAML-specified name & replace spaces
table_name = f"{dependent_variable_name}_table"  # Format table name
table_type = dependent_variable_name

efficiency_values = []
err_minus = []
err_plus = []

for entry in data["dependent_variables"][0]["values"]:
    efficiency_values.append(entry["value"])

    # Checking errors
    if "errors" in entry:
        error_entry = entry["errors"][0]
        if "asymerror" in error_entry:
            err_minus.append(abs(error_entry["asymerror"]["minus"]))
            err_plus.append(error_entry["asymerror"]["plus"])
        elif "symerror" in error_entry:
            err_minus.append(error_entry["symerror"])
            err_plus.append(error_entry["symerror"])
        else:
            err_minus.append(0.0)
            err_plus.append(0.0)
    else:
        err_minus.append(0.0)
        err_plus.append(0.0)

# Extract independent variables
independent_variables = []
variable_names = []
for var in data["independent_variables"]:
    variable_names.append(var["header"]["name"])  # Store variable names
    independent_variables.append([entry["value"] for entry in var["values"]])  # Store values

# Generate min values for each independent variable
min_values = []
for var_values in independent_variables:
    min_values.append([0] + var_values[:-1])  # First min is 0, others are previous max

# Step 3: Write to an ADL file
adl_filename = "output.adl"

with open(adl_filename, "w") as adl_file:
    adl_file.write(f"table {table_name}\n")  # Use custom table name
    adl_file.write(f"tabletype {table_type}\n")
    adl_file.write(f"nvars {len(independent_variables)}\n")  # Number of independent variables
    adl_file.write("errors true\n")

    # Writing header with the correct dependent variable name
    header = f"# {dependent_variable_name:<12} {'err-':<12} {'err+':<12} " + " ".join(
        [f"{var}_Min".ljust(15) + f"{var}_Max".ljust(15) for var in variable_names]
    ) + "\n"
    adl_file.write(header)

    # Writing data with aligned columns
    for i in range(len(efficiency_values)):
        row = f"{efficiency_values[i]:<12.6f} {err_minus[i]:<12.4f} {err_plus[i]:<12.4f}"
        for j in range(len(independent_variables)):
          row += f" {float(min_values[j][i]):<15.3f} {float(independent_variables[j][i]):<15.3f}"
        adl_file.write(row + "\n")

print(f"ADL file '{adl_filename}' has been successfully created.")

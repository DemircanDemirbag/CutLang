import requests
import re

# Step 1: Fetch YODA content from the URL
url = "https://www.hepdata.net/download/table/ins2705044/Long%20tracks%3A%20number%20of%20b-tagged%20jets/2/yoda"  # Replace with actual YODA file URL
response = requests.get(url)

if response.status_code != 200:
    raise Exception(f"Failed to fetch YODA data. Status code: {response.status_code}")

yoda_content = response.text  # Get YODA content as text

# Step 2: Process YODA content (example: split into lines)
lines = yoda_content.split("\n")

# Step 2: Prepare containers
edges = []
values = []
errors_dn = []
errors_up = []
parsing_values = False
table_name = "default"

for line in lines:
    line = line.strip()

    # Table name
    if line.startswith("BEGIN YODA_BINNEDESTIMATE"):
        table_name = line.split()[-1].replace("/", "_")

    # Bin max edges
    if line.startswith("Edges(A1):"):
        match = re.search(r'\[([^\]]+)\]', line)
        if match:
            edge_parts = match.group(1).split(",")
            edges = [float(e.strip().strip('"')) for e in edge_parts]

    # Start of values + error reading
    if line.startswith("# value"):
        parsing_values = True
        continue

    # Read value + errDn + errUp from same line
    if parsing_values and line and not line.startswith("#") and "END" not in line:
        parts = line.split()

        # value
        val = parts[0]
        if val.lower() in ["---", "nan"]:
            continue

        values.append(float(val))

        # errDn
        if len(parts) >= 2:
            errdn = parts[1]
            errors_dn.append(0.0 if errdn in ["---", "nan"] else abs(float(errdn)))
        else:
            errors_dn.append(0.0)

        # errUp
        if len(parts) >= 3:
            errup = parts[2]
            errors_up.append(0.0 if errup in ["---", "nan"] else abs(float(errup)))
        else:
            errors_up.append(0.0)

# Step 3: Binning
max_vals = edges[:len(values)]
min_vals = [0.0] + max_vals[:-1]

# Step 4: Write ADL file
adl_filename = "output_from_yoda.adl"

with open(adl_filename, "w") as adl_file:
    adl_file.write(f"table {table_name}_table\n")
    adl_file.write(f"tabletype {table_name}\n")
    adl_file.write("nvars 1\n")
    adl_file.write("errors true\n")
    adl_file.write("# {0:<12} {1:<12} {2:<12} {3:<12} {4:<12}\n".format("eff", "err-", "err+", "Min", "Max"))

    n = min(len(values), len(errors_dn), len(errors_up), len(min_vals), len(max_vals))
    for i in range(n):
        adl_file.write(
            "{0:<12.6e} {1:<12.4f} {2:<12.4f} {3:<12.3f} {4:<12.3f}\n".format(values[i], errors_dn[i], errors_up[i],
                                                                              min_vals[i], max_vals[i]))

print(f"ADL file '{adl_filename}' has been successfully created from YODA.")
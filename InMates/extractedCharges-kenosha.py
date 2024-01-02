import pandas as pd
import json

# Load the CSV file
df = pd.read_csv('/Users/vikas/builderspace/scrapping/InMates/kenosha.csv')

# Define a function to parse the charges column
def parse_charges(charges_str):
    try:
        return json.loads(charges_str.replace("'", '"'))
    except json.JSONDecodeError:
        return []

# Apply the parsing function to the charges column
df['charges'] = df['charges'].apply(parse_charges)

# Create a new DataFrame for the extracted data
extracted_data = []

# Iterate over each row and extract each charge
for index, row in df.iterrows():
    for charge in row['charges']:
        # Extract each attribute of the charge into its own column
        charge_data = {
            'jailID': row['jailID'],
            'charge': charge.get('charge', ''),
            'courtFile': charge.get('courtFile', ''),
            'bondOrFine': charge.get('bondOrFine', ''),
            'dispositionDate': charge.get('dispositionDate', ''),
            'dispositionOfCharge': charge.get('dispositionOfCharge', '')
        }
        extracted_data.append(charge_data)

# Convert the list of dictionaries to a DataFrame
df_extracted = pd.DataFrame(extracted_data)

# Save the new dataframe to a CSV file
df_extracted.to_csv('/Users/vikas/builderspace/scrapping/InMates/extracted_charges.csv', index=False)

print('Data extracted and saved to extracted_data.csv')

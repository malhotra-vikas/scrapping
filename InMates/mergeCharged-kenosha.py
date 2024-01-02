import pandas as pd

# Load the CSV files
file1 = pd.read_csv('/Users/vikas/builderspace/scrapping/InMates/kenosha.csv')
file2 = pd.read_csv('/Users/vikas/builderspace/scrapping/InMates/extracted_charges.csv')

print(file1.head())
print(file2.head())

# Merge the files on 'jailID'
merged_file = pd.merge(file1, file2, on='jailID', how='inner')

# Save the merged file
merged_file.to_csv('/Users/vikas/builderspace/scrapping/InMates/ready_kenosha.csv', index=False)

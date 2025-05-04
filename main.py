import requests
from tqdm import tqdm

INPUT_FILE = "address.txt"
OUTPUT_FILE = "result.txt"

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def is_numeric_field(value):
    try:
        float(value)
        return True
    except:
        return False

# Read addresses from the file
with open(INPUT_FILE, "r") as f:
    addresses = [line.strip() for line in f if line.strip()]

# Initialize summary variables
grand_total = 0.0
claimed_total = 0.0
address_totals = []

# Prepare a list to store address and total allocation
address_data = []

# Open the output file to write the results
with open(OUTPUT_FILE, "w") as f:
    # Write the header
    f.write("Address | Total Allocation (Jager)\n")
    f.write("-------------------------------\n")

    # Using tqdm to show progress for processing each address
    for address in tqdm(addresses, desc="Processing Addresses", unit="address"):
        url = f"https://api.jager.meme/api/airdrop/queryAirdrop/{address}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", {})

            # Check if the airdrop is claimed and calculate the total sum
            total_sum = 0.0
            claimed = data.get("claimed", False)

            # Sum all numeric fields for this address
            for key, value in data.items():
                if is_numeric_field(value):
                    total_sum += safe_float(value)

            # Apply rounding to the total sum to ensure no extra decimals
            total_sum = round(total_sum, 2)  # Round to 2 decimal places

            # If total allocation is non-zero, include in the results
            if total_sum > 0:
                # Append the address and its total to the address_data list
                address_data.append((address, total_sum))

                # Add to grand total
                grand_total += total_sum
                address_totals.append(total_sum)

        except Exception as e:
            # Skip addresses with errors or issues retrieving data
            continue

    # Sort address data by total allocation in descending order
    address_data.sort(key=lambda x: (x[1] if isinstance(x[1], (int, float)) else 0), reverse=True)

    # Write sorted results to the output file
    for address, total in address_data:
        f.write(f"{address} | {total:,.2f}\n")

    # Summary: Write the Grand Total and other stats
    f.write("\nSUMMARY:\n")
    f.write("-------------------------------\n")
    f.write(f"Total Addresses Elig: {len(address_data)}\n")
    f.write(f"Grand Total Allocation (Jager): {grand_total:,.2f}\n")
    f.write(f"Average Allocation per Address: {grand_total / len(address_data) if len(address_data) > 0 else 0:,.2f}\n")
    f.write(f"Maximum Allocation (Jager): {max(address_totals) if address_totals else 0:,.2f}\n")
    f.write(f"Minimum Allocation (Jager): {min(address_totals) if address_totals else 0:,.2f}\n")

print(f"Results and summary written to '{OUTPUT_FILE}'")

import csv
from datetime import datetime
from typing import List, Dict

def parse_csv(file_path: str) -> List[Dict]:
    """
    Parses a CSV file with headers 'Date', 'Description', 'Amount'.
    Normalizes Date to ISO format (YYYY-MM-DD) and Amount to float.
    """
    transactions = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        # Handle case-insensitive headers
        fieldnames = reader.fieldnames
        if not fieldnames:
            return []
        
        header_map = {}
        for f in fieldnames:
            lowered = f.lower().strip()
            if lowered == 'date':
                header_map['Date'] = f
            elif lowered == 'description':
                header_map['Description'] = f
            elif lowered == 'amount':
                header_map['Amount'] = f
        
        required = {'Date', 'Description', 'Amount'}
        if not required.issubset(header_map.keys()):
            missing = required - header_map.keys()
            raise ValueError(f"CSV missing required headers: {missing}")

        for row in reader:
            # Normalize Date
            raw_date = row[header_map['Date']].strip()
            normalized_date = ""
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    normalized_date = datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            
            if not normalized_date:
                raise ValueError(f"Could not parse date: {raw_date}")
            
            # Normalize Amount
            raw_amount_val = row[header_map['Amount']]
            try:
                # Remove any currency symbols or commas if they exist
                raw_amount = raw_amount_val.replace('$', '').replace(',', '').strip()
                normalized_amount = float(raw_amount)
            except ValueError:
                raise ValueError(f"Could not parse amount: {raw_amount_val}")
            
            transactions.append({
                "date": normalized_date,
                "description": row[header_map['Description']].strip(),
                "amount": normalized_amount
            })
    return transactions

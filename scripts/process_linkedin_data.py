#!/usr/bin/env python3
"""
Process LinkedIn JSON files and convert to CSV for Salesforce import
"""

import json
import csv
import os
import glob
from datetime import datetime
from pathlib import Path

def load_json_file(filepath):
    """Load and parse a JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_experience(experiences):
    """Convert experience list to a single string for CSV"""
    if not experiences:
        return ''
    
    exp_strings = []
    for exp in experiences:
        exp_str = f"{exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
        exp_strings.append(exp_str)
    
    return ' | '.join(exp_strings)

def flatten_education(educations):
    """Convert education list to a single string for CSV"""
    if not educations:
        return ''
    
    edu_strings = []
    for edu in educations:
        edu_str = f"{edu.get('school', '')} - {edu.get('degree', '')} ({edu.get('years', '')})"
        edu_strings.append(edu_str)
    
    return ' | '.join(edu_strings)

def get_latest_experience(experiences):
    """Extract the most recent experience"""
    if not experiences:
        return {'current_role': '', 'current_company': ''}
    
    latest = experiences[0]  # Assuming first is most recent
    return {
        'current_role': latest.get('role', ''),
        'current_company': latest.get('company', '')
    }

def process_json_files(input_dir, output_csv):
    """Process all JSON files in directory and subdirectories"""
    
    # Find all LinkedIn JSON files (including in subdirectories)
    json_files = []
    
    # Check main directory
    pattern = os.path.join(input_dir, 'linkedin_*.json')
    json_files.extend(glob.glob(pattern))
    
    # Check LinkedIn_Profiles subdirectory if it exists
    linkedin_dir = os.path.join(input_dir, 'LinkedIn_Profiles')
    if os.path.exists(linkedin_dir):
        # Search recursively in subdirectories
        for root, dirs, files in os.walk(linkedin_dir):
            for file in files:
                if file.startswith('linkedin_') and file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
    
    if not json_files:
        print(f"No LinkedIn JSON files found in {input_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Prepare CSV headers
    headers = [
        'Profile ID',
        'Full Name',
        'First Name',
        'Last Name',
        'Headline',
        'Location',
        'LinkedIn URL',
        'About',
        'Current Role',
        'Current Company',
        'All Experience',
        'All Education',
        'Connections',
        'Extraction Date'
    ]
    
    # Process files and write to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for json_file in json_files:
            try:
                data = load_json_file(json_file)
                
                # Parse name
                full_name = data.get('name', '')
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Get latest experience
                latest_exp = get_latest_experience(data.get('experience', []))
                
                # Create row
                row = {
                    'Profile ID': data.get('profileId', ''),
                    'Full Name': full_name,
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Headline': data.get('headline', ''),
                    'Location': data.get('location', ''),
                    'LinkedIn URL': data.get('url', ''),
                    'About': data.get('about', '')[:500],  # Limit to 500 chars
                    'Current Role': latest_exp['current_role'],
                    'Current Company': latest_exp['current_company'],
                    'All Experience': flatten_experience(data.get('experience', [])),
                    'All Education': flatten_education(data.get('education', [])),
                    'Connections': data.get('connections', ''),
                    'Extraction Date': data.get('timestamp', '')
                }
                
                writer.writerow(row)
                print(f"✓ Processed: {full_name}")
                
            except Exception as e:
                print(f"✗ Error processing {json_file}: {str(e)}")
    
    print(f"\nCSV file created: {output_csv}")
    print(f"Total profiles processed: {len(json_files)}")

def create_salesforce_ready_csv(input_csv, output_csv):
    """Create a Salesforce-ready CSV with proper field mapping"""
    
    # Salesforce field mapping (adjust based on your Salesforce setup)
    salesforce_mapping = {
        'FirstName': 'First Name',
        'LastName': 'Last Name',
        'Title': 'Current Role',
        'Company': 'Current Company',
        'Description': 'About',
        'LeadSource': 'LinkedIn',
        'Website': 'LinkedIn URL',
        'Email': '',  # You'll need to add emails separately
        'Phone': '',  # You'll need to add phones separately
    }
    
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=salesforce_mapping.keys())
            writer.writeheader()
            
            for row in reader:
                sf_row = {}
                for sf_field, csv_field in salesforce_mapping.items():
                    if csv_field and csv_field in row:
                        sf_row[sf_field] = row[csv_field]
                    elif sf_field == 'LeadSource':
                        sf_row[sf_field] = 'LinkedIn'
                    else:
                        sf_row[sf_field] = ''
                
                writer.writerow(sf_row)
    
    print(f"Salesforce-ready CSV created: {output_csv}")

if __name__ == "__main__":
    # Configuration
    downloads_dir = str(Path.home() / "Downloads")
    output_dir = os.getcwd()
    
    # Generate filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    general_csv = os.path.join(output_dir, f"linkedin_profiles_{timestamp}.csv")
    salesforce_csv = os.path.join(output_dir, f"salesforce_import_{timestamp}.csv")
    
    # Process JSON files
    print("LinkedIn Profile Processor")
    print("=" * 40)
    print(f"Looking for JSON files in: {downloads_dir}")
    print(f"Output directory: {output_dir}\n")
    
    # Create general CSV
    process_json_files(downloads_dir, general_csv)
    
    # Create Salesforce-ready CSV
    if os.path.exists(general_csv):
        create_salesforce_ready_csv(general_csv, salesforce_csv)
        print(f"\nFiles created:")
        print(f"1. General CSV: {general_csv}")
        print(f"2. Salesforce CSV: {salesforce_csv}")
        print("\nYou can now import the Salesforce CSV into your CRM!")
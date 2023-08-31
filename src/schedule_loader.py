from src.schedule_parser import extract_schedule
# from schedule_parser import extract_schedule # for testing

import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_file_expired(filepath, filename_prefix, expiration_hours):
    """Check if the file is expired based on filename."""
    files_in_directory = [f for f in os.listdir(filepath) if f.startswith(filename_prefix)]
    
    if not files_in_directory:
        return True  # If directory is empty, file is expired
    
    latest_file = max(files_in_directory)
    file_timestamp = datetime.strptime(latest_file.split('_')[-1].split('.')[0], '%Y%m%d%H%M%S')
    expiration_time = datetime.now() - timedelta(hours=expiration_hours)
    
    return file_timestamp < expiration_time

def get_current_timestamp():
    """Get the current timestamp as a formatted string."""
    return datetime.now().strftime('%Y%m%d%H%M%S')

def read_or_download_schedule(url, expiration_hours=24):
    """Read or download schedule data based on file expiration."""

    filename_prefix = 'schedule_data'
    city = url.split('.')[0].split('/')[-1]
    base_filepath = 'schedules'
    filepath = os.path.join(base_filepath, city)

    if not os.path.exists(base_filepath):
        os.makedirs(base_filepath)
        logging.info(f'Created directory: {base_filepath}')

    if not os.path.exists(filepath):
        os.makedirs(filepath)
        logging.info(f'Created directory: {filepath}')

    files_in_directory = [f for f in os.listdir(filepath) if f.startswith('schedule_data')]


    files_in_directory = [f for f in os.listdir(filepath) if f.startswith(filename_prefix)]
    if not files_in_directory:
        logging.info('No files found in the directory. Creating a new file...')
        current_timestamp = get_current_timestamp()
        json_filename = f'{filename_prefix}_{current_timestamp}.json'
        full_path = os.path.join(filepath, json_filename)
        
        # Call extract_schedule function to get new data
        schedule_data = extract_schedule(url)
        
        # Save new data to file
        with open(full_path, 'w') as file:
            json.dump(schedule_data, file)
        logging.info(f'New data downloaded and saved to {full_path}')
    else:
        latest_file = max(files_in_directory)
        full_path = os.path.join(filepath, latest_file)
        if is_file_expired(filepath, filename_prefix, expiration_hours):
            # Logging: File expired, downloading new data...
            logging.info('File is expired, downloading new data...')
            
            # Call extract_schedule function to get new data
            schedule_data = extract_schedule(url)
            
            # Save new data to file
            new_timestamp = get_current_timestamp()
            new_filename = f'{filename_prefix}_{new_timestamp}.json'
            new_full_path = os.path.join(filepath, new_filename)
            with open(new_full_path, 'w') as file:
                json.dump(schedule_data, file)
            logging.info(f'New data downloaded and saved to {new_full_path}')
            
            # Remove old file
            os.remove(full_path)
            logging.info(f'Removed old file: {full_path}')
        else:
            # Logging: File not expired, reading existing data...
            logging.info('File is not expired, reading existing data...')
            with open(full_path, 'r') as file:
                schedule_data = json.load(file)
            logging.info(f'Existing data read from {full_path}')
            
            # Remove other files
            for file in files_in_directory:
                if file != latest_file:
                    os.remove(os.path.join(filepath, file))
                    logging.info(f'Removed old file: {file}')

    return schedule_data

# url = "https://moscow.quizplease.ru/schedule"
# schedule = read_or_download_schedule(url)
# print(schedule[0])

import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

filename_prefix = 'schedule_data'
base_filepath = 'schedules'

def is_file_expired(filepath: str, filename_prefix: str, expiration_hours: int):
    """Check if the file is expired based on filename."""
    files_in_directory = [f for f in os.listdir(filepath) if f.startswith(filename_prefix)]
    
    if not files_in_directory:
        return True  # If directory is empty, file is expired
    
    latest_file = max(files_in_directory)
    file_timestamp = datetime.strptime(latest_file.split('_')[-1].split('.')[0], '%Y%m%d%H%M%S')
    expiration_time = datetime.utcnow() - timedelta(hours=expiration_hours)
    
    return file_timestamp < expiration_time

def get_current_timestamp():
    """Get the current timestamp as a formatted string."""
    return datetime.utcnow().strftime('%Y%m%d%H%M%S')

def is_schedule_expired(uploaded_timestamp: str, city: str):
    filepath = os.path.join(base_filepath, city)
    files_in_directory = [f for f in os.listdir(filepath) if f.startswith(filename_prefix)]
    latest_file = max(files_in_directory)
    latest_file_timestamp = latest_file.split('.')[0].split('_')[-1]
    return latest_file_timestamp >= uploaded_timestamp


def download_schedule(url, filepath, filename_prefix):
    # Call extract_schedule function to get new data
    schedule_data = extract_schedule(url)
    
    # Save new data to file
    new_timestamp = get_current_timestamp()
    new_filename = f'{filename_prefix}_{new_timestamp}.json'
    new_full_path = os.path.join(filepath, new_filename)
    with open(new_full_path, 'w') as file:
        json.dump(schedule_data, file, default=lambda x: x.name if isinstance(x, GameType) else x)
    logger.info(f'New data downloaded and saved to {new_full_path}')
    return schedule_data, new_timestamp

def read_or_download_schedule(url, expiration_hours=24):
    """Read or download schedule data based on file expiration."""

    
    city = url.split('.')[0].split('/')[-1]
    filepath = os.path.join(base_filepath, city)

    if not os.path.exists(base_filepath):
        os.makedirs(base_filepath)
        logger.info(f'Created directory: {base_filepath}')

    if not os.path.exists(filepath):
        os.makedirs(filepath)
        logger.info(f'Created directory: {filepath}')


    files_in_directory = [f for f in os.listdir(filepath) if f.startswith(filename_prefix)]
    if not files_in_directory:
        logger.info('No files found in the directory. Creating a new file...')
        schedule_data, timestamp = download_schedule(url, filepath, filename_prefix)
    else:
        latest_file = max(files_in_directory)
        full_path = os.path.join(filepath, latest_file)
        if is_file_expired(filepath, filename_prefix, expiration_hours):
            # logger: File expired, downloading new data...
            logger.info('File is expired, downloading new data...')
            
            schedule_data, timestamp = download_schedule(url, filepath, filename_prefix)
            
            # Remove old file
            os.remove(full_path)
            logger.info(f'Removed old file: {full_path}')
        else:
            # logger: File not expired, reading existing data...
            logger.info('File is not expired, reading existing data...')
            timestamp = latest_file.split('.')[0].split('_')[-1]
            with open(full_path, 'r') as file:
                schedule_data = json.load(file)
            logger.info(f'Existing data read from {full_path}')
            
            # Remove other files
            for file in files_in_directory:
                if file != latest_file:
                    os.remove(os.path.join(filepath, file))
                    logger.info(f'Removed old file: {file}')
        
        for game in schedule_data:
            for key, _ in game.items():
                if key == 'type' and isinstance(game[key], str):
                    # game_type = GameType[game[key]]
                    game_type = getattr(GameType, game[key])
                    game.update({'type': game_type})

    return schedule_data, timestamp

# url = "https://moscow.quizplease.ru/schedule"
# schedule = read_or_download_schedule(url)
# print(schedule[0])

    
if __name__ != "__main__":
    from src.schedule_parser import extract_schedule, GameType
else:
    from schedule_parser import extract_schedule, GameType # for testing
    schedule, timestamp = read_or_download_schedule("https://moscow.quizplease.ru/schedule", expiration_hours=24)
    for game in schedule:
        print(game['title'])
    
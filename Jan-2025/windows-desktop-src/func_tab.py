from datetime import datetime
import pandas as pd
import os
import csv


def data_extraction(mfpt_container, file_path, file_name):

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_file_name = f'{file_name}_{current_time}.csv'

    full_path = os.path.join(file_path, full_file_name)

    rows = []
    for pair in mfpt_container:
        w_param = None
        mfpt = None
        for entry in pair:
            if entry.startswith('W: '):
                w_param = entry.split(': ')[1]
            elif entry.startswith('MFPT: '):
                mfpt = entry.split(': ')[1]
        rows.append([w_param, mfpt])

    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['W', 'MFPT'])
        writer.writerow(rows)

    print(f'CSV file saved at: {full_path}, for time: {current_time}')


def data_extraction_pandas(mfpt_container, file_path, file_name):
    w_values = []
    mfpt_values = []
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_file_name = f'{file_name}_{current_time}.csv'

    for entry in mfpt_container:
        for item in entry:
            if 'W:' in item:
                w_values.append(float(item.split(':')[1]))
            if 'MFPT:' in item:
                mfpt_values.append(float(item.split(':')[1]))
    df = pd.DataFrame({
        'W': w_values,
        'MFPT': mfpt_values
    })

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    df.to_csv(os.path.join(file_path, full_file_name), sep=',', index=False)


def create_directory(filepath, directory_name):

    directory_path = os.path.join(filepath, directory_name)

    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory '{directory_name}' created-successfully at {filepath}.")
        return directory_path
    except Exception as e:
        print(f"An error occurred while creating the directory: {e}")

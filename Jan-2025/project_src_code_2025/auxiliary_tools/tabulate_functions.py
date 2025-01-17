from . import datetime, pd, os


# general use function for any two-dimensional data frame using analogous xy coordinates.
# note, this only works for a specific format where the data is provided as {x1:y1, x2:y2, ... ,xn:yn}

def produce_csv_from_xy(data_array, xlab, ylab, file_path, file_name):
    x_values = []
    y_values = []
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_file_name = f'{file_name}_{current_time}.csv'

    for entry in data_array:
        for item in entry:
            if xlab in item:
                x_values.append(float(item.split(':')[1]))
            if ylab in item:
                y_values.append(float(item.split(':')[1]))

    df = pd.DataFrame({
        xlab: x_values,
        ylab: y_values
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
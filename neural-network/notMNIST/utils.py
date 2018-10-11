from urllib.request import urlretrieve
import os
from zipfile import ZipFile
from tqdm import tqdm
import numpy as np
from PIL import Image
from sklearn.preprocessing import LabelBinarizer
import pickle
from sklearn.model_selection import train_test_split

train_file_url = 'https://s3.amazonaws.com/udacity-sdc/notMNIST_train.zip'
test_file_url = 'https://s3.amazonaws.com/udacity-sdc/notMNIST_test.zip'
train_filename = 'notMNIST_train.zip'
test_filename = 'notMNIST_test.zip'


def download_data(url, filename):
    ''' Download data from URL.
    Args:
        url: URL to get file from
        filename: filename to save as

    Returns:
        nothing
    '''
    if not os.path.isfile(filename):
        urlretrieve(url, filename)
        print('[INFO] Zip files has been downloaded!')
    else:
        print('[INFO] Zip files has already existed!')


def uncompress_features_labels(filename):
    ''' Uncompress downloaded zip file to features and labels.
    Args:
        filename: filename to uncompress

    Returns:
        features: features with shape [num_of_files, feature_size]
        labels: labels with shape [num_of_files, label_size]
    '''
    features = []
    labels = []

    with ZipFile(filename) as zipf:
        filenames_pbar = tqdm(zipf.namelist(), unit='files')

        for filename in filenames_pbar:
            if not filename.endswith('/'):
                with zipf.open(filename) as image_file:
                    image = Image.open(image_file)
                    image.load()

                    feature = np.array(image, dtype=np.float32).flatten()

                label = os.path.split(filename)[1][0]

                features.append(feature)
                labels.append(label)
    print('[INFO] Features and labels uncompressed!')
    return np.array(features), np.array(labels)


def normalize_grayscale(image_data, a=-1, b=1):
    ''' Normalize pixel value to range [a, b].
    Args:
        image_data: image data with shape [num_of_files, feature_size]
        a: lower band
        b: upper band

    Returns:
        image_data normalized to [a, b]
    '''
    xmin = 0
    xmax = 255
    print('[INFO] Image normalized!')
    return 0.1 + (image_data - xmin) * (b - a) / (xmax - xmin)


def binarize_label(labels):
    ''' Binarize label from string values to sparse arrays.
    Args:
        labels: label data as string values

    Returns:
        label data as sparse arrays of float32
    '''
    encoder = LabelBinarizer()
    encoder.fit(labels)
    labels = encoder.transform(labels)
    print('[INFO] Label binarized!')
    return labels.astype(np.float32)


def dump_to_pickle(data, filename):
    ''' Save processed data to pickle file for future use.
    Args:
        data: processed data as a Dict
        filename: pickle filename to dump

    Returns:
        nothing
    '''
    with open(filename, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    print('[INFO] Data dumped to pickle file at {}.'.format(filename))


def process_data(filename):
    ''' Process data for training and testing,
    including all necessary steps above.

    Args:
        data: processed data as a Dict
        filename: pickle filename to dump

    Returns:
        nothing
    '''
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        print('[INFO] Data successfully loaded!')
        return (data['train_features'], data['train_labels']), (data['valid_features'], data['valid_labels']), (data['test_features'], data['test_labels'])

    else:
        download_data(train_file_url, train_filename)
        download_data(test_file_url, test_filename)

        train_features, train_labels = uncompress_features_labels(
            train_filename)
        test_features, test_labels = uncompress_features_labels(test_filename)

        train_features = normalize_grayscale(train_features)
        test_features = normalize_grayscale(test_features)

        train_labels = binarize_label(train_labels)
        test_labels = binarize_label(test_labels)

        train_features, valid_features, train_labels, valid_labels = train_test_split(
            train_features, train_labels,
            test_size=0.1)

        data = {
            'train_features': train_features,
            'train_labels': train_labels,
            'valid_features': valid_features,
            'valid_labels': valid_labels,
            'test_features': test_features,
            'test_labels': test_labels
        }
        dump_to_pickle(data, filename)
        print('[INFO] Data successfully loaded!')
        return (train_features, train_labels), (valid_features, valid_labels), (test_features, test_labels)
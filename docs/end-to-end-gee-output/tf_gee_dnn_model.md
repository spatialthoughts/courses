## Deep Neural Network Classification with Google Earth Engine

Adapted from https://developers.google.com/earth-engine/guides/tf_examples#multi-class-prediction-with-a-dnn

This notebook shows how to build, train and use a DNN model for multi-class classification on satellite imagery using Tensorflow and Keras.

The training points and Sentinel-2 composite are created in Google Earth Engine. The region in the Arkavathy River Basin in South India. We aim to carry out a landcover in 4 classes: Urban, Bare, Water and Vegetation using an offline training and prediction workflow.

![Classification Results](https://courses.spatialthoughts.com/images/end_to_end_gee/tf_classification.png)


#### Installation and Imports




#### Configuration

The following cells define the configuration options and GCS paths. You will have to change them to appropriate values for your own account.


```python
PROJECT = 'deep-learning-287813'
REGION = 'us-central1'

FEATURE_NAMES = [ 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12', 'landcover']
BANDS = [ 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']

LABEL = 'landcover'
N_CLASSES = 4
TRAIN_FILE_PATH = 'gs://earthengine-tf/arkavathy_training.tfrecord.gz'
TEST_FILE_PATH = 'gs://earthengine-tf/arkavathy_testing.tfrecord.gz'
MODEL_DIR = 'gs://earthengine-tf/arkavathy_model'
MODEL_NAME = 'arkavathy_tf_model'
VERSION_NAME = 'v1'
EXPORTED_IMAGE_PREFIX = 'arkavathy_image'
OUTPUT_IMAGE_FILE = 'gs://earthengine-tf/arkavathy_tf_classified.TFRecord'
OUTPUT_ASSET_ID = 'users/ujavalgandhi/tf/arkavathy_classified_dnn'

```


```python
import tensorflow as tf
from tensorflow import keras
import numpy as np
import ee
import json
```

#### Initialization


Authnenticate and initialize GEE API. This needs to done once per colab session.


```python
cloud_project = PROJECT

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)
```

## Data Pre-Processing

The training data for our model is in the TFRecord format and stored on GCS. As we are using Keras API, we need to parse the data and convert it into tuples.


```python
# Create a dataset from the TFRecord file in Cloud Storage.
train_dataset = tf.data.TFRecordDataset(TRAIN_FILE_PATH, compression_type='GZIP')
# Print the first record to check.
iter(train_dataset).next()
```


```python
# List of fixed-length features, all of which are float32.
columns = [
  tf.io.FixedLenFeature(shape=[1], dtype=tf.float32) for k in FEATURE_NAMES
]

# Dictionary with names as keys, features as values.
features_dict = dict(zip(FEATURE_NAMES, columns))

def parse_tfrecord(example_proto):
  """The parsing function.

  Read a serialized example into the structure defined by featuresDict.

  Args:
    example_proto: a serialized Example.

  Returns:
    A tuple of the predictors dictionary and the label, cast to an `int32`.
  """
  parsed_features = tf.io.parse_single_example(example_proto, features_dict)
  labels = parsed_features.pop(LABEL)
  return parsed_features, tf.cast(labels, tf.int32)

# Map the function over the dataset.
parsed_dataset = train_dataset.map(parse_tfrecord, num_parallel_calls=5)

# Print the first parsed record to check.
iter(parsed_dataset).next()

```


```python
# Keras requires inputs as a tuple.  Note that the inputs must be in the
# right shape.  Also note that to use the categorical_crossentropy loss,
# the label needs to be turned into a one-hot vector.
def to_tuple(inputs, label):
  return (tf.transpose(list(inputs.values())),
          tf.one_hot(indices=label, depth=N_CLASSES))

# Map the to_tuple function
input_dataset = parsed_dataset.map(to_tuple)
iter(input_dataset).next()
```

The dataset is now in the correct shape to be used with Keras

## Building and Training the DNN

We will use a simple DNN architecture with 1 input layer, 1 hidden-layer and 1 output layer.


* **Input Layer**: The training data contains 12 input band values, so the input will be an array of 12 values.
* **Hidden Layer**: 64-nodes with ReLU activation function and 0.2 dropout rate.
* **Output Layer**:  4 nodes with softmax activation to predict the class probability of each input.

> The dropout layer will set the output of 20% of the nodes from the hidden layer to 0 for each epoch. Dropout layers help in avoiding overfitting.

![Architecture](https://courses.spatialthoughts.com/images/end_to_end_gee/dnn_architecture.png)



```python
# Define the layers in the model.
model = tf.keras.models.Sequential([
  tf.keras.layers.Dense(64, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(N_CLASSES, activation=tf.nn.softmax)
])

# Compile the model with the specified loss function.
model.compile(optimizer=tf.keras.optimizers.Adam(),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Shuffle the training and data and create a batch
# 8 training samples per batch
input_dataset = input_dataset.shuffle(64).batch(8)

# Fit the model to the training data.
model.fit(x=input_dataset, epochs=50)
```


```python
model.summary()
```

Check model accuracy on the validation fraction.


```python
test_dataset = (
  tf.data.TFRecordDataset(TEST_FILE_PATH, compression_type='GZIP')
    .map(parse_tfrecord, num_parallel_calls=5)
    .map(to_tuple)
    .batch(8))

model.evaluate(test_dataset)
```


```python
model.save(MODEL_DIR, save_format='tf')
```

## Classifying the Image

We will now use the DNN model to predict the output class for all pixels of the input image. The input composite for the entire basin has been exported to GCS. We will read the image and run prediction for each image path.

When you export an image from Earth Engine as TFRecords, you get 2 files


*   `.tfrecord.gz` files containing image patches
*   `mixer.json` file containing image metadata and georeferencing information




```python
# Get a list of all the files in the output bucket.
files_list = !gsutil ls 'gs://earthengine-tf'

# Get only the files generated by the image export.
exported_files_list = [s for s in files_list if EXPORTED_IMAGE_PREFIX in s]

# Get the list of image files and the JSON mixer file.
image_files_list = []
json_file = None
for f in exported_files_list:
  if f.endswith('.tfrecord.gz'):
    image_files_list.append(f)
  elif f.endswith('.json'):
    json_file = f

```


```python
# Make sure the files are in the right order.
image_files_list.sort()

image_files_list

```


```python

# Load the contents of the mixer file to a JSON object.
json_text = !gsutil cat {json_file}
# Get a single string w/ newlines from the IPython.utils.text.SList
mixer = json.loads(json_text.nlstr)
mixer
```


```python
# Get relevant info from the JSON mixer file.
patch_width = mixer['patchDimensions'][0]
patch_height = mixer['patchDimensions'][1]
patches = mixer['totalPatches']
patch_dimensions_flat = [patch_width * patch_height, 1]

# Note that the tensors are in the shape of a patch, one patch for each band.
image_columns = [
  tf.io.FixedLenFeature(shape=patch_dimensions_flat, dtype=tf.float32)
    for k in BANDS
]

# Parsing dictionary.
image_features_dict = dict(zip(BANDS, image_columns))

# Note that you can make one dataset from many files by specifying a list.
image_dataset = tf.data.TFRecordDataset(end-to-end-gee-output/image_files_list, compression_type='GZIP')

# Parsing function.
def parse_image(example_proto):
  return tf.io.parse_single_example(example_proto, image_features_dict)

# Parse the data into tensors, one long tensor per patch.
image_dataset = image_dataset.map(parse_image, num_parallel_calls=5)

# Break our long tensors into many little ones.
image_dataset = image_dataset.flat_map(
  lambda features: tf.data.Dataset.from_tensor_slices(features)
)

# Turn the dictionary in each record into a tuple without a label.
image_dataset = image_dataset.map(
  lambda data_dict: (tf.transpose(list(data_dict.values())), )
)
```


```python
# Turn each patch into a batch.
image_dataset = image_dataset.batch(patch_width * patch_height)

iter(image_dataset).next()
```


```python
# Run prediction in batches, with as many steps as there are patches.
predictions = model.predict(image_dataset, steps=patches, verbose=1)
```


```python
# Note that the predictions come as a numpy array.  Check the first one.
print(predictions[0])
```


```python
# Instantiate the writer.
writer = tf.io.TFRecordWriter(OUTPUT_IMAGE_FILE)

# Every patch-worth of predictions we'll dump an example into the output
# file with a single feature that holds our predictions. Since our predictions
# are already in the order of the exported data, the patches we create here
# will also be in the right order.
patch = [[]]
cur_patch = 1
for prediction in predictions:
  patch[0].append(tf.argmax(prediction, 1))

  # Once we've seen a patches-worth of class_ids...
  if (len(patch[0]) == patch_width * patch_height):
    print('Done with patch ' + str(cur_patch) + ' of ' + str(patches) + '...')
    # Create an example
    example = tf.train.Example(
      features=tf.train.Features(
        feature={
          'prediction': tf.train.Feature(
              int64_list=tf.train.Int64List(
                  value=patch[0]))
        }
      )
    )
    # Write the example to the file and clear our patch array so it's ready for
    # another batch of class ids
    writer.write(example.SerializeToString())
    patch = [[]]
    cur_patch += 1

writer.close()
```


```python
!earthengine upload image --asset_id={OUTPUT_ASSET_ID} --pyramiding_policy=mode {OUTPUT_IMAGE_FILE} {json_file}
```

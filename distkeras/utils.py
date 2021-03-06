"""
Utils module.
"""

## BEGIN Import. ###############################################################

from pyspark.sql import Row

from keras.models import model_from_json

import numpy as np

## END Import. #################################################################

def to_vector(x, n_dim):
    vector = np.zeros(n_dim)
    vector[x] = 1.0

    return vector

def new_dataframe_row(old_row, column_name, column_value):
    d = old_row.asDict(True)
    d[column_name] = column_value
    new_row = Row(**dict(d))

    return new_row

def serialize_keras_model(model):
    d = {}
    d['model'] = model.to_json()
    d['weights'] = model.get_weights()

    return d

def deserialize_keras_model(d):
    architecture = d['model']
    weights = d['weights']
    model = model_from_json(architecture)
    model.set_weights(weights)

    return model

def uniform_weights(model, constraints=[-0.5, 0.5]):
    # We assume the following: Keras will return a list of weight matrices.
    # All layers, even the activiation layers, will be randomly initialized.
    weights = model.get_weights()
    for layer in weights:
        shape = layer.shape
        if len(shape) > 1:
            # Fill the matrix with random numbers.
            n_rows = shape[0]
            n_columns = shape[1]
            for i in range(0, n_rows):
                for j in range(0, n_columns):
                    layer[i][j] = np.random.uniform(low=constraints[0], high=constraints[1])
        else:
            # Fill the vector with random numbers.
            n_elements = shape[0]
            for i in range(0, n_elements):
                layer[i] = np.random.uniform(low=constraints[0], high=constraints[1])
    # Set the new weights in the model.
    model.set_weights(weights)

def weights_mean(weights):
    assert(weights.shape[0] > 1)

    return np.mean(weights, axis=0)

def weights_mean_vector(weights):
    num_weights = weights.shape[0]

    # Check if the precondition has been met.
    assert(num_weights > 1)

    w = []
    for weight in weights:
        flat = np.asarray([])
        for layer in weight:
            layer = layer.flatten()
            flat = np.hstack((flat, layer))
        w.append(flat)
    w = np.asarray(w)

    return np.mean(w, axis=0)

def weights_std(weights):
    num_weights = weights.shape[0]

    # Check if the precondition has been met.
    assert(num_weights > 1)

    w = []
    for weight in weights:
        flat = np.asarray([])
        for layer in weight:
            layer = layer.flatten()
            flat = np.hstack((flat, layer))
        w.append(flat)
    w = np.asarray(w)
    std = np.std(w, axis=0)
    for i in range(0, std.shape[0]):
        if std[i] == 0.0:
            std[i] = 0.000001

    return std

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:05:22 2017

@author: SAA
"""


# coding: utf-8

# Deep Learning
# =============
# 
# Assignment 3
# ------------
# 
# Previously in `2_fullyconnected.ipynb`, you trained a logistic regression and a neural network model.
# 
# The goal of this assignment is to explore regularization techniques.

# In[ ]:


# These are all the modules we'll be using later. Make sure you can import them
# before proceeding further.
from __future__ import print_function
import numpy as np
import tensorflow as tf
from six.moves import cPickle as pickle


# First reload the data we generated in `1_notmnist.ipynb`.

# In[ ]:


pickle_file = 'notMNIST.pickle'

with open(pickle_file, 'rb') as f:
  save = pickle.load(f)
  train_dataset = save['train_dataset']
  train_labels = save['train_labels']
  valid_dataset = save['valid_dataset']
  valid_labels = save['valid_labels']
  test_dataset = save['test_dataset']
  test_labels = save['test_labels']
  del save  # hint to help gc free up memory
  print('Training set', train_dataset.shape, train_labels.shape)
  print('Validation set', valid_dataset.shape, valid_labels.shape)
  print('Test set', test_dataset.shape, test_labels.shape)


# Reformat into a shape that's more adapted to the models we're going to train:
# - data as a flat matrix,
# - labels as float 1-hot encodings.

# In[ ]:


image_size = 28
num_labels = 10

def reformat(dataset, labels):
  dataset = dataset.reshape((-1, image_size * image_size)).astype(np.float32)
  # Map 1 to [0.0, 1.0, 0.0 ...], 2 to [0.0, 0.0, 1.0 ...]
  labels = (np.arange(num_labels) == labels[:,None]).astype(np.float32)
  return dataset, labels
train_dataset, train_labels = reformat(train_dataset, train_labels)
valid_dataset, valid_labels = reformat(valid_dataset, valid_labels)
test_dataset, test_labels = reformat(test_dataset, test_labels)
print('Training set', train_dataset.shape, train_labels.shape)
print('Validation set', valid_dataset.shape, valid_labels.shape)
print('Test set', test_dataset.shape, test_labels.shape)



# In[ ]:

def accuracy(predictions, labels):
  return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1))
          / predictions.shape[0])

train_subset = 10000

batch_size = 128
hiddenlayer_num1 = 1024
hiddenlayer_num2 = 300
hiddenlayer_num3 = 50

lam1 = .001/3
lam2 = .001/3
lam3 = .001/3
lam4 = .001/3

graph = tf.Graph()
with graph.as_default():

  # Input data. For the training data, we use a placeholder that will be fed
  # at run time with a training minibatch.
  tf_train_dataset = tf.placeholder(tf.float32,
                                    shape=(batch_size, image_size * image_size))
  tf_train_labels = tf.placeholder(tf.float32, shape=(batch_size, num_labels))
  tf_valid_dataset = tf.constant(valid_dataset)
  tf_test_dataset = tf.constant(test_dataset)
  
  # Decay learning
  global_step = tf.Variable(0, trainable=False)
  starter_learning_rate = 0.5
  end_learning_rate = 0.05
  decay_steps = 10000
  learning_rate = tf.train.polynomial_decay(starter_learning_rate, global_step,
                                              decay_steps, end_learning_rate,
                                              power=1)
  
  # Variables.
  weights1 = tf.Variable(
    tf.truncated_normal([image_size * image_size, hiddenlayer_num1],stddev=.12))
  weights2 = tf.Variable(
    tf.truncated_normal([hiddenlayer_num1, hiddenlayer_num2],stddev=.12))
  weights3 = tf.Variable(
    tf.truncated_normal([hiddenlayer_num2, hiddenlayer_num3],stddev=.12))
  weights4 = tf.Variable(
    tf.truncated_normal([hiddenlayer_num3, num_labels],stddev=.12))
  
  biases1 = tf.Variable(tf.ones([hiddenlayer_num1]))
  biases2 = tf.Variable(tf.ones([hiddenlayer_num2]))
  biases3 = tf.Variable(tf.ones([hiddenlayer_num3]))
  biases4 = tf.Variable(tf.ones([num_labels]))
  
  # Training computation.
  logits1 = tf.exp(-tf.square(tf.matmul(tf_train_dataset, weights1) + biases1))
  logits2 = tf.exp(-tf.square(tf.matmul(logits1, weights2) + biases2))
  logits3 = tf.exp(-tf.square(tf.matmul(logits2, weights3) + biases3))
  logits4 = tf.matmul(logits3, weights4) + biases4
  
  loss = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits(labels=tf_train_labels, logits=logits4))
  loss = loss + lam1 * tf.nn.l2_loss(weights1) + lam2 * tf.nn.l2_loss(weights2) + lam3 * tf.nn.l2_loss(weights3) + lam4 * tf.nn.l2_loss(weights4)
  # Optimizer.
  optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss,global_step=global_step)
  
  # Predictions for the training, validation, and test data.
  train_prediction = tf.nn.softmax(logits4)
  valid_prediction = tf.nn.softmax(
    tf.matmul(tf.exp(-tf.square(tf.matmul(tf.exp(-tf.square(tf.matmul(tf.exp(-tf.square(tf.matmul(tf_valid_dataset, weights1) + biases1)), weights2) + biases2)), weights3) + biases3)),weights4)+biases4)
  test_prediction = tf.nn.softmax(tf.matmul(tf.exp(-tf.square(tf.matmul(tf.exp(-tf.square(tf.matmul(tf.exp(-tf.square(tf.matmul(tf_test_dataset, weights1) + biases1)), weights2) + biases2)), weights3) + biases3)),weights4)+biases4)
#########################################################
num_steps = 10001

with tf.Session(graph=graph) as session:
  tf.global_variables_initializer().run()
  print("Initialized")
  for step in range(num_steps):
    # Pick an offset within the training data, which has been randomized.
    # Note: we could use better randomization across epochs.
    offset = (step * batch_size) % (train_labels.shape[0] - batch_size)
    # Generate a minibatch.
    batch_data = train_dataset[offset:(offset + batch_size), :]
    batch_labels = train_labels[offset:(offset + batch_size), :]
    # Prepare a dictionary telling the session where to feed the minibatch.
    # The key of the dictionary is the placeholder node of the graph to be fed,
    # and the value is the numpy array to feed to it.
    feed_dict = {tf_train_dataset : batch_data, tf_train_labels : batch_labels}
    _, l, predictions = session.run(
      [optimizer, loss, train_prediction], feed_dict=feed_dict)
    if (step % 500 == 0):
      print("Minibatch loss at step %d: %f" % (step, l))
      print("Minibatch accuracy: %.1f%%" % accuracy(predictions, batch_labels))
      print("Validation accuracy: %.1f%%" % accuracy(
        valid_prediction.eval(), valid_labels))
  print("Test accuracy: %.1f%%" % accuracy(test_prediction.eval(), test_labels))

# ---

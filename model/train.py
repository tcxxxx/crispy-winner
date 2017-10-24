from __future__ import division, print_function, absolute_import

import os
import sys
import tflearn
import tensorflow as tf
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization, batch_normalization
from tflearn.layers.estimator import regression
from tflearn.data_utils import image_preloader

os.environ["CUDA_VISIBLE_DEVICES"]="0"
os.environ["PYTHONUNBUFFERED"]="1"

dataset_file = 'dataset.txt'
sub1_file = ''
sub2_file = ''
sub3_file = ''

class Model(object):
    '''
    alexnet
    '''
    def __init__(self, runId):
        self.runId = runId
        network = input_data(shape=[None, 100, 100, 3], name="input")
        network = self.make_core_network(network)
        network = regression(network, optimizer='momentum', loss='categorical_crossentropy', learning_rate=0.001)
        model = tflearn.DNN(network, tensorboard_verbose=3)
        self.model = model
    
    @staticmethod
    def make_core_network(network, mode=True):
        network = batch_normalization(network)
        network = conv_2d(network, 6, 6, strides=4, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = batch_normalization(network)
        network = conv_2d(network, 128, 5, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = batch_normalization(network)
        network = conv_2d(network, 128, 3, activation='relu')

        network = batch_normalization(network)
        network = conv_2d(network, 128, 3, activation='relu')

        network = batch_normalization(network)
        network = conv_2d(network, 64, 3, activation='relu')
        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = fully_connected(network, 256, activation='tanh')
        network = dropout(network, 0.5)
        network = fully_connected(network, 256, activation='tanh')
        network = dropout(network, 0.5)

        if mode == True:
            network = fully_connected(network, 4, activation='softmax')

        return network

    def train(self, X, Y):
        self.model.fit(X, Y, n_epoch=40, validation_set=0.2, shuffle=True,
                  show_metric=True, batch_size=16, snapshot_step=200,
                  snapshot_epoch=True, run_id=self.runId)

class Model_Combination(object):
    '''
    Combination
    '''
    def __init__(self, runId):
        self.runId = runId
        inputs = input_data(shape=[None, 100, 100, 3], name="input")

        with tf.variable_scope("scope0") as scope:
            net_alex0 = Model.make_core_network(inputs, mode=False)
        with tf.variable_scope("scope1") as scope:
            net_alex1 = Model.make_core_network(inputs, mode=False)
        with tf.variable_scope("scope2") as scope:
            net_alex2 = Model.make_core_network(inputs, mode=False)
        with tf.variable_scope("scope3") as scope:
            net_alex3 = Model.make_core_network(inputs, mode=False)

        network = tf.concat([net_alex0, net_alex1, net_alex2, net_alex3], 1, name="concat")
        network = fully_connected(network, 256 * 3, activation='tanh')   # 256
        network = dropout(network, 0.5)
        network = fully_connected(network, 256 * 3, activation='tanh')   # 256
        network = dropout(network, 0.5)
        network = tflearn.fully_connected(network, 2, activation="softmax")
        network = regression(network, optimizer='momentum', learning_rate=0.001, loss='categorical_crossentropy', name='target')
        self.model = tflearn.DNN(network, tensorboard_verbose=0)

    def load_weights(self, m0fn, m1fn, m2fn, m3fn):
        self.model.load(m0fn, scope_for_restore="scope0", weights_only=True)
        self.model.load(m1fn, scope_for_restore="scope1", weights_only=True, create_new_session=False)
        self.model.load(m2fn, scope_for_restore="scope2", weights_only=True, create_new_session=False)
        self.model.load(m3fn, scope_for_restore="scope3", weights_only=True, create_new_session=False)

    def load_weights_p(self, mfn, number):
        if number == 1:
            self.model.load(mfn, scope_for_restore="scope0", weights_only=True)
        elif number == 2:
            self.model.load(mfn, scope_for_restore="scope1", weights_only=True)
        elif number == 3:
            self.model.load(mfn, scope_for_restore="scope2", weights_only=True)
        elif number == 4:
            self.model.load(mfn, scope_for_restore="scope3", weights_only=True)

    def train(self, X, Y):
        self.model.fit(X, Y, n_epoch=40, validation_set=0.2, shuffle=True,
                  show_metric=True, batch_size=16, snapshot_step=200,
                  snapshot_epoch=True, run_id=self.runId)

X0, Y0 = image_preloader(dataset_file, image_shape=(100, 100), mode='file', categorical_labels=True, normalize=True, filter_channel=True)

def train_model0():
    tf.reset_default_graph()
    m0 = Model("alexnet-model0")
    m0.train(X0, Y0)
    m0.model.save("model/model_saved/model0/model0.tfl")

if __name__ == "__main__":
    train_model0()
    

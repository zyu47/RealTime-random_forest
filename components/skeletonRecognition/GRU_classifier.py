import tensorflow as tf
import numpy as np
from Preprocessing import normalize_joint_dataset
from tensorflow.contrib import rnn


class GRU_RNN:
    def __init__(self, logs_path, n_hidden=10, n_classes=5, batch_size=1, features=21):
        self.logs_path = logs_path
        self.n_hidden = n_hidden
        self.n_classes = n_classes
        self._feature_size = features

        self.batch_size= batch_size
        self.x = tf.placeholder(tf.float32, [None, None, self._feature_size])
        self.n_frames = tf.placeholder(tf.int32, [None])


        cell = tf.nn.rnn_cell.GRUCell(self.n_hidden)
        cell_out = rnn.OutputProjectionWrapper(cell, self.n_classes)

        outputs, state = tf.nn.dynamic_rnn(cell_out, self.x, sequence_length=self.n_frames, dtype=tf.float32, time_major=False)

        trial_output = []
        for i in range(self.batch_size):
            trial_output.append(outputs[i, self.n_frames[i]-1, :])


        self.outputs = tf.stack(trial_output)
        self.prediction = tf.nn.softmax(self.outputs)
        self.predicted_values = tf.argmax(self.prediction, 1)


        try:
            config = tf.ConfigProto(allow_soft_placement=True)
            config.gpu_options.allow_growth = True
            self.sess = tf.Session(config= config)
        except:
            config = tf.ConfigProto(allow_soft_placement=True)
            config.gpu_options.allow_growth = True
            self.sess = tf.Session(config= config)

        # model saver
        self.saver = tf.train.Saver()
        self.sess.run(tf.global_variables_initializer())





class EGGNOGClassifierSlidingWindow(object):
    def __init__(self, model, **kwargs):
        self.model = model

        # Unpack keyword arguments
        self.lr = kwargs.pop('learning_rate', 1e-2)
        self.lr_decay = kwargs.pop('lr_decay', 1.0)
        self.batch_size = kwargs.pop('batch_size', 1)
        self.test_batch_size = kwargs.pop('test_batch_size', 1)

        self.num_epochs = kwargs.pop('num_epochs', 10)
        self.num_classes = kwargs.pop('num_classes', 5)

        self.print_every = kwargs.pop('print_every', 100)
        self.save_every = kwargs.pop('save_every', 100)
        self.verbose = kwargs.pop('verbose', True)
        self.keep_prob = kwargs.pop('dropout', .5)

        self.restore_model = kwargs.pop('restore_model', False)

        # Throw an error if there are extra keyword arguments
        if len(kwargs) > 0:
            extra = ', '.join('"%s"' % k for k in kwargs.keys())
            raise ValueError('Unrecognized arguments %s' % extra)


        if self.restore_model:
            self.model.saver.restore(self.model.sess, self.model.logs_path)
            print 'Old model restored from %s' % (self.model.logs_path)


    def predict(self, res):
        frames = res[0].shape[0]

        res = normalize_joint_dataset(res, 6, verbose=False)
        n_frame_batch = [frames] * self.test_batch_size

        x_data = res[0][np.newaxis, :, :]
        x_data = np.array([x_data[0] for _ in range(self.test_batch_size)])

        pred_val, proba_output = self.model.sess.run( [self.model.predicted_values, self.model.prediction], feed_dict={self.model.x: x_data, self.model.n_frames: n_frame_batch})
        pred_val = int(pred_val[0])
        proba = proba_output[0]

        # class_list = ['emblems', 'motions', 'neutral', 'oscillate', 'still']
        #Format of result of classifier <Label index>, <Probability values for 5 classes>
        return (pred_val, proba)


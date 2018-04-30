import resnet_model_half_weights
import tensorflow as tf
import numpy as np
import os

class RealTimeHeadRecognition():
    def __init__(self, gestures):

        hps = resnet_model_half_weights.HParams(batch_size=1,
                                                num_classes=gestures,
                                                min_lrn_rate=0.0001,
                                                lrn_rate=0.1,
                                                num_residual_units=5,
                                                use_bottleneck=True,
                                                weight_decay_rate=0.0002,
                                                relu_leakiness=0,
                                                optimizer='mom')

        model = resnet_model_half_weights.ResNet(hps, "eval")
        model.build_graph()
        saver = tf.train.Saver()

        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
        tf.train.start_queue_runners(sess)
        ckpt_state = tf.train.get_checkpoint_state("/s/red/a/nobackup/cwc/tf/heads/head_diff_half_weights/")
        print 'Loading checkpoint %s', ckpt_state.model_checkpoint_path
        saver.restore(sess, ckpt_state.model_checkpoint_path)
        print "Loading done"

        self.sess = sess
        self.model = model

        self.past_probs = None

    def classify(self, data):
        (predictions) = self.sess.run([self.model.predictions], feed_dict={self.model._images: data})
        probs = predictions[0][0]

        if self.past_probs is None:
            self.past_probs = probs
        else:
            self.past_probs = (self.past_probs+probs)/2


        max_prediction = np.argmax(self.past_probs)
        if (max_prediction == 0 or max_prediction == 1) and self.past_probs[max_prediction]<0.6:
            #print "*",self.past_probs
            max_prediction = 2
            self.past_probs = [0,0,1]

        return max_prediction, self.past_probs


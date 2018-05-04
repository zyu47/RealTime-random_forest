import hands_resnet_model
import tensorflow as tf
import numpy as np
import os

class RealTimeHandRecognition():
    def __init__(self, hands, gestures):

        hps = hands_resnet_model.HParams(batch_size=1,
                                                num_classes=gestures,
                                                min_lrn_rate=0.0001,
                                                lrn_rate=0.1,
                                                num_residual_units=5,
                                                use_bottleneck=True,
                                                weight_decay_rate=0.0002,
                                                relu_leakiness=0,
                                                optimizer='mom')

        model = hands_resnet_model.ResNet(hps, "eval")
        model.build_graph()
        saver = tf.train.Saver()

        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
        tf.train.start_queue_runners(sess)
        ckpt_state = tf.train.get_checkpoint_state("/s/red/a/nobackup/cwc/tf/hands_demo_1/%s"%hands)
        print 'Loading checkpoint %s', ckpt_state.model_checkpoint_path
        saver.restore(sess, ckpt_state.model_checkpoint_path)

        self.sess = sess
        self.model = model

        self.past_probs = None

    def classify(self, data):
            (feature) = self.sess.run([self.model.fc_x], feed_dict={self.model._images: data})

            return feature

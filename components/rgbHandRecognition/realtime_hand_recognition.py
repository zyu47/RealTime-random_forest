import os
from resnet_v2 import resnet_v2_50
import resnet_utils
import numpy as np
import tensorflow as tf

slim = tf.contrib.slim

class RealTimeHandRecognition():
    def __init__(self, hands, gestures):


        self._image = tf.placeholder(tf.float32, [128, 128, 3])

        self._standardized_images = tf.expand_dims(tf.image.per_image_standardization(self._image), 0)
        print self._standardized_images

        with slim.arg_scope(resnet_utils.resnet_arg_scope()):
            logits_tensor, end_points = resnet_v2_50(self._standardized_images, gestures, False)

        saver = tf.train.Saver()
        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
        tf.train.start_queue_runners(sess)

        self.probabilities_tensor = end_points['predictions']

        if hands == "RH":
            ckpt = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/RH_fine/model.ckpt-5590"
        else:
            ckpt = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/LH_fine/model.ckpt-40734"

        print 'Loading checkpoint %s'%ckpt
        saver.restore(sess, ckpt)

        self.sess = sess

        self.past_probs = None

    def classify(self, data):
        (predictions) = self.sess.run([self.probabilities_tensor], feed_dict={self._image: data})
        probs = predictions[0][0]

        if self.past_probs is None:
            self.past_probs = probs
        else:
            self.past_probs = (self.past_probs+probs)/2


        max_prediction = np.argmax(self.past_probs)
        return max_prediction, self.past_probs


if __name__ == "__main__":
    import skimage.io
    from skimage.transform import rescale
    import matplotlib.pyplot as plt

    hand = "LH"

    gesture_list = os.listdir("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_01")
    gesture_list.sort()

    r = RealTimeHandRecognition(hand, 20)

    for gesture in gesture_list:
        image_list = os.listdir("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_03/%s/%s"%(gesture,hand))

        image = skimage.io.imread("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_03/%s/%s/%s"%(gesture,hand,image_list[20]))
        #print np.min(image), np.max(image)
        #image = rescale(image, 2, 3)
        #print np.min(image), np.max(image), image.shape
        #image = image[np.newaxis,:,:,:]
        #plt.imshow(image)
        #plt.show()

        r.past_probs = None

        index, probs = r.classify(image)

        print gesture, gesture_list[index]

        if gesture!=gesture_list[index]:
            plt.imshow(image)
            plt.title(gesture+" "+gesture_list[index])
            plt.show()


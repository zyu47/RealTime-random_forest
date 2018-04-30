from resnet_v2 import resnet_v2_50
import tensorflow as tf
import os
import numpy as np
import resnet_utils
import time
from image_reader import get_input

slim = tf.contrib.slim

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('hand', 'RH', 'RH or LH')
tf.app.flags.DEFINE_string('mode', 'train', 'train or eval or test')

hand = FLAGS.hand

log_root = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/%s_fine" % hand
train_dir = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/%s_fine/train" % hand
eval_dir = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/%s_fine/eval" % hand
print log_root, train_dir, eval_dir

#eval_batch_count = 250611  # 191231

save_summaries_steps = 100
save_checkpoint_secs = 300


def train():
    tf.logging.set_verbosity(tf.logging.INFO)  # Set the verbosity to INFO level

    initial_learning_rate = 0.0002
    learning_rate_decay_factor = 0.7
    decay_steps = 40000

    checkpoint_file = tf.train.latest_checkpoint(log_root)
    print(checkpoint_file)

    images, one_hot_labels = get_input(20, FLAGS.batch_size, hand=FLAGS.hand)

    with slim.arg_scope(resnet_utils.resnet_arg_scope()):
        logits, end_points = resnet_v2_50(images, 20)
        print logits, end_points

    variables_to_restore = slim.get_variables_to_restore()

    loss = tf.losses.softmax_cross_entropy(onehot_labels=one_hot_labels, logits=logits)
    total_loss = tf.losses.get_total_loss()  # obtain the regularization losses as well

    # Create the global step for monitoring the learning_rate and training.
    global_step_1 = tf.contrib.framework.get_or_create_global_step()

    # Define your exponentially decaying learning rate
    lr = tf.train.exponential_decay(
        learning_rate=initial_learning_rate,
        global_step=global_step_1,
        decay_steps=decay_steps,
        decay_rate=learning_rate_decay_factor,
        staircase=True)

    # Now we can define the optimizer that takes on the learning rate
    optimizer = tf.train.AdamOptimizer(learning_rate=lr)
    #variables_to_train = [v for v in variables_to_restore if 'resnet_v2_50/logits' in v.name]
    #print variables_to_train
    #raw_input()

    # Create the train_op.
    train_op = slim.learning.create_train_op(total_loss, optimizer,)# variables_to_train = variables_to_train)

    # State the metrics that you want to predict. We get a predictions that is not one_hot_encoded.
    predictions = tf.argmax(end_points['predictions'], 1)
    probabilities = end_points['predictions']
    labels = tf.argmax(one_hot_labels, 1)
    precision = tf.reduce_mean(tf.to_float(tf.equal(predictions, labels)))

    summary_writer = tf.summary.FileWriter(train_dir)
    summary_op=tf.summary.merge([tf.summary.scalar('costs/cost', total_loss),tf.summary.scalar('Precision', precision),tf.summary.scalar('learning_rate', lr)])

    saver = tf.train.Saver(max_to_keep=0)
    sess = tf.Session()
    saver.restore(sess, tf.train.latest_checkpoint(log_root))


    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess,coord=coord)


    var = [v for v in tf.model_variables() if "50/conv1" in v.name or "logits" in v.name]
    var_list = sess.run(var)
    for v1, v in zip(var, var_list):
        print v1.name, v.shape, np.min(v), np.max(v), np.mean(v), np.std(v)

    saver.save(sess, os.path.join(log_root,"model.ckpt"), global_step=global_step_1)
    checkpoint_time = time.time()

    while True:
        _, summary, g_step, loss, accuracy, l_rate = sess.run([train_op, summary_op, global_step_1, total_loss, precision, lr])

        if g_step%10 == 0:
            tf.logging.info('Global_step_1: %d, loss: %f, precision: %.2f, lr: %f'%(g_step, loss, accuracy, l_rate))

        if time.time() - checkpoint_time > save_checkpoint_secs:
            saver.save(sess, os.path.join(log_root, "model.ckpt"), global_step=global_step_1)
            checkpoint_time = time.time()

        if g_step%save_summaries_steps == 0:
            summary_writer.add_summary(summary, g_step)
            summary_writer.flush()


def evaluate():
    """Eval loop."""
    images, one_hot_labels = get_input(20, FLAGS.batch_size, FLAGS.mode, FLAGS.hand)
    gesture_list = os.listdir("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_01")
    gesture_list.sort()
    print gesture_list


    with slim.arg_scope(resnet_utils.resnet_arg_scope()):
        logits_tensor, end_points = resnet_v2_50(images, 20, False)

    saver = tf.train.Saver()
    summary_writer = tf.summary.FileWriter(eval_dir)

    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    tf.train.start_queue_runners(sess)

    best_precision = 0.0
    
    predictions_tensor = tf.argmax(end_points['predictions'], 1)
    probabilities_tensor = end_points['predictions']

    labels = tf.argmax(one_hot_labels, 1)
    #precision = tf.reduce_mean(tf.to_float(tf.equal(predictions_tensor, labels)))
    
    checkpoint_list = os.listdir(log_root)
    checkpoint_list=[c.replace(".index","") for c in checkpoint_list if ".index" in c]
    print checkpoint_list

    precision_list = []

    #while True:
    for c in checkpoint_list:
        try:
            ckpt_state = tf.train.get_checkpoint_state(log_root)
        except tf.errors.OutOfRangeError as e:
            tf.logging.error('Cannot restore checkpoint: %s', e)
            continue
        if not (ckpt_state and ckpt_state.model_checkpoint_path):
            tf.logging.info('No model to eval yet at %s', log_root)
            continue
        ckpt_state.model_checkpoint_path = os.path.join(log_root, c)
        tf.logging.info('Loading checkpoint %s', ckpt_state.model_checkpoint_path)
        saver.restore(sess, ckpt_state.model_checkpoint_path)
        tf.logging.info("Checkpoint restoration done")
        train_step = int(ckpt_state.model_checkpoint_path.split("-")[-1])

        total_prediction, correct_prediction = 0, 0

        gt_list = []
        pred_list = []


        for sample in range(212):
            (predictions, truth) = sess.run([probabilities_tensor, one_hot_labels])

            gt_list.append(truth)
            pred_list.append(predictions)

            truth = np.argmax(truth, axis=1)
            predictions = np.argmax(predictions, axis=1)
            correct_prediction += np.sum(truth == predictions)
            total_prediction += predictions.shape[0]

            if sample % 40 == 0:
                print sample, correct_prediction, total_prediction
	    

        gt = np.squeeze(np.vstack(gt_list))
        pred = np.squeeze(np.vstack(pred_list))


        
        precision = np.mean(np.argmax(gt,axis=1)==np.argmax(pred,axis=1))
	precision_list.append(precision)
        best_precision = max(precision, best_precision)
	print gt.shape, pred.shape, precision, best_precision
	gt = np.argmax(gt,axis=1)
	pred = np.argmax(pred,axis=1)
	'''cm = np.float(confusion_matrix(gt,pred))
	
	cm /= np.sum(cm,axis=0)
	plt.imshow(cm,interpolation='nearest')
	plt.xticks(range(20),gesture_list,rotation=90)
	plt.yticks(range(20),gesture_list)
	plt.show()
        precision_summ = tf.Summary()
        precision_summ.value.add(tag='Precision', simple_value=precision)
        summary_writer.add_summary(precision_summ, train_step)
        best_precision_summ = tf.Summary()
        best_precision_summ.value.add(tag='Best Precision', simple_value=best_precision)
        summary_writer.add_summary(best_precision_summ, train_step)'''

       
        tf.logging.info(
            'precision: %.3f, best precision: %.3f' %
            (precision, best_precision))
        summary_writer.flush()

        #time.sleep(60)
    print "Max Precision : ",np.max(precision_list)," Ckpt: ",checkpoint_list[np.argmax(precision_list)]

def forward():
    import random
    import cv2
    import matplotlib.pyplot as plt

    gesture_list = os.listdir("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_01")
    gesture_list.sort()
    print gesture_list

    #lh_list = np.load("/s/red/a/nobackup/cwc/hands/rgb_test/LH.npy")
    if FLAGS.hand == "RH":
    	rh_list = np.load("/s/red/a/nobackup/cwc/hands/rgb_test/LH.npy")
	ckpt = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/RH_fine/model.ckpt-5590"
    else:
	rh_list = np.load("/s/red/a/nobackup/cwc/hands/rgb_test/RH.npy")
	ckpt = "/s/red/a/nobackup/cwc/tf/hands_demo_rgb/LH_fine/model.ckpt-40734"



    checkpoint_file = tf.train.latest_checkpoint(log_root)
    print(checkpoint_file)

    _image = tf.placeholder(tf.float32, [128, 128, 3])

    _standardized_images = tf.expand_dims(tf.image.per_image_standardization(_image), 0)


    with slim.arg_scope(resnet_utils.resnet_arg_scope()):
        logits, end_points = resnet_v2_50(_standardized_images, 20)
        print logits, end_points

    variables_to_restore = slim.get_variables_to_restore()

    # State the metrics that you want to predict. We get a predictions that is not one_hot_encoded.
    predictions = tf.argmax(end_points['predictions'], 1)
    probabilities = end_points['predictions']

    saver = tf.train.Saver(max_to_keep=0)
    sess = tf.Session()
    #saver.restore(sess, tf.train.latest_checkpoint(log_root))
    saver.restore(sess, ckpt)

    for i in range(10):
	index = random.randint(0, rh_list.shape[0]-1)
	rh_image = rh_list[index]
	rh_image = rh_image[:,:,[2,1,0]]
        rh_image = cv2.resize(rh_image, (128, 128))

	print rh_image.shape

	pred_index = sess.run(predictions,feed_dict={_image:rh_image})
	pred_gesture = gesture_list[pred_index[0]]
	plt.imshow(rh_image)
	plt.title(pred_gesture)
	plt.show()





def main(_):
    if FLAGS.mode == "train":
        FLAGS.batch_size = 64
        train()
    elif FLAGS.mode == "eval":
	FLAGS.batch_size = 64
        evaluate()
    else:
	forward()

#LH: 40734 79.1
#RH 23593 76.7; 5590 78.83

if __name__ == '__main__':
    tf.logging.set_verbosity(tf.logging.INFO)
    tf.app.run()

import struct
import time
from skimage.transform import resize, rotate
import sys
import numpy as np

from realtime_hand_recognition import RealTimeHandRecognition
from RandomForest.forest import Forest

from ..fusion.conf.endpoints import connect
from ..fusion.conf import streams


# timestamp (long) | depth_hands_count(int) | left_hand_height (int) | left_hand_width (int) |
# right_hand_height (int) | right_hand_width (int)| left_hand_pos_x (float) | left_hand_pos_y (float) | ... |
# left_hand_depth_data ([left_hand_width * left_hand_height]) |
# right_hand_depth_data ([right_hand_width * right_hand_height])
def decode_frame_hand(raw_frame):
    # Expect network byte order
    endianness = "<"

    # In each frame_hand, a header is transmitted
    header_format = "qiiiff"
    header_size = struct.calcsize(endianness + header_format)
    header = struct.unpack(endianness + header_format, raw_frame[:header_size])

    timestamp, frame_type, width, height, posx, posy = header
    # print timestamp, frame_type, width, height, posx, posy

    depth_data_format = str(width * height) + "H"

    depth_data = struct.unpack_from(endianness + depth_data_format, raw_frame, header_size)

    return (timestamp, frame_type, width, height, posx, posy, list(depth_data))


# Timestamp | frame_hand type | command_length | command
def decode_frame_speech(raw_frame):
    # Expect little endian byte order
    endianness = "<"

    # In each frame_hand, a header is transmitted
    # Timestamp | frame_hand type | command_length
    header_format = "qii"

    header_size = struct.calcsize(endianness + header_format)
    header = struct.unpack(endianness + header_format, raw_frame[:header_size])

    timestamp, frame_type, command_length = header

    # print timestamp, frame_type, command_length

    command_format = str(command_length) + "s"

    command = struct.unpack_from(endianness + command_format, raw_frame, header_size)[0]

    return (timestamp, frame_type, command_length, command)


def recv_all(sock, size):
    result = b''
    while len(result) < size:
        data = sock.recv(size - len(result))
        if not data:
            raise EOFError("Error: Received only {} bytes into {} byte message".format(len(data), size))
        result += data
    return result


def recv_frame(sock):
    """
    Experimental function to read each stream frame_hand from the server
    """
    (frame_size,) = struct.unpack("<i", recv_all(sock, 4))
    return recv_all(sock, frame_size)


def is_learn(frame_speech):
    timestamp, frame_type, command_length, command = decode_frame_speech(frame_speech)
    if command_length > 0:
        print timestamp, frame_type, command
        print "\n\n"
    if 'LEARN' in command:
        print('*'*100)
        print('Confirm to Learn!')
        print('*'*100)
        return True


def img_aug(in_hand):
    result = []
    for i in [5, 10, 15, -5, -10, -15]:
        hand_new = rotate(in_hand, i, clip=False, preserve_range=True)
        hand_new = hand_new[20:-20, 20:-20]
        hand_new = hand_new.reshape((1, 128, 128, 1))
        feature_new = hand_classfier.classify(hand_new)
        result.append(feature_new[0])
    return result


# By default read 100 frames
if __name__ == '__main__':

    hand = sys.argv[1]
    stream_id = streams.get_stream_id(hand)
    gestures = list(np.load("/s/red/a/nobackup/cwc/hands/real_time_training_data/%s/gesture_list.npy" % hand))
    gestures = [g.replace(".npy", "") for g in gestures]
    num_gestures = len(gestures)

    gestures += ['blind']
    print hand, num_gestures

    hand_classfier = RealTimeHandRecognition(hand, num_gestures)
    forest = Forest()

    training_fea_path = '/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_features_%s.npy' % hand
    samples = np.load(training_fea_path)
    training_label_path = '/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_labels_%s.npy' % hand
    labels = np.load(training_label_path)
    forest.build_forest(samples, labels, n_trees=10)

    kinect_socket_hand = connect('kinect', hand)
    kinect_socket_speech = connect('kinect', 'Speech')
    fusion_socket = connect('fusion', hand)

    # the first speech frame usually has noise, ignore first frame speech
    frame_hand = recv_frame(kinect_socket_hand)
    frame_speech = recv_frame(kinect_socket_speech)

    frame_num_learned = 0  # Number of frames that have already been added into forest
    new_hand = None  # save a copy of hand frame for data augmentation
    # f = open('./log.txt', 'w')
    while True:
        try:
            frame = recv_frame(kinect_socket_hand)
            frame_speech = recv_frame(kinect_socket_speech)
        except KeyboardInterrupt:
           break
        except:
            continue

        # Process depth images
        timestamp, frame_type, width, height, posx, posy, depth_data = decode_frame_hand(frame)
        feature = None

        probs = [0] * num_gestures  # probabilities to send to fusion

        if posx == -1 and posy == -1:
            probs += [1]
            max_index = len(probs)-1
        else:
            hand = np.array(depth_data, dtype=np.float32).reshape((height, width))
            posz = hand[int(posx), int(posy)]
            hand -= posz
            hand /= 150
            hand = np.clip(hand, -1, 1)
            hand = resize(hand, (168, 168))
            new_hand = np.copy(hand)
            hand = hand[20:-20, 20:-20]
            hand = hand.reshape((1, 128, 128, 1))
            feature = hand_classfier.classify(hand)
            found_index, dist = forest.find_nn(feature, method=0)
            max_index = found_index[0]
            probs[max_index] = 1

            probs = list(probs)+[0]



        # Process learning
        if is_learn(frame_speech) and feature is not None and sys.argv[1] == 'RH':
            frame_num_learned += 1

        if 1 < frame_num_learned <= 61:
            if frame_num_learned % 3 == 0:  # learn every other frame
                start = time.time()
                # f.write(str(time.time()) + '\t' + str(frame_num_learned)+'\n')
                print ('-'*100, str(frame_num_learned), '-'*100)
                new_features = img_aug(new_hand)
                new_features.append(feature[0])
                forest.add_new(new_features, [4]*len(new_features))   # add a new gesture for claw_down
                probs = [0] * num_gestures + [1]  # if learning, do not send to fusion
                max_index = len(probs)-1
                # f.write(str(time.time() - start) + '\t' + str(frame_num_learned)+'\n')
            # if frame_num_learned == 61:
            #     f.close()
            frame_num_learned += 1
        elif frame_num_learned != 1:
            frame_num_learned = 0

        print timestamp, gestures[max_index], probs[max_index]

        pack_list = [stream_id, timestamp, max_index] + list(probs)

        # send to fusion
        bytes = struct.pack("<iqi"+"f"*(num_gestures+1), *pack_list)

        if fusion_socket is not None:
            fusion_socket.send(bytes)

    kinect_socket_hand.close()
    if fusion_socket is not None:
        fusion_socket.close()
    sys.exit(0)


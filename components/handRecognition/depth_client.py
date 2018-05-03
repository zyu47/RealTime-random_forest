import struct
import time
from skimage.transform import resize
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
def decode_frame(raw_frame):
    # Expect network byte order
    endianness = "<"

    # In each frame, a header is transmitted
    header_format = "qiiiff"
    header_size = struct.calcsize(endianness + header_format)
    header = struct.unpack(endianness + header_format, raw_frame[:header_size])

    timestamp, frame_type, width, height, posx, posy = header
    print timestamp, frame_type, width, height, posx, posy

    depth_data_format = str(width * height) + "H"

    depth_data = struct.unpack_from(endianness + depth_data_format, raw_frame, header_size)

    return (timestamp, frame_type, width, height, posx, posy, list(depth_data))


def recv_all(sock, size):
    result = b''
    while len(result) < size:
        data = sock.recv(size - len(result))
        if not data:
            raise EOFError("Error: Received only {} bytes into {} byte message".format(len(data), size))
        result += data
    return result


def recv_depth_frame(sock):
    """
    Experimental function to read each stream frame from the server
    """
    (frame_size,) = struct.unpack("<i", recv_all(sock, 4))
    return recv_all(sock, frame_size)


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

    if hand == 'RH':
        samples = np.load('/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_features.npy')
        labels = np.load('/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_labels.npy')
        forest.build_forest(samples, labels, n_trees=10)

    kinect_socket = connect('kinect', hand)
    fusion_socket = connect('fusion', hand)

    i = 0
    hands_list = []

    start_time = time.time()
    while True:
        try:
            frame = recv_depth_frame(kinect_socket)
        except KeyboardInterrupt:
           break
        except:
            continue

        timestamp, frame_type, width, height, posx, posy, depth_data = decode_frame(frame)

        probs = [0] * num_gestures + [1]  # final probabilities to send to fusion

        if posx == -1 and posy == -1:
            max_index = len(probs)-1
        else:
            hand = np.array(depth_data, dtype=np.float32).reshape((height, width))
            print hand.shape, posx, posy
            posz = hand[int(posx), int(posy)]
            hand -= posz
            hand /= 150
            hand = np.clip(hand, -1, 1)
            hand = resize(hand, (168, 168))
            hand = hand[20:-20, 20:-20]
            hand = hand.reshape((1, 128, 128, 1))
            if hand == 'RH':
                feature = hand_classfier.classify(hand, hands='RH')
                max_index, dist = forest.find_nn(feature)
                probs[max_index] = 0.5 - dist/2.0
            else:
                max_index, probs = hand_classfier.classify(hand)

                probs = list(probs)+[0]

        print i, timestamp, gestures[max_index], probs[max_index]
        i += 1

        if i % 100==0:
            print "="*100, "FPS", 100/(time.time()-start_time)
            start_time = time.time()

        pack_list = [stream_id, timestamp,max_index]+list(probs)

        bytes = struct.pack("<iqi"+"f"*(num_gestures+1), *pack_list)

        if fusion_socket is not None:
            fusion_socket.send(bytes)

    kinect_socket.close()
    if fusion_socket is not None:
        fusion_socket.close()
    sys.exit(0)


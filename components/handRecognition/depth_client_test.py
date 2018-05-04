import struct
# import time
from skimage.transform import resize, rotate
import sys
import numpy as np
import matplotlib.pyplot as plt

# from realtime_hand_recognition import RealTimeHandRecognition
# from RandomForest.forest import Forest

from ..fusion.conf.endpoints import connect
# from ..fusion.conf import streams


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


# By default read 100 frames
if __name__ == '__main__':

    hand = sys.argv[1]
    # stream_id = streams.get_stream_id(hand)
    # gestures = list(np.load("/s/red/a/nobackup/cwc/hands/real_time_training_data/%s/gesture_list.npy" % hand))
    # gestures = [g.replace(".npy", "") for g in gestures]
    # num_gestures = len(gestures)
    #
    # gestures += ['blind']
    # print hand, num_gestures
    #
    # hand_classfier = RealTimeHandRecognition(hand, num_gestures)
    # forest = Forest()
    #
    # samples = np.load('/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_features.npy')
    # labels = np.load('/s/red/a/nobackup/vision/jason/DraperLab/one_shot_learning/random_forest/result_for_final/training_labels.npy')
    # forest.build_forest(samples, labels, n_trees=10)

    kinect_socket_hand = connect('kinect', hand)
    # kinect_socket_speech = connect('kinect', 'Speech')
    # fusion_socket = connect('fusion', hand)

    # the first speech frame usually has noise, ignore first frame speech
    frame_hand = recv_frame(kinect_socket_hand)
    # frame_speech = recv_frame(kinect_socket_speech)

    # i = 0
    # hands_list = []

    # start_time = time.time()
    while True:
        try:
            frame_hand = recv_frame(kinect_socket_hand)
            # frame_speech = recv_frame(kinect_socket_speech)
        except KeyboardInterrupt:
           break
        except:
            continue

        timestamp, frame_type, width, height, posx, posy, depth_data = decode_frame_hand(frame_hand)
        # timestamp, frame_type, command_length, command = decode_frame_speech(frame_speech)
        # if command_length > 0:
        #     print timestamp, frame_type, command
        #     print "\n\n"
        # if command == 'LEARN':
        #     print('I learned!')
        #
        # probs = [0] * num_gestures  # probabilities to send to fusion

        if posx == -1 and posy == -1:
            # probs += [1]
            # max_index = len(probs)-1
            continue
        else:
            hand = np.array(depth_data, dtype=np.float32).reshape((height, width))
            # print hand.shape, posx, posy
            posz = hand[int(posx), int(posy)]
            hand -= posz
            hand /= 150
            hand = np.clip(hand, -1, 1)
            hand = resize(hand, (168, 168))
            new_hand = rotate(hand, 90, clip=False, preserve_range=True)
            hand = hand[20:-20, 20:-20]
            # hand = hand.reshape((1, 128, 128, 1))
            new_hand = new_hand[20:-20, 20:-20]
            print(np.amin(new_hand), np.amax(new_hand))
            print(np.amin(hand), np.amax(hand))
            # new_hand = new_hand.reshape((1, 128, 128, 1))

            plt.subplot(121)
            plt.imshow(hand, cmap='Greys')
            plt.subplot(122)
            plt.imshow(new_hand, cmap='Greys')
            plt.savefig('./test1.png')
            break
    #         if sys.argv[1] == 'RH':
    #             feature = hand_classfier.classify(hand, hands='RH')
    #             found_index, dist = forest.find_nn(feature)
    #             max_index = found_index[0]
    #             probs[max_index] = 1
    #             # print(probs)
    #         else:
    #             max_index, probs = hand_classfier.classify(hand)
    #
    #         probs = list(probs)+[0]
    #
    #         # print i, timestamp, gestures[max_index], probs[max_index]
    #     # i += 1
    #     #
    #     # if i % 100==0:
    #     #     # print "="*100, "FPS", 100/(time.time()-start_time)
    #     #     print('Time for 30 frames', (time.time()-start_time)*0.3)
    #     #     start_time = time.time()
    #
    #     pack_list = [stream_id, timestamp, max_index]+list(probs)
    #
    #     bytes = struct.pack("<iqi"+"f"*(num_gestures+1), *pack_list)
    #
    #     if fusion_socket is not None:
    #         fusion_socket.send(bytes)
    #
    # kinect_socket_hand.close()
    # if fusion_socket is not None:
    #     fusion_socket.close()
    # sys.exit(0)
    #

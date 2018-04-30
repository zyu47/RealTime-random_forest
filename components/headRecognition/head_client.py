#!/usr/bin/env python

import sys, struct
import time
import numpy as np
from collections import deque
from skimage.transform import resize
from realtime_head_recognition import RealTimeHeadRecognition
from ..fusion.conf.endpoints import connect
from ..fusion.conf import streams

# Timestamp | frame type | width | height | depth_data
def decode_frame(raw_frame):
    # Expect little endian byte order
    endianness = "<"

    # In each frame, a header is transmitted
    header_format = "qiiiff"
    header_size = struct.calcsize(endianness + header_format)
    header = struct.unpack(endianness + header_format, raw_frame[:header_size])

    timestamp, frame_type, width, height, posx, posy = header

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


if __name__ == '__main__':
    stream_id = streams.get_stream_id("Head")

    gesture_list = ["nod", "shake", "other"]
    num_gestures = len(gesture_list)

    head_classifier = RealTimeHeadRecognition(num_gestures)

    gesture_list += ['blind']

    kinect_socket = connect('kinect', "Head")
    fusion_socket = connect('fusion', "Head")

    if kinect_socket is None:
        sys.exit(0)

    i = 0
    avg_frame_time = 0.0
    do_plot = True #if len(sys.argv) > 1 and sys.argv[1] == '--plot' else False


    index = 0
    start_time = time.time()
    window = deque(maxlen=30)
    euclidean_skeleton = deque(maxlen=29)
    prev_skeleton = None

    while True:
        try:
            t_begin = time.time()
            f = recv_depth_frame(kinect_socket)
            t_end = time.time()
        except:
            break
        #print "Time taken for this frame: {}".format(t_end - t_begin)
        avg_frame_time += (t_end - t_begin)
        timestamp, frame_type, width, height, posx, posy, depth_data = decode_frame(f)
        print timestamp, frame_type, width, height,

        curr_skeleton = np.array([posx, posy])

        if height>0 and width > 0:
            head = np.array(depth_data, dtype=np.float32).reshape((height, width))
            posz = head[int(posx), int(posy)]
            head -= posz
            head /= 150
            head = np.clip(head, -1, 1)
            head = resize(head, (168, 168))
            head = head[20:-20, 20:-20]
            head += 1
            head *= 127.5

            window.append(head)
            if prev_skeleton is not None:
                euclidean_skeleton.append(np.linalg.norm(curr_skeleton - prev_skeleton))
            prev_skeleton = curr_skeleton

            if len(window)==30:
                new_window = [window[0]]
                for i in range(1,30):
                    new_window.append(window[i]-window[i-1])

                new_window = [n/255.0 for n in new_window]

                new_window = np.rollaxis(np.stack(new_window), 0, 3)[np.newaxis,:,:,:]

                gesture_index, probs = head_classifier.classify(new_window)
                head_movement = np.sum(euclidean_skeleton)
                probs = list(probs)+[0]
                print gesture_list[gesture_index], probs[gesture_index], head_movement,

                if head_movement>13: #0.03
                    gesture_index = 2
                    probs = [0,0,1,0]
                    print gesture_list[gesture_index],
                print "\n"

                pack_list = [stream_id, timestamp, gesture_index] + list(probs)

                bytes = struct.pack("<iqi" + "f" * (num_gestures+1), *pack_list)

                if fusion_socket is not None:
                    fusion_socket.send(bytes)

            else:
                pack_list = [stream_id, timestamp, num_gestures] + [0] * num_gestures + [1]
                print 'Buffer not full'
                bytes = struct.pack("<iqi" + "f" * (num_gestures + 1), *pack_list)

                if fusion_socket is not None:
                    fusion_socket.send(bytes)


            index += 1

        else:
            pack_list = [stream_id, timestamp, num_gestures] + [0] * num_gestures + [1]
            print 'blind'
            bytes = struct.pack("<iqi" + "f" * (num_gestures + 1), *pack_list)

            if fusion_socket is not None:
                fusion_socket.send(bytes)

        if index % 100==0:
            print "="*100, "FPS", 100/(time.time()-start_time)
            start_time = time.time()

    kinect_socket.close()
    if fusion_socket is not None:
        fusion_socket.close()
    sys.exit(0)

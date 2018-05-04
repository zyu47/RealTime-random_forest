#!/usr/bin/env python

import socket, sys, struct
import time
import numpy as np
from realtime_hand_recognition import RealTimeHandRecognition
import os
import cv2
from ..fusion.conf.endpoints import connect
from ..fusion.conf import streams

src_addr = '129.82.45.252'
src_port = 9009

  # lh and rh color stream


def connect_rgb(hand):
    """
    Connect to a specific port
    """
    if hand == "LH":
        stream_id = 1024
    elif hand =="RH":
        stream_id = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((src_addr, src_port))
    except:
        print "Error connecting to {}:{}".format(src_addr, src_port)
        return None

    try:
        print "Sending stream info"
        sock.sendall(struct.pack('<i', stream_id))
    except:
        print "Error: Stream rejected"
        return None

    print "Successfully connected to host"
    return sock
    

def decode_frame_openpose(raw_frame):
    # The format is given according to the following assumption of network data

    # Expect little endian byte order
    endianness = "<"

    # [ commonTimestamp | frame_hand type (0 => LH; 1 => RH)| img_width | img_height ]
    header_format = "qiHH"
    header_size = struct.calcsize(endianness + header_format)
    timestamp, frame_type, width, height = struct.unpack(endianness + header_format,
                                                                       raw_frame[:struct.calcsize(header_format)])

    color_data_format = str(width*height*3) + "H"  # 1(image)*img_width*img_height*3(channels)

    color_data = struct.unpack_from(endianness + color_data_format, raw_frame, header_size)

    decoded = (timestamp, frame_type, width, height, list(color_data))

    # print "decoded:", decoded
    return decoded


def recv_all(sock, size):
    result = b''
    while len(result) < size:
        data = sock.recv(size - len(result))
        if not data:
            raise EOFError("Error: Received only {} bytes into {} byte message".format(len(data), size))
        result += data
    return result


def recv_color_frame(sock):
    """
    Experimental function to read each stream frame_hand from the server
    """
    (frame_size,) = struct.unpack("<i", recv_all(sock, 4))
    return recv_all(sock, frame_size) 


if __name__ == '__main__':

    hand = sys.argv[1]
    stream_id = streams.get_stream_id(hand)
    if hand == "RH":
        FRAME_TYPE = 1
    elif hand == "LH":
        FRAME_TYPE = 0

    r = RealTimeHandRecognition(hand, 20)

    gesture_list = os.listdir("/s/red/a/nobackup/cwc/hands/rgb_hands_new_frames/s_01")
    gesture_list.sort()

    fusion_map_dict = {0:1,19:2,1:3,2:4,3:8,4:10,5:11,6:13,7:14,8:15,9:17,10:21,11:22,12:23,13:24,14:26,15:27,16:28,
                       17:29,18:31}

    fusion_map_dict = {7:1,10:2,0:3,1:4,2:8,3:10,4:11,5:13,6:14,8:15,9: 17,11:21,12:22,13:23,14:24,15:26,16:27,17:28,
                       18:29,19:31}

    s = connect_rgb(hand)
    fusion_socket = connect('fusion', hand)

    if s is None:
        sys.exit(0)
    
    i = 0
    avg_frame_time = 0.0

    start_time = time.time()

    while True:
        try:
            f = recv_color_frame(s)
        except:
            break

        timestamp, frame_type, width, height, color_data = decode_frame_openpose(f)

        if height*width > 0 and frame_type == FRAME_TYPE:


            image_rgb = np.array(color_data[0:len(color_data)], dtype='uint8').reshape((height, width, 3))

            if np.sum(image_rgb) == 0:
                fusion_probs = [0 for _ in range(33)]
                fusion_probs[0] = 1
                print timestamp,"blind"

            else:
                image_rgb = image_rgb[:,:,[2,1,0]]
                image_rgb = cv2.resize(image_rgb, (128, 128))

                rgb_max_index, probs = r.classify(image_rgb)

                print timestamp, gesture_list[rgb_max_index]

                fusion_probs = [0 for _ in range(33)]

                for index, p in enumerate(probs):
                    fusion_probs[fusion_map_dict[index]] = p

            max_index = np.argmax(fusion_probs)

            #print max_index, rgb_max_index, fusion_map_dict[rgb_max_index]

            pack_list = [stream_id, timestamp, max_index] + list(fusion_probs)
            bytes = struct.pack("<iqi" + "f" * 33, *pack_list)

            if fusion_socket is not None:
                fusion_socket.send(bytes)

            i += 1

            if i % 100 == 0:
                print "=" * 100, "FPS", 100 / (time.time() - start_time)
                start_time = time.time()


    s.close()
    sys.exit(0)

import sys, struct
from ..fusion.conf.endpoints import connect

# Timestamp | frame type | command_length | command
def decode_frame(raw_frame):
    
    # Expect little endian byte order
    endianness = "<"

    # In each frame, a header is transmitted
    # Timestamp | frame type | command_length
    header_format = "qii"
    
    header_size = struct.calcsize(endianness + header_format)
    header = struct.unpack(endianness + header_format, raw_frame[:header_size])

    timestamp, frame_type, command_length = header
    
    #print timestamp, frame_type, command_length
    
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

def recv_speech_frame(sock):
    """
    Experimental function to read each stream frame from the server
    """
    (frame_size,) = struct.unpack("<i", recv_all(sock, 4))
    #print frame_size
    return recv_all(sock, frame_size) 
    

if __name__ == '__main__':

    k = connect('kinect', 'Speech')
    if k is None:
        sys.exit(0)

    f = connect('fusion', 'Speech')

    while True:
        try:
            frame = recv_speech_frame(k)
        except:
            print "Unable to receive speech frame"
            break
        timestamp, frame_type, command_length, command = decode_frame(frame)
        if command_length > 0:
            print timestamp, frame_type, command
            print "\n\n"
        if f is not None:
            try:
                # Excluding frame size
                f.sendall(struct.pack("<iqi" + str(len(command)) + "s", frame_type, timestamp, command_length, command))
            except:
                print "Error: Connection to fusion lost"
                f.close()
                f = None

    k.close()
    if f is not None:
        f.close()
    sys.exit(0)

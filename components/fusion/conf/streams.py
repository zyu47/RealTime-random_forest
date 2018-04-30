_stream_ids = {
    "Color": 0x2,   # 2
    "Speech": 0x4,  # 4
    "Audio": 0x8,   # 8
    "Depth": 0x10,  # 16
    "Body": 0x20,   # 32
    "LH": 0x40,     # 64
    "RH": 0x80,     # 128
    "Head": 0x100   # 256
}

_active_streams = frozenset(["LH", "RH", "Body", "Head", "Speech"])

for s in _active_streams:
    if s not in _stream_ids:
        raise Exception("Active streams configured incorrectly.\n{} not present in stream list.\n".format(s))


def get_stream_id(stream_name):
    return _stream_ids[stream_name]


def is_valid(stream_name):
    return stream_name in _stream_ids


def is_valid_id(stream_id):
    return stream_id in _stream_ids.values()


def is_active(stream_name):
    return stream_name in _active_streams


def is_active_id(stream_id):
    return get_stream_name(stream_id) in _active_streams


def get_stream_name(stream_id):
    for st in _stream_ids:
        if _stream_ids[st] & stream_id != 0:
            return st
    raise KeyError("Invalid stream type")


def get_stream_names():
    return _stream_ids.keys()


def get_streams_count():
    return len(_stream_ids)


def get_active_streams_count():
    return len(_active_streams)


def all_connected(connected_streams):
    """
    Check if all the streams in active_streams have been connected
    :return: True if all active streams are connected, False otherwise
    """
    return _active_streams.intersection(connected_streams) == _active_streams

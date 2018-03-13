class Frame(object):
    def __init__(self, header=None, body=None):
        self.header = header
        self.body = body


class Header(object):
    def __init__(self, application=None, frame_type=None, protocol=None, time_stamp=None):
        self.application = application
        self.frame_type = frame_type
        self.protocol = protocol
        self.time_stamp = time_stamp


class Body(object):
    def __init__(self, device_info=None, user_info=None):
        self.device_info = device_info
        self.user_info = user_info
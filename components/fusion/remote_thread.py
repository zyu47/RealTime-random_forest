import threading
import socket
import select
import sys
import Queue

from .conf.endpoints import serve


class Remote(threading.Thread):

    def __init__(self, name, target, input_queue, conn_event):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name = name
        self.id = "[ " + name + " ]\t"
        self.target = target
        self.input_queue = input_queue
        self._stop = threading.Event()
        self._conn = conn_event

    def stop(self):
        self._stop.set()

    def is_stopped(self):
        return self._stop.is_set()

    def _log(self, msg):
        print self.id + msg

    def run(self):
        remote_sock = serve(self.target)
        remote_sock.listen(5)

        inputs = [remote_sock]
        outputs = []
        excepts = []

        self._log("Waiting for the destination to connect\n")

        while not self.is_stopped():
            try:
                read_socks, write_socks, except_socks = select.select(inputs, outputs, excepts, 0.02)
            except socket.error:
                # Only input is server socket, so exit if there is a problem
                self._log("Problem in the server socket. Stopping ...")
                sys.exit(0)

            for rs in read_socks:
                if rs is remote_sock:
                    client_sock, client_addr = rs.accept()
                    self._log("Accepted destination {}:{}".format(client_addr[0], client_addr[1]))
                    client_sock.shutdown(socket.SHUT_RD)
                    outputs += [client_sock]
                    if not self._conn.is_set():
                        self._conn.set()

            while True:
                try:
                    data = self.input_queue.get_nowait()

                    for ws in write_socks:
                        try:
                            client_addr = ws.getpeername()
                            ws.sendall(data)
                        except (socket.error, EOFError):
                            if ws in outputs:
                                outputs.remove(ws)
                            if len(outputs) == 0:
                                self._conn.clear()
                            self._log("{}:{} disconnected".format(client_addr[0], client_addr[1]))
                except Queue.Empty:
                    break

        self._log("Stopped")

        for s in outputs:
            s.close()

        remote_sock.close()
        self._conn.clear()

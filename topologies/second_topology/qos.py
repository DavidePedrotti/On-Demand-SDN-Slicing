import subprocess

class QoS:
    _instance = None
    _running = None

    def _new_(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QoS, cls).new_(cls, *args, **kwargs)
        return cls._instance

    def start_process(self, process, *args):
        if self._running is None:
            self._running = subprocess.call([process, *args])
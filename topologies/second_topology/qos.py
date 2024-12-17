import subprocess

class QoS:
    _instance = None
    _running = None

    def _new_(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QoS, cls).new_(cls, *args, **kwargs)
        return cls._instance

    def start_process(self, process, http_size, dns_size, icmp_size):
        if self._running is None:
            self._running = subprocess.call([process, http_size, dns_size, icmp_size])

    def stop_process(self):
        if self._running:
            self._running.kill()
            self._running = None

    def get_process(self):
        return self._running
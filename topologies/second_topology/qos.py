import subprocess

current_queues_path = "queues_uuids.txt"
old_queues_path = "old_queues.txt"
stderr_path = "errors.txt"
create_queue_script = "./createQueue.sh"

class QoS:
    _instance = None
    _running = None

    def _new_(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QoS, cls).new_(cls, *args, **kwargs)
        return cls._instance

    def start_process(self, *args):
        with open(current_queues_path, "r") as input_file:
            with open(old_queues_path, "w") as output_file:
                output_file.write(input_file.read())

        with open(current_queues_path, "w") as stdout_file:
            with open(stderr_path, "w") as error_file:
                self._running = subprocess.call([create_queue_script, *args], stdout=stdout_file, stderr=error_file)
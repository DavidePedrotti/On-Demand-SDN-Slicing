import subprocess
import os

qos_path = "qos_data"
current_queues_path = os.path.join(qos_path, "current_queues.txt")
old_queues_path = os.path.join(qos_path, "old_queues.txt")
stderr_path = os.path.join(qos_path, "stderr.txt")
create_queue_script = "./createQueue.sh"

class QoS:
    _instance = None
    _running = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QoS, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def start_process(self, *args):
        os.makedirs(qos_path, exist_ok=True)
        if os.path.isfile(current_queues_path):
            with open(current_queues_path, "r") as input_file, open(old_queues_path, "w") as output_file:
                output_file.write(input_file.read())

        with open(current_queues_path, "w") as stdout_file, open(stderr_path, "w") as error_file:
            self._running = subprocess.call([create_queue_script, *args], stdout=stdout_file, stderr=error_file)
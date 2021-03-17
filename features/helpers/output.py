import re


class LogParser:
    """ Parses output from lazy-kaniko image """

    def __init__(self, logs):
        self.logs = logs

    def tag(self) -> str:
        for line in self.logs.splitlines():
            print(line)
            match = re.search(r"Calculated image checksum as tag: (?P<tag>.*)", line)
            if match:
                return match.group("tag")
        raise ValueError("Unable to find tag in log lines")

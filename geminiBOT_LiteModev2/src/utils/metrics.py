class Metrics:
    def __init__(self):
        self.counters = {}

    def inc(self, name: str):
        self.counters[name] = self.counters.get(name, 0) + 1

    def get(self, name: str):
        return self.counters.get(name, 0)


metrics = Metrics()

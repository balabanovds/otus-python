import statistics, logging
from string import Template

class StatBuilder:
    all_counter = 0
    all_time_sum = 0.0
    data = {}


    def add_data(self, url: str, duration: float):
        self.all_time_sum += duration
        self.all_counter += 1
        if not url in self.data:
            self.data[url] = {
                'count': 0,
                'durations': [],
            }
        self.data[url]['count'] += 1
        self.data[url]['durations'].append(duration)

    def calculate_stats(self):
        for key, val in self.data.items():
            count = val['count']
            durations = val['durations']
            val['count_perc'] = count / self.all_counter * 100
            val['time_sum'] = sum(durations)
            val['time_perc'] = val['time_sum'] / self.all_time_sum * 100
            val['time_avg'] = val['time_sum'] / count
            val['time_max'] = max(durations)
            val['time_med'] = statistics.median(durations)
            val['url'] = key

    def create_report(self, to_file: str):
        fd = open('report.html', 'r')
        t = Template(fd.read())

        s = t.safe_substitute(table_json=self.get_data())
        fd = open(to_file, 'w')
        fd.write(s)

    def get_data(self) -> list:
        return list(self.data.values())
import re


class ValidationTimeMixin(object):

    def _validate_time(self, string_time):
        if isinstance(string_time, str):
            match = re.search("\D*((?P<days>\d*)(d)){0,1}\D*((?P<hours>\d*)(h)){0,1}\D*((?P<minutes>\d+)(m){0,1}){0,1}",
                              string_time)
            time = 0
            if match.group("minutes"):
                time = int(match.group("minutes"))
            if match.group('hours'):
                time = time + int(match.group("hours")) * 60
            if match.group('days'):
                time = time + int(match.group("days")) * 60 * 24
            return time
        else:
            return string_time

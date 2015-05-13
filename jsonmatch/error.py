
class MatchError(Exception):
    pass


class MatchConfigError(MatchError):
    def __init__(self, *args):
        super(MatchConfigError, self).__init__(*args)


class MatchKeyError(MatchError):
    def __init__(self, *args):
        super(MatchKeyError, self).__init__(*args)
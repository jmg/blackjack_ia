debug = False

class Log(object):

    @classmethod
    def log(cls, text):

        if debug:
            print text
from collections import defaultdict


class Logger(object):

    ''' The Logger class allows you to log PlanetWars data to log files.

        During game play log calls are stored in memory. When flush() is called
        any data logged is stored to one of the following log files:
         - results # contains the match result (win/loss score)
         - turns # contains turn-by-turn details
         - errors # contains any errors logged during the match
         - player_id # player log details, one file for each player.

        If messages have not been logged the corresponding file is not created.

    '''

    def __init__(self, filename_pattern):
        ''' Creates a log file at this file location.
            The pattern must contain one '%s' which will be replaced with the
            name of each log file.
        '''
        self._pattern = filename_pattern
        self._results = []
        self._turns = []
        self._errors = []
        self._players = defaultdict(list)

    def flush(self):

        def flushit(name, data):
            if data:
                f = open(self._pattern % name, 'w')
                f.writelines(data)
                f.close()

        flushit('results', self._results)
        flushit('turns', self._turns)
        flushit('errors', self._errors)

        for k, v in self._players.items():
            flushit('player' + str(k), v)

    def _append_message(self, log, message):
        if message[-1] != "\n":
            message = message + "\n"
        log.append(message)

    def result(self, message):
        ''' Use to set a match result message to file. '''
        self._append_message(self._results, message)

    def turn(self, message):
        ''' Use to set a turn result message to file. '''
        self._append_message(self._turns, message)

    def player(self, player_id, message):
        ''' Use to set a player message to file. '''
        self._append_message(self._players[player_id], message)

    def get_player_logger(self, player_id):
        ''' Wrap (decorate) the player() log method with the player_id. '''
        def player_log(message):
            self.player(player_id, message)
        return player_log

    def error(self, message):
        ''' Use to log error details. '''
        self._append_message(self._errors, message)

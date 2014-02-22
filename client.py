"""
Tron Battle client library. Basic code for talking to the server.
"""

from grid import TronGrid  # @include(grid.py)
from player import PlayerInfo  # @include(player.py)


class TronClient(object):

    def __init__(self, handler):
        self.handler = handler
        self.grid = TronGrid()
        self.players = {}
        self.my_number = 0
        self.players_count = 0

    @staticmethod
    def read_numbers():
        return map(int, raw_input().split())

    def handle_input(self):
        self.players_count, self.my_number = self.read_numbers()

        for i in xrange(self.players_count):
            x0, y0, x1, y1 = self.read_numbers()

            if i not in self.players:
                self.players[i] = PlayerInfo(i)
                if x0 != -1:
                    self.grid.put(x0, y0, i)
            else:
                # replace old head with body
                old_head = self.players[i].head
                self.grid.put(old_head[0], old_head[1], i)

            player = self.players[i]
            player.move(x0, y0, x1, y1)

            if player.is_alive:
                self.grid.put(x1, y1, 4 + i)
            else:
                self.remove_player(i)

    def remove_player(self, i):
        self.grid.replace(i, 0)

    def run(self):
        while 1:
            if self.players and not self.players[self.my_number].alive:
                return
            self.handle_input()
            print self.handler(players_count=self.players_count,
                    my_number=self.my_number, players=self.players,
                    grid=self.grid)

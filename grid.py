"""
Grid -- the field of the Tron Battle.
"""

from array import array
from collections import defaultdict
from copy import deepcopy, copy


class ProbeResult(object):
    """Result of a probe."""

    #: Value of the closest obstacle
    closest_obstacle = None
    #: Distance to the closest obstacle
    closest_obstacle_d = None

    def __init__(self, steps, empty_count, obj2dist, pois_reached):
        self.max_distance = steps
        self.empty_count = empty_count
        self.obj2dist = obj2dist
        self.objects = set(obj2dist.keys())
        self.pois_reached = pois_reached

        self.dist2obj = defaultdict(list)
        for obj, dist in obj2dist.items():
            self.dist2obj[dist].append(obj)

        if self.dist2obj:
            self.closest_obstacle_d = min(self.dist2obj.keys())
            self.closest_obstacle = self.dist2obj[self.closest_obstacle_d][0]


class TronGrid(object):

    """Data structure for the field of the tron battle.

    Coordinates are mapped to indices like this:

        idx = x + (y << 6)

    Then:

        x = idx & 63
        y = idx >> 6

    The size of the grid is 30 x 20 with some padding to avoid overflows with
    reasonably small moves. Initially the grid is filled with 0s for empty
    cells and -1s for walls.

    The values in the grid are signed integers. Assigned values are:

        * -1 wall
        * 0 empty space
        * 1-4 body of tron #1-4
        * 5-8 head of tron #1-4
    """

    DIRECTIONS = {
            'UP': -64,
            'DOWN': 64,
            'LEFT': -1,
            'RIGHT': 1
    }

    def __init__(self):
        self.grid = array('h', ([0] * 30 + [-1] * 34) * 20 + [-1] * 128)

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        ret = []
        for start in range(0, 64 * 20, 64):
            cells = ['{: >-2d}'.format(cell) if cell else '  '
                    for cell in self.grid[start:start + 30]]
            ret.append(' '.join(cells))
        ret = ['#' * len(ret[0])] + ret + ['#' * len(ret[0])]
        ret = ['#' + l + '#' for l in ret]
        return '\n'.join(ret)

    def __getitem__(self, idx):
        return self.grid[idx]

    def __setitem__(self, idx, value):
        self.grid[idx] = value

    @staticmethod
    def head_of(player_number):
        return player_number + 8

    @staticmethod
    def body_of(player_number):
        return player_number + 4

    @staticmethod
    def coords2index(x, y):
        return x + (y << 6)

    @staticmethod
    def index2coords(idx):
        return idx & 63, idx >> 6

    def put(self, x, y, value):
        self.grid[self.coords2index(x, y)] = value

    def get(self, x, y):
        return self.grid[self.coords2index(x, y)]

    def replace(self, src, dst):
        for i, value in enumerate(self.grid):
            if value == src:
                self.grid[i] = dst

    def bfs_fill(self, value, origins, empty=0):
        directions = self.DIRECTIONS.values()
        grid = self.grid

        while origins:
            new_origins = []
            for origin in origins:
                for d in directions:
                    idx = origin + d
                    if grid[idx] == empty:
                        grid[idx] = value
                        new_origins.append(idx)
            origins = new_origins

    def bfs_probe(self, start_idx, pois={}, limit=None, empty=0):
        """See how far we can get from the ``start_idx``.

        Returns the information about the surroundings of that point:

            * Max distance walked,
            * Number of passed positions that are empty,
            * List of objects encountered and the distances to them,
            * List of POIs reached (taken out of ``pois`` set).

        If ``limit`` is specified, don't probe beyond that many steps.
        """
        directions = self.DIRECTIONS.values()
        grid = copy(self.grid)  # This method doesn't change the grid.
        origins = [start_idx]
        steps = -1
        empty_count = 0
        pois_left = set(pois)
        pois_reached = set()
        obj2dist = {}
        marker = 32000

        while origins:
            steps += 1
            if limit is not None and steps >= limit:
                break
            new_origins = []
            for origin in origins:
                for d in directions:
                    idx = origin + d
                    if idx == start_idx: continue
                    value = grid[idx]
                    if value == empty:
                        grid[idx] = marker
                        new_origins.append(idx)
                        empty_count += 1
                    elif value != marker:
                        if value not in obj2dist:
                            obj2dist[value] = steps + 1
                    if idx in pois_left:
                        pois_reached.add(idx)
                        pois_left.remove(idx)
            origins = new_origins
        print obj2dist

        return ProbeResult(steps, empty_count, obj2dist, pois_reached)

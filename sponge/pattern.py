import os
import numpy as np

class Sequence():
    def __init__(self, fname=None, source="./source", delimiter=","):

        if fname is None:
            fname = choose_file(source)

        self.fname = fname

        path = os.path.join(source, fname)

        self.patterns = parse_file(path, delimiter=delimiter)
        self.current = 0

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.patterns[self.current]
        except IndexError:
            raise StopIteration

        self.current += 1
        return result

def choose_file(src):
    """Function to list files and ask
    for index to select filename."""

    # Get files in directory "src"
    files = os.listdir(src)

    # Print items.
    print("Choose a file:")
    for i, f in enumerate(files):
        print("%d) - %s" % (i, f))

    # Ask for input from user (convert to integer)
    select = int(input("Enter number: "))

    return files[select]

def parse_file(fname, delimiter=","):
    """Function to load pattern sequence file and
    parse it so we can use it to run patterns."""

    # load the file
    with open(fname, "r") as f:
        l = f.readlines()

    # Strip lines
    lines = [line.strip().split(delimiter) for line in l]

    # Extract info from file and put
    # in dictionary
    patterns = []
    for line in lines:
        # Skip line with "X"
        if line[0].capitalize() == "X":
            continue

        # Extract pattern number
        p = [val for val in line if "P" in val][0]
        n = int(p[1:])

        # The columns before the current pattern
        precols = line[:line.index(p)]

        # Extract values for each motor from line
        motors = line[line.index("S%d" % n)+1: line.index("I%d" % n)]
        active = line[line.index("E%d" % n)+1: line.index("S%d" % n)]
        intensities = line[line.index("I%d" % n)+1: len(line)]

        # Convert to integers
        motors = [int(val) for val in motors]
        active = [int(val) for val in active]
        intensities = [int(val) for val in intensities]


        # Get list indices for
        # All values
        pattern = {
            "number"       : p,
            "duration"      : float(line[line.index("D%d" % n)+1]),
            "active"        : active,
            "motors"        : motors,
            "intensities"   : intensities,
        }

        # Include additional columns that
        # appeared before the Pattern number
        for i, col in enumerate(precols):
            pattern.update({"col%d"%i: col})

        # Store pattern
        patterns.append(pattern)

    return patterns


def create_motor_layout(ncols, nrows):
    return np.arange(nrows*ncols).reshape((nrows, ncols))


def get_difference_motor_position(m0, m1, ncols=4, nrows=4):

    motors = create_motor_layout(ncols, nrows)

    ys, xs = np.indices(motors.shape)
    coords0 = np.array((xs[motors == m0], ys[motors == m0]))
    coords1 = np.array((xs[motors == m1], ys[motors == m1]))
    x, y = np.squeeze(coords1 - coords0)

    return x, y

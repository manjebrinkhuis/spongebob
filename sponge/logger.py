import os
import pandas as pd
import csv
import sys

if sys.version_info.major == 2:
    input = raw_input

class Logger():
    """Create a file to log pattern and responses.
    If the file exists, you will be prompted to
    give different specifications."""
    def __init__(self,
                 participant=0,
                 condition=0,
                 session=0,
                 location="./data"
                 ):

        # Create filename
        fname = "part_%03d_cond_%03d_sess_%03d.csv" % (
            int(participant),
            int(condition),
            int(session))

        # If file exists loop new attempts
        while os.path.exists(os.path.join(location, fname)):
            overwrite = input("File exists. Overwrite (y/N)? ")

            if overwrite in ["y", "Y", "yes"]:
                break
            else:
                # Create new filename.
                participant = input("participant: ")
                condition = input("condition: ")
                session = input("session: ")
                fname = "part_%03d_cond_%03d_sess_%03d.csv" % (
                    int(participant),
                    int(condition),
                    int(session))

        self.path = os.path.join(location, fname)

        # Create empty file
        self.header = True
        open(self.path, "w").close()

    def log(self, data):
        with open(self.path, "a") as f:
            pd.DataFrame(data).to_csv(f,
                index=False,
                header=self.header,
                quoting=csv.QUOTE_ALL)
        self.header = False

#!/usr/bin/env python

"""
Parse data from Expedition CSV file
"""

import pandas as pd


class Expedition:
    """
    Parse CSV file of expedition data and return as an object.
    """
    def __init__(self, csv_file):
        self._load_2018_dataframe(csv_file)


    def subset(self, taxon):
        """
        Return data only for a selected taxon
        """
        mask = self.data.shortname.apply(lambda x: taxon in x)
        subset = self.data[mask].reset_index()
        return subset


    def _load_2018_dataframe(self, csv_file):
        """
        Parse the data file.
        """
        # load Data
        data = pd.read_csv(csv_file)

        # drop unidentified
        data = data[data.species_epithet.notna()]

        # select just the columns we want
        data = data[["accession", "locality", "date", "latitude", "longitude", "genus", "species_epithet"]]
        data["shortname"] = data[["genus", "species_epithet"]].apply(lambda x: '-'.join(x), axis=1)

        # convert lat longs to decimals
        data["lat"] = data.latitude.apply(convert_gps)
        data["long"] = data.longitude.apply(convert_gps)

        # get year from the date data
        data["year"] = data.date.apply(lambda x: x.split("/")[-1])

        # store accession as a short name "cid"
        data["cid"] = data["accession"]

        # convert label names to match with Hengduan object
        data = data.drop(columns=["latitude", "longitude", "genus", "species_epithet", "date", "accession"])
        data = data.rename({"lat": "latitude", "long": "longitude", "locality": "sid"}, axis='columns')

        # reset index
        self.data = data.reset_index(drop=True)




def convert_gps(tude):
    """
    Convert a degree, minute, second coordinate to decimals.
    """
    deg, _ = tude.split("°")
    minu, _ = _.split("'")
    seco = _.split('"')[0]
    tude = "-".join([deg, minu, seco])
    return sum(float(x) / 60 ** n for n, x in enumerate(tude.split('-')))  

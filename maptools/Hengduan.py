#!/usr/env/bin python

"""
A Class object for scraping data from the Hengduan database.
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
import pandas as pd



class Hengduan:
    "Search the Hengduan database and return a dataframe"

    def __init__(self, taxon, dna=True,):
        # class globals
        baseurl = "http://hengduan.huh.harvard.edu/fieldnotes/"
        self.search_url = baseurl + "specimens/search/search.zpt"
        self.specimen_url = baseurl + "specimens/search/specimen_detail.zpt"

        # class attrs
        self.taxon = taxon
        self.dna = ["on" if True else "off"][0]
        self.data = None

        # do search and fill database
        if self._get_search_data():
            self._fill_data_coords()


    def _search_request(self):
        # slow it down by waiting one second
        time.sleep(1)
        res = requests.get(
            url=self.search_url,
            params={
                "dna_collection": self.dna, 
                "st": self.taxon,
                "action": "search", 
                "submit_button": "Search",
            }
        )
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")


    def _get_search_data(self):
        soup = self._search_request()
        table = soup.find('table', attrs={"class": "listing", "id": "angio_table"})
        if table:
            headers = [header.text for header in table.find_all('th')]
        # if no record then return 0
        else:
            return 0

        headers.extend(["specimen-id"])
        rows = []
        for row in table.find_all('tr')[1:]:
            tds = row.find_all('td')
            row = [val.text.strip() for val in tds]
            tmp = [i.a for i in tds][2]
            spid = (tmp.attrs['href'].split("=")[-1])
            row.extend([spid])
            rows.append(row)
        self.data = pd.DataFrame(
            rows, 
            columns=["family", "taxon", "cid", "cdate", "", "sid"]
        )
        self.data['year'] = (
            self.data["cdate"]
             .apply(str.split)
             .apply(lambda x: x[-1])
            )
        self.data = self.data.drop(["cdate", ""], axis=1)
        # add shortname ref
        self.data["shortname"] = (
            self.data
            .taxon
            .apply(str.split)
            .apply("-".join)
        )
        # on success return 1
        return 1


    def _specimen_request(self, spid):
        res = requests.get(
            url=self.specimen_url,
            params={
                "specimen_id": spid,
            }
        )
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")


    def _get_coordinates(self, specid):
        soup = self._specimen_request(specid)
        textlocs = soup.find(id="locality")
        text = textlocs.find_all("td")[1].text.split("\n")
        # descr = " ".join([i.strip() for i in text][1:4])
        tmp0, tmp1 = text[-3].strip().split("°")
        tmp0, tmp1
        tmp1, tmp2 = tmp1.split("\'")
        tmp2 = tmp2.lstrip(";").rstrip(";").replace('"', '')
        point = "-".join([tmp0, tmp1, tmp2])
        eastwest = self._convert_gps(point)

        tmp0, tmp1 = text[-4].strip().split("°")
        tmp1, tmp2 = tmp1.split("\'")
        tmp2 = tmp2.lstrip(";").rstrip(",").replace('"', '')
        point = "-".join([tmp0, tmp1, tmp2])
        northsouth = self._convert_gps(point)
        return (northsouth, eastwest)


    @staticmethod
    def _convert_gps(tude):
        multiplier = 1 if tude[-1] in ['N', 'E'] else -1
        return multiplier * sum(float(x) / 60 ** n for n, x in enumerate(tude[:-1].split('-')))


    def _fill_data_coords(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            jobs = [executor.submit(
                self._get_coordinates, specid) for specid in self.data.sid]
            res = [i.result() for i in jobs]

        self.data['latitude'] = [i[0] for i in res]
        self.data['longitude'] = [i[1] for i in res]


    def count_by_maxyear(self, year):
        try:
            return (
             self.data[self.data.year.astype(int) <= year]
             .sort_values(by=["year", "shortname"])
             .groupby('shortname')
             .apply(len)
             .sort_values(ascending=False)
            )
        except TypeError:
            return None


    def filter_by_max_year(self, year):
        try:
            return (
             self.data[self.data.year.astype(int) <= year]
             .sort_values(by=["year", "shortname"])
            )
        except TypeError:
            return None



if __name__ == "__main__":

    test = Hengduan(taxon="Ped cranolopha", dna=True)
    test.filter_by_max_year(1998)

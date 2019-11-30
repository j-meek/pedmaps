#!/usr/bin/env python

"""
Generate a Leaflet map constructed using folium
"""

import folium
import numpy as np
import pandas as pd



class Map:
    """
    Map object.

    Parameters
    ==========

    data (pandas.DF)
        Data to center the coordinates.
    height (int, str)
        If int then sets height as n pixels, else write string perc. (100%).
    width (int, str)
        If int then sets width as n pixels, else write string perc. (100%).
    """
    def __init__(
        self, 
        data=None,
        height="100%", 
        width="100%",
        ):

        # attributes that will be updated 
        self.map = None
        self.data = None

        # store attributes
        if data is not None:
            if isinstance(data, (list, tuple)):
                self.data = pd.concat(self.data, sort=False)
            else:
                self.data = data
            location = [
                self.data.latitude.median(), 
                self.data.longitude.median(),
            ]
        else:
            location = [30.3849, 101.0083]

        # create map with zoom x and location y
        self.map = folium.Map(           
            zoom_start=6.5,
            location=location,
            tiles='Stamen Terrain',
            height=height,
            width=width,
        )


    def draw(self, fit_bounds=False):
        """
        Return rendered Canvas ...
        """
        # TODO: fit bounds of map to show all points
        if fit_bounds:
            latlongtuples = [
                self.data[["latitude", "longitude"]].iloc[i].tolist() 
                for i in self.data.index
            ]
            self.map.fit_bounds(latlongtuples)
        return self.map


    def add_markers(self, df, styledict=None):        
        """
        Add points on the map for each lat,long point in df
        """

        # parse styles in case entered as a list/arr
        size = style_to_list(styledict.get("size"), df, 5)
        stroke = style_to_list(styledict.get("stroke"), df, "black")
        stroke_width = style_to_list(styledict.get("stroke-width"), df, 2)
        stroke_opacity = style_to_list(styledict.get("stroke-opacity"), df, 0.9)
        fill = style_to_list(styledict.get("fill"), df, "black")
        fill_opacity = style_to_list(styledict.get("fill-opacity"), df, 0.5)

        # popup = style_to_list(styledict.get("stroke"), default=)

        # build markers for each point
        for idx in df.index:

            # get lat,long
            elat = df.iloc[idx].latitude
            elon = df.iloc[idx].longitude

            # make popup info
            popup = " | ".join(
                df.iloc[idx][["shortname", "cid", "year"]].tolist())

            # create the marker
            marker = folium.CircleMarker(
                location=[elat, elon],
                fill=True,                        # always 'true'
                fill_color=fill[idx],             # fill
                fill_opacity=fill_opacity[idx],   # fill-opacity
                color=stroke[idx],                # stroke
                weight=stroke_width[idx],         # stroke-width
                opacity=stroke_opacity[idx],      # stroke-opacity
                radius=str(size[idx]),            # size
                popup=popup,
                # icon=folium.Icon(color="blue", icon="circle", prefix="fa"),
            )

            # add merker to the map
            marker.add_to(self.map)


def style_to_list(style, df, default=None):
    """
    Extend single styles into a list of correct length    
    """
    # set style to default value
    if style is None:
        style = default

    # if list assert list is correct length
    if isinstance(style, (list, np.ndarray)):
        assert len(style) == df.shape[0]
        return style

    # if single then extend to a list
    else:
        style = [style] * df.shape[0]
        return style



def scale_range(data, minsize=2, maxsize=8, nbins=10, reverse=False):
    """
    Group a range of data into bins spanning from minsize to maxsize
    """
    # arr to be returned
    newvals = np.zeros(data.shape[0])

    # transform
    vals = data.astype(float)
    bins = np.histogram(vals, bins=nbins)[0]
    sizes = np.linspace(minsize, maxsize, nbins)

    if reverse:
        vals = vals[::-1]
        svals = sorted(vals, reverse=reverse)
        sizes = sizes[::-1]
        bins = bins[::-1]
    else:
        svals = sorted(vals)

    # set values
    vidx = 0
    sidx = 0
    for sbin in bins:

        # if there are any in this bin
        if sbin:

            # get n next values
            val = svals[vidx:vidx + sbin]
            siz = sizes[sidx]
            for v in val:
                newvals[vals == v] = siz
            sidx += 1
            vidx += sbin
    return newvals



def year_to_size(x):
    """
    Scales years to be different sized markers
    """
    diff = x - 1995
    ndiff = 1 - (diff / 25)
    return 12 * np.sqrt(ndiff)

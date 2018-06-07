import numpy as np

from .. georecords import GeoRecords
from .. import (
    nptools,
    projection,
    transformation,
)


def loadPtx(fileName, sep=' ', proj=None, bulk=500000):
    """Loads points from a .ptx file.

    Parameters
    ----------
    ptx_file : String
        File to be read.
    sep : Sting
        Column seperator string.
    proj : optional, Proj
        Projection associated with the points.
    bulk : optiona, positive int
        Bulk size.


    Notes
    -----
    Implemented for testing reasons. Not indended to be used.

    """

    # Read
    header = []
    with open(fileName) as f:
        for i in range(10):
            header.append(f.readline())
    T1 = np.array([np.fromstring(header[i], sep=sep) for i in range(2, 5)])
    T2 = np.array([np.fromstring(header[i], sep=sep) for i in range(6, 10)])

    dtypes = [('coords', np.float, 3), ('intensity', float)]
    cols = [0, 1, 2, 3]

    records = nptools.loadCsv(
        fileName,
        dtypes,
        skip=10,
        cols=cols,
        sep=sep,
        bulk=bulk)
    records['coords'] = transformation.transform(records['coords'], T2)
    records['intensity'] = records['intensity'] * 100

    # Filter missing values
    mask = np.any(
        (records.coords[:, 0] == 0, records.coords[:, 1] == 0, records.coords
         [:, 2] == 0),
        axis=0)
    records = records[~mask]

    if proj is None:
        proj = projection.Proj()

    return GeoRecords(proj, records)

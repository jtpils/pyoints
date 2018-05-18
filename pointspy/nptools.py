"""Provides functions for convienient handling of numpy arrays.
"""

import numpy as np


def isarray(o):
    """Checks weather or nor an object is an array.

    Parameters
    ----------
    o : object
        Some object.

    Returns
    -------
    bool
        Indicates weather or not the object is an array.

    Example
    -------

    >>> isarray([1, 2, 3])
    True
    >>> isarray('text')
    False

    """
    return hasattr(o, '__getitem__') and hasattr(o, '__iter__')


def isnumeric(arr, dtypes=[np.int32, np.int64, np.float32, np.float64]):
    """Checks if the data type of an `numpy.ndarray` is numeric.

    Parameters
    ----------
    arr : np.ndarray
        Numpy array to check.
    dtypes : optional, tuple
        Tuple of allowed numeric data types.

    Returns
    -------
    bool
        Indicates weather or not the array is numeric.

    Example
    -------

    >>> isnumeric([1, 2, 3])
    True
    >>> isnumeric(['1', '2', '3'])
    False
    >>> isnumeric([1, 2, None])
    False

    """
    if not isarray(arr):
        raise ValueError("'arr' needs to an array like object")
    if not isinstance(arr, np.ndarray):
        arr = np.array(arr)
    if not isinstance(dtypes, list):
        raise ValueError("'dtypes' needs to be a list. got %s" % (str(dtypes)))
    for dtype in dtypes:
        if np.issubdtype(arr.dtype.type, np.dtype(dtype).type):
            return True
    return False


def haskeys(d):
    """Checks if object has keys and can be used like a dictionary.

    Parameters
    ----------
    d : object
        Object to be checked.

    Returns
    -------
    bool
        Indicates weather or not the object has accessable keys.

    Examples
    --------

    >>> haskeys({'a': 5, 'b': 3})
    True
    >>> haskeys([5, 6])
    False
    >>> haskeys(np.recarray(3, dtype=[('a', int)]))
    False

    """
    return hasattr(d, '__getitem__') and hasattr(d, 'keys')


def missing(data):
    """Find missing values.

    Parameters
    ----------
    data : array_like
        A array like object to search missing values for. Missing values are
        either None or NaN values.

    Returns
    -------
    array_like(bool)
        Boolean values indicate missing values.

    Examples
    --------

    Finding missing values in a list.

    >>> arr = ['str', 1, None, np.nan, np.NaN]
    >>> print(missing(arr))
    [False False  True  True  True]

    Finding missing values in multidimensional arrays.

    >>> arr = np.array([(0,np.nan),(None, 1),(2, 3)], dtype=float)
    >>> print(missing(arr)
    [[False  True]
     [ True False]
     [False False]]

    """

    if not hasattr(data, '__len__'):
        raise ValueError("'data' has be a array like object")
    strings = np.array(data, dtype=str)

    ismissing = np.equal(data, None)
    ismissing[strings == 'nan'] = True

    return ismissing


def recarray(dataDict, dtype=[], dim=1):
    """Converts a dictionary of array like objects to a numpy record array.

    Parameters
    ----------
    dataDict : dict
        Dictionary of array like objects to convert to a numpy record array.
    dtype : optional, numpy.dtype
        Describes the desired data type of specific fields.
    dim : positive int
        Desired dimension of the resulting numpy record array.

    Returns
    -------
    np.recarray
        Numpy record array build from input dictionary.

    Examples
    --------

    Creation of an numpy record array using a dictionary.

    >>> rec = recarray({
    ...    'coords': [ (3, 4), (3, 2), (0, 2), (5, 2)],
    ...    'text': ['text1', 'text2', 'text3', 'text4'],
    ...    'n':  [1, 3, 1, 2],
    ...    'missing':  [None, None, 'str', None],
    ... })
    >>> rec.dtype.descr
    [('text', '|S5'), ('missing', '|O'), ('coords', '<i8', (2,)), ('n', '<i8')]
    >>> print(rec.coords)
    [[3 4]
     [3 2]
     [0 2]
     [5 2]]
    >>> print(rec[0]
    ('text1', None, [3, 4], 1)

    Create a two dimensional array.

    >>> data = {
    ...    'coords': [
    ...                 [(2, 3.2), (-3, 2.2)],
    ...                 [(0, 1.1), (-1, 2.2)],
    ...                 [(-7, -1), (9.2, -5)]
    ...             ],
    ...    'values': [[1, 3], [4, 0], [-4, 2]]
    ... }
    >>> rec = recarray(data, dim=2)
    >>> print(rec.shape)
    (3, 2)
    >>> print(rec.values)
    [[ 1  3]
     [ 4  0]
     [-4  2]]
    >>> print(rec.dtype)
    (numpy.record, [('values', '<i8'), ('coords', '<f8', (2,))])

    """

    if not haskeys(dataDict):
        raise ValueError("'dataDict' has to be a dictionary like object")

    # check data types
    dtype = np.dtype(dtype)
    for key in dtype.names:
        if key not in dataDict.keys():
            raise ValueError('column "%s" not found!' % key)

    if not isinstance(dim, int) and dim > 0:
        raise ValueError("'dim' has to be an integer greater zero")

    # convert to numpy arrays if neccessary
    for key in dataDict.keys():
        if not isinstance(dataDict[key], (np.ndarray, np.recarray)) and key not in dtype.names:
            dataDict[key] = np.array(dataDict[key], copy=False)

    # get shape
    shape = dataDict[dataDict.keys()[0]].shape
    for key in dataDict.keys():
        s = dataDict[key].shape
        if len(s) < dim:
            raise ValueError('shape "%s" needs to be least of dimension "%i"' % (str(s), dim))
        if not s[:dim] == shape[:dim]:
            raise ValueError('incompatible shape of field "key"' % key)

    # get data types
    outDtypes = []
    for key in dataDict.keys():
        if key in dtype.names:
            dt = dtype[key]
        else:
            arr = dataDict[key]
            dt = (key, arr.dtype.descr[0][1], arr.shape[dim:])
        outDtypes.append(dt)

    # define array
    rec = np.recarray(shape[:dim], dtype=outDtypes)
    for key in dataDict.keys():
        rec[key][:] = dataDict[key]

    return rec


def add_fields(arr, dtypes, data=None):
    """Adds fields to numpy record array.

    Parameters
    ----------
    arr : numpy.ndarray
        Numpy array to add field to.
    dtypes : np.dtype
        Data types of the new fields.
    data : optional, list of arrays
        Data values of the new fields.

    Returns
    -------
    np.recarray
        Record array similar to `A`, but with additional fields.

    Examples
    --------

    >>> A = recarray({'a': [0, 1, 2, 3]})
    >>> C = add_fields(A, [('b', float, 2), ('c', int)])
    >>> print(C.dtype.descr)
    [('a', '<i8'), ('b', '<f8', (2,)), ('c', '<i8')]

    >>> D = add_fields(A, [('d', int), ('e', str)], data=[[1, 2, 3, 4], None])
    >>> print(D
    [(0, 1, '') (1, 2, '') (2, 3, '') (3, 4, '')]

    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("'arr' has to be an instance of 'np.ndarray'")
    if data is not None and not hasattr(data, '__iter__'):
        raise ValueError("'data' has to be iterable")

    dtypes = np.dtype(dtypes)

    # check for duplicate fields
    for name in dtypes.names:
        if name in arr.dtype.names:
            raise ValueError('field "%s" already exists' % name)

    newDtypes = arr.dtype.descr + dtypes.descr

    # set values
    rec = np.recarray(arr.shape, dtype=newDtypes)
    for name in arr.dtype.names:
        rec[name] = arr[name]

    # set new values
    if data is not None:
        for name, column in zip(dtypes.names, data):
            if column is not None:
                rec[name] = column

    return rec


def fuse(*recarrays):
    """Fuses two numpy record arrays of identical shape to one array.

    Parameters
    ----------
    *recarrays : np.recarray
        Numpy recarrays to fuse.

    Returns
    -------
    np.recarray
        Record array with same fields as `A` and `B`.

    Examples
    --------

    One dimensional arrays.

    >>> A = recarray({'a': [0, 1, 2, 3]})
    >>> B = recarray({'b': [4, 5, 6, 7]})
    >>> C = fuse(A, B)
    >>> print(C.shape)
    (4,)
    >>> print(C.dtype.names
    ('a', 'b')

    Two dimensional arrays.

    >>> A = recarray({'a': [[0, 1], [2, 3]]}, dim = 2)
    >>> B = recarray({'b': [[4, 5], [6, 7]]}, dim = 2)
    >>> C = fuse(A, B)
    >>> print(C.shape)
    (2, 2)
    >>> print(C)
    [[(0, 4) (1, 5)]
     [(2, 6) (3, 7)]]

    """

    shape = None
    dtype = []
    for arr in recarrays:
        if not isinstance(arr, np.recarray):
            raise ValueError("all arrays have to be of type 'np.recarray'")
        dtype.extend(arr.dtype.descr)

        # check shape
        if shape is None:
            shape = arr.shape
        elif not arr.shape == shape:
            raise ValueError("all arrays have to have the same shape")

    # define array
    fused = np.recarray(shape, dtype=dtype)
    for arr in recarrays:
        for name in arr.dtype.names:
            fused[name] = arr[name]

    return fused


def merge(*arrays):
    """Merges multiple arrays.

    Parameters
    ----------
    arrays : array_like
        List of numpy arrays to merge.

    Returns
    -------
    np.ndarray
        Merged numpy record array.

    Examples
    --------

    One dimensional arrays.

    >>> A = recarray({'a': [0, 1, 2, 3]})
    >>> B = recarray({'b': [4, 5, 6, 7]})
    >>> C = merge(A.a, B.b)

    """
    # TODO enable for np.recarray
    for arr in arrays:
        # TODO welcher typ?
        if not isinstance(arr, np.ndarray):
            ValueError("all values have to be of type 'np.recarray'")

    # TODO bug
    return arrays[0].__array_wrap__(np.hstack(arrays))


def flatten_dtypes(np_dtypes):
    """Exract name, datatype and shape information from numpy data type.

    Parameters
    ----------
    np_dtypes : np.dtype
        Numpy data types to flatten.

    Returns
    -------
    names : list of str
        Names of fields.
    dtypes : list of dtypes
        Data types of fields.
    shapes : list of tuples
        Shapes of fields.

    Examples
    --------

    >>> dtype = np.dtype([
    ...     ('simple', int),
    ...     ('multidimensional', float, 3),
    ... ])
    >>> names, dtypes, shapes = flatten_dtypes(dtype)
    >>> names
    ['simple', 'multidimensional']
    >>> dtypes
    [dtype('int64'), dtype('float64')]
    >>> shapes
    [0, 3]

    """

    # ensure data type
    np_dtypes = np.dtype(np_dtypes)

    dtypes = []
    shapes = []
    names = list(np_dtypes.names)

    for name in names:

        dtype = np_dtypes[name]
        shape = 0

        subDtype = dtype.subdtype
        if subDtype is not None:
            shape = dtype.shape[0]
            dtype = dtype.subdtype[0]

        dtypes.append(dtype)
        shapes.append(shape)

    return names, dtypes, shapes


def unnest(rec):
    """Unnest a numpy record array. Recursively adds each named field to a list.

    Parameters
    ----------
    rec: np.recarray
        Numpy record array to unnest.

    Returns
    -------
    list
        List of unnested fields.

    Examples
    --------

    >>> dtype = [
    ...    ('regular', np.int, 1),
    ...    ('nested', [
    ...         ('child1', '|S0'),
    ...         ('child2', np.float, 2)
    ...    ])
    ... ]
    >>> rec = np.ones(2, dtype=dtype).view(np.recarray)
    >>> print(rec.nested.child2
    [[1. 1.]
     [1. 1.]]
    >>> unnested = unnest(rec)
    >>> print(unnested[0])
    [1 1]
    >>> print(unnested[1])
    ['' '']
    >>> print(unnested[2])
    [[1. 1.]
     [1. 1.]]

    """

    if not isinstance(rec, (np.recarray, np.ndarray)):
        raise ValueError("'rec' has to a 'np.recarray' or 'np.ndarray'")

    if rec.dtype.names is None:
        ret = [rec]
    else:
        ret = []
        for name in rec.dtype.names:
            ret.extend(unnest(rec[name]))
    return ret


def colzip(arr):
    """Splits a two dimensional np.ndarray into a list of columns.

    Parameters
    ----------
    arr : (n, k), np.ndarray
        Numpy array with `n` rows and `k` columns.

    Returns
    -------
    columns : list of np.ndarray
        List of `k` numpy arrays.

    Examples
    --------

    >>> arr = np.eye(3, dtype=int)
    >>> cols = colzip(arr)
    >>> len(cols)
    3
    >>> print(cols[0])
    [1 0 0]

    """
    if not (isinstance(arr, np.ndarray) and len(arr.shape) == 2):
        raise ValueError("'arr' has be a two dimensional np.ndarray")

    return [arr[:, col] for col in range(arr.shape[1])]


def fields_view(arr, fields, dtype=None):
    """TODO

    Parameters
    ----------
    TODO

    Returns
    -------
    TODO

    Examples
    --------
    TODO

    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("'arr' has be a 'np.ndarray'")

    if dtype is None:
        dtype = np.dtype({name: arr.dtype.fields[name] for name in fields})
    return np.ndarray(arr.shape, dtype, arr, 0, arr.strides)


def apply_function(ndarray, func, dtypes=None):
    """Applies a function to each record of a numpy array.

    Parameters
    ----------
    ndarray : np.ndarray
        Numpy array to apply function to.
    func : function
        Function to apply to each record.
    dtypes : optional, np.dtype
        Desired data type of the output array.

    Returns
    -------
    np.recarray
        Record array similar to input array, but with function applied to.

    Examples
    --------

    Numpy ndarray.

    >>> data = { 'a': [0, 1, 2, 3], 'b': [1, 2, 3, 4] }
    >>> arr = np.ones((2, 3), dtype=[('a', int), ('b', int)])
    >>> func = lambda item: item[0] + item[1]
    >>> print(apply_function(arr, func))
    [[2 2 2]
     [2 2 2]]

    One dimensional case with aggregation.

    >>> data = { 'a': [0, 1, 2, 3], 'b': [1, 2, 3, 4] }
    >>> arr = recarray(data)
    >>> func = lambda record: record.a + record.b
    >>> print(apply_function(arr, func))
    [1 3 5 7]

    Two dimensional case.

    >>> data = { 'a': [[0, 1], [2, 3]], 'b': [[1, 2], [3, 4]] }
    >>> arr = recarray(data, dim=2)
    >>> func = lambda record: record.a ** record.b
    >>> print(apply_function(arr, func))
    [[ 0  1]
     [ 8 81]]

    Multiple output data types.

    >>> func = lambda record: (record.a + record.b, record.a ** record.b)
    >>> print(apply_function(arr, func, dtypes=[('c', float), ('d', int)])
    [[(1.,  0) (3.,  1)]
     [(5.,  8) (7., 81)]]

    """
    if not hasattr(func, '__call__'):
        raise ValueError("'func' needs to be callable")
    if not isinstance(ndarray, np.ndarray):
        raise ValueError("'ndarray' needs to an instance of np.ndarray")
    if dtypes is not None:
        dtypes = np.dtype(dtypes)

    args = np.broadcast(None, ndarray)
    values = [func(*arg[1:]) for arg in args]
    res = np.array(values, dtype=dtypes)
    res = res.reshape(ndarray.shape)
    return res.view(np.recarray)

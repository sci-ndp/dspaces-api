import math

from api.models import Interval, BoundingBox

def get_corners_from_bounds(box: BoundingBox):
    '''
    Convert bounding box start and span list into upper and lower bounds

    Parameters
    ----------
    box
        Contains a list of start, span pairs in order to define an extent in n-dimensional space
    
    Returns
    -------
    Two tuples of length n, containing the lower and upper bounds of box
    '''
    lb = tuple([b.start for b in box.bounds])
    ub = tuple([(b.start+b.span)-1 for b in box.bounds])
    return (lb,ub)

def get_bounds_from_corners(lb = tuple[int], ub = tuple[int]) -> list[Interval]:
    '''
    Convert upper and lower bounds into start and span list

    Parameters
    ----------
    lb
        Contains a list of lower bound coordinates
    ub
        Contains a list of upper bound coordinates (must be same length as lb)

    Returns
    -------
    A list of start/span pairs that define the bounding box
    '''
    if len(lb) != len(ub):
        raise ValueError('lb and ub must have same length')
    return [Interval(start=a, span=(b-a)+1) for a,b in zip(lb, ub)]

def get_box_volume(box: BoundingBox) -> int:
    '''
    Get the number of elements spanned by a box

    Parameters
    ----------
    box
        Contains a list of start, span pairs in order to define an extent in n-dimensional space

    Returns
    -------
    The product of the spans of box
    '''
    return math.prod([b.span for b in box.bounds])
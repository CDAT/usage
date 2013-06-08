from datetime import datetime, timedelta
from django.db import connection
from django.utils import timezone



def get_machine_count_for_sources(startDate=datetime(1900, 01, 01),
                                  endDate=datetime.now() + timedelta(days=1),
                                  sliceHrs=24):
    """
    Queries the database and returns the number of unique machines that have
    used each source.
    Returns: A list of lists. Sublists take the form of:
        ('source name', 'source version', 'num of unique machines')
    """
    # validate input before we use it in a query
    if(type(startDate) != datetime):
        raise TypeError("startDate had invalid type '%s'. Must pass a datetime" % (type(startDate)))
    if(type(endDate) != datetime):
        raise TypeError("endDate had invalid type '%s'. Must pass a datetime" % (type(endDate)))
    
    
    cursor = connection.cursor()
    cursor.execute(
        """SELECT name, version, count(machine_id) AS total
            FROM(
                SELECT DISTINCT machine_id, source_id FROM logevent
                WHERE logevent.date
                    BETWEEN '%s' and '%s'
            ) log
        JOIN sources src
            ON (log.source_id = src.id)
        GROUP BY version;""" % (str(startDate), str(endDate))
    )
    return cursor.fetchall()

def _setupTest():
    """
    A little helper function to make debugging less tedious.
    """
    start = datetime.now() - timedelta(days=10)
    end = datetime.now()
    return (start, end)


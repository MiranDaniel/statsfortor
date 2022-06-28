import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from io import StringIO, BytesIO
from datetime import datetime
import time
import numpy as np
import matplotlib.dates as mdates
import math
import base64

def plot(write, read, unit, first, last, title, log=False):
    fig, ax = plt.subplots(figsize=(9,5))
    ax.set_title(f"Bandwidth {title}{' (log scale)' if log else ''}")

    write = np.array(write)
    read = np.array(write)

    firstTime = datetime.strptime(first, "%Y-%m-%d %H:%M:%S")
    lastTime = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")

    firstUnix = time.mktime(firstTime.timetuple())
    lastUnix = time.mktime(lastTime.timetuple())
    spacer = (lastUnix-firstUnix)/len(write)

    timeAx = []

    for i in range(0,len(write)):
        timeAx.append(
            datetime.utcfromtimestamp(i*spacer+firstUnix).date()
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))


    ax.plot(timeAx,write, label="Write (upload ⬆️)", color="#68B030")
    ax.plot(timeAx, read, label="Read (download ⬇️)", color="blueviolet")

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"Bandwidth ({unit}/s)")
    ax.legend(loc="best")

    if log:
        ax.set_yscale('log')


    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)  # rewind the data
    plt.close(fig)
    return imgdata.getvalue()
    


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

matplotlib.rcParams['text.color'] = '#7D4698'
matplotlib.rcParams['axes.labelcolor'] = '#7D4698'
matplotlib.rcParams['xtick.color'] = '#7D4698'
matplotlib.rcParams['ytick.color'] = '#7D4698'

def plot(write, read, unit, first, last, title, log=False):
    fig, ax = plt.subplots(figsize=(9,5))
    ax.set_title(f"Bandwidth {title}{' (log scale)' if log else ''}")
    ax.tick_params(color='#7D4698', labelcolor='#59316B')
    for spine in ax.spines.values():
        spine.set_edgecolor('#59316B')


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
    ax.plot(timeAx, read, label="Read (download ⬇️)", color="blueviolet", linestyle = 'dashed')

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"Bandwidth ({unit}/s)")
    ax.legend(loc="best")

    if log:
        ax.set_yscale('log')


    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data
    plt.close(fig)
    return imgdata.getvalue()
    


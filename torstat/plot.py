import time
from datetime import datetime
from io import StringIO

import matplotlib
import matplotlib.dates as mdates
import numpy as np
from matplotlib import pyplot as plt

matplotlib.use('svg')


matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1
matplotlib.rcParams['text.color'] = '#7D4698'
matplotlib.rcParams['axes.labelcolor'] = '#7D4698'
matplotlib.rcParams['xtick.color'] = '#7D4698'
matplotlib.rcParams['ytick.color'] = '#7D4698'


def plotBandwidth(return_dict, write, read, unit, first, last, title):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(f"Bandwidth {title}")
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

    for i in range(0, len(write)):
        timeAx.append(
            datetime.utcfromtimestamp(i*spacer+firstUnix).date()
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    ax.plot(timeAx, write, label="Write (upload ⬆️)", color="#68B030")
    ax.plot(timeAx, read, label="Read (download ⬇️)",
            color="blueviolet", linestyle='dashed')

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"Bandwidth ({unit}/s)")
    ax.legend(loc="best")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"plotData_{title}"] = imgdata.getvalue()

    ax.set_yscale('log')
    ax.set_title(f"Bandwidth {title} (logarithmic scale)")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"plotDataLog_{title}"] = imgdata.getvalue()

    plt.close(fig)


def plotWeights(return_dict, consensus_weight_fraction, guard_probability, middle_probability, exit_probability, first, last, title):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(f"Weights {title}")
    ax.tick_params(color='#7D4698', labelcolor='#59316B')
    for spine in ax.spines.values():
        spine.set_edgecolor('#59316B')

    firstTime = datetime.strptime(first, "%Y-%m-%d %H:%M:%S")
    lastTime = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")

    firstUnix = time.mktime(firstTime.timetuple())
    lastUnix = time.mktime(lastTime.timetuple())
    spacer = (lastUnix-firstUnix)/len(consensus_weight_fraction)

    timeAx = []

    for i in range(0, len(consensus_weight_fraction)):
        timeAx.append(
            datetime.utcfromtimestamp(i*spacer+firstUnix).date()
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    ax.plot(timeAx, consensus_weight_fraction,
            label="consensus_weight_fraction", color="#8231d3")
    ax.plot(timeAx, guard_probability,
            label="guard_probability", color="#68B030")
    ax.plot(timeAx, middle_probability,
            label="middle_probability", color="#4034f4")
    ax.plot(timeAx, exit_probability, label="exit_probability", color="#f5a423")

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"%")
    ax.legend(loc="best")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"plotWeight_{title}"] = imgdata.getvalue()

    ax.set_yscale('log')
    ax.set_title(f"Weights {title} (logarithmic scale)")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data
    plt.close(fig)
    return_dict[f"plotWeightLog_{title}"] = imgdata.getvalue()


def plotClients(return_dict, clients, first, last, title):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(f"Clients {title}")
    ax.tick_params(color='#7D4698', labelcolor='#59316B')
    for spine in ax.spines.values():
        spine.set_edgecolor('#59316B')

    clients = np.array(clients)

    firstTime = datetime.strptime(first, "%Y-%m-%d %H:%M:%S")
    lastTime = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")

    firstUnix = time.mktime(firstTime.timetuple())
    lastUnix = time.mktime(lastTime.timetuple())
    spacer = (lastUnix-firstUnix)/len(clients)

    timeAx = []

    for i in range(0, len(clients)):
        timeAx.append(
            datetime.utcfromtimestamp(i*spacer+firstUnix).date()
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    ax.plot(timeAx, clients, label="Clients", color="#68B030")

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"Average clients")
    ax.legend(loc="best")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"clientData_{title}"] = imgdata.getvalue()
    ax.set_title(f"Clients {title} (logarithmic scale)")
    ax.set_yscale('log')
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"clientDataLog_{title}"] = imgdata.getvalue()

    plt.close(fig)


def plotUptime(return_dict, uptime, exit_, fast, guard, hsdir, running, stable, stabledesc, v2dir, valid, first, last, title):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_title(f"Uptime {title}")
    ax.tick_params(color='#7D4698', labelcolor='#59316B')
    for spine in ax.spines.values():
        spine.set_edgecolor('#59316B')

    uptime = np.array(uptime)

    firstTime = datetime.strptime(first, "%Y-%m-%d %H:%M:%S")
    lastTime = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")

    firstUnix = time.mktime(firstTime.timetuple())
    lastUnix = time.mktime(lastTime.timetuple())

    shortest = len(uptime)
    for i in [uptime, exit_, fast, guard, hsdir, running, stable, stabledesc, v2dir, valid]:
        if type(i) in (list, tuple):
            shortest = min(len(i), shortest)

    spacer = (lastUnix-firstUnix)/shortest

    timeAx = []

    for i in range(0, shortest):
        timeAx.append(
            datetime.utcfromtimestamp(i*spacer+firstUnix).date()
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    opacity = 0.7
    width = 3

    ht = {
        "Exit": exit_,
        "Fast":fast,
        "Guard":guard,
        "HSDir":hsdir,
        "Running":running,
        "Stable":stable,
        "StableDesc":stabledesc,
        "V2Dir": v2dir,
        "Valid":valid
    }
    colors = {
        "Exit": "#2a9d8f",
        "Fast":"#f7a8b8",
        "Guard":"#a3306f",
        "HSDir":"#c1b225",
        "Running":"#990b52",
        "Stable":"#0000ff",
        "StableDesc":"#429bfa",
        "V2Dir": "#ff7b00",
        "Valid":"#429bfa"
    }

    ax.plot(timeAx, uptime[:shortest], label="System uptime",
                    color="#110015", alpha=opacity, linewidth=width)

    for i in ht:
        if type(ht[i]) in (list, tuple):
            ax.plot(timeAx, ht[i][:shortest], label=i, color=colors[i], alpha=opacity)

    fig.autofmt_xdate()
    ax.grid()

    ax.set_ylabel(f"%")
    ax.legend(loc="best")

    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"uptimeData_{title}"] = imgdata.getvalue()
    ax.set_title(f"Clients {title} (logarithmic scale)")
    ax.set_yscale('log')
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg', transparent=True)
    imgdata.seek(0)  # rewind the data

    return_dict[f"uptimeDataLog_{title}"] = imgdata.getvalue()

    plt.close(fig)

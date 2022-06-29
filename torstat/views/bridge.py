import multiprocessing
from datetime import datetime, timezone

import arrow
import pycountry
from django.core.cache import cache
from django.shortcuts import  render

from ..common import convert_size
from ..plot import plotBandwidth, plotClients


def bridgeHandler(request, name, details, bandwidth, clients):
    ctx = {
        "type_raw": "bridge",
        "name": details["bridges"][0]["nickname"],
        "fingerprint": details["bridges"][0]["hashed_fingerprint"],
        "type": f"{', '.join(details['bridges'][0]['transports'])} bridge",
        "dataTypes": ["summary", "details", "uptime", "weights", "history"],
        "flags": details["bridges"][0].get("flags"),
        "flags_l": [i.lower() for i in details["bridges"][0].get("flags")],
        "first_seen": details["bridges"][0].get("first_seen"),
        "last_seen": details["bridges"][0].get("last_seen"),
        "last_restarted": details["bridges"][0].get("last_restarted"),
        "blocklist": [(i, pycountry.countries.get(alpha_2=i).name) for i in details["bridges"][0].get("blocklist")],
        "last_seen_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["bridges"][0].get("last_seen")
        ),
        "first_seen_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["bridges"][0].get("first_seen")
        ),
        "last_restarted_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["bridges"][0].get("last_restarted")
        ),
        "running": details["bridges"][0].get("running"),
        "transports": details["bridges"][0].get("transports"),
        "or_addresses": details["bridges"][0]["or_addresses"],
        "version_status": details["bridges"][0]["version_status"],
        "platform": details["bridges"][0]["platform"],
        "advertised_bandwidth": convert_size(details["bridges"][0]["advertised_bandwidth"]),
        "contact": details["bridges"][0]["contact"],
        "bridgedb_distributor": details["bridges"][0]["bridgedb_distributor"],
        "bandwidthAdvertisedNice": convert_size(details["bridges"][0]["advertised_bandwidth"])
    }

    print("=== RENDERING START ===")

    found = False
    for j in ["plotData_", "plotDataLog_", "clientData_", "clientDataLog_"]:
        for i in ["1_month", "6_months", "1_year", "5_years"]:
            check = f"{ctx['fingerprint']}|{j}{i}"
            x = cache.get(check)
            if x != None:
                ctx[f"{j}{i}"] = x
                found = True

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []

    if not found:
        for i in ["1_month", "6_months", "1_year", "5_years"]:
            if i not in bandwidth["bridges"][0]["read_history"]:
                break

            ctx["writes"] = bandwidth["bridges"][0]["write_history"][i]["values"]
            ctx["reads"] = bandwidth["bridges"][0]["read_history"][i]["values"]
            ctx["clients"] = clients["bridges"][0]["average_clients"][i]["values"]

            ctx["writes"] = [x for x in ctx["writes"] if x is not None]
            ctx["reads"] = [x for x in ctx["reads"] if x is not None]
            ctx["clients"] = [x for x in ctx["clients"] if x is not None]

            ctx["write_factor"] = bandwidth["bridges"][0]["write_history"][i]["factor"]
            ctx["read_factor"] = bandwidth["bridges"][0]["read_history"][i]["factor"]
            ctx["client_factor"] = clients["bridges"][0]["average_clients"][i]["factor"]

            ctx["writesNice"] = [convert_size(
                i*ctx["write_factor"], True) for i in ctx["writes"]]
            ctx["readsNice"] = [convert_size(
                i*ctx["read_factor"], True) for i in ctx["reads"]]
            ctx["clientsNice"] = [convert_size(
                i*ctx["client_factor"], True) for i in ctx["clients"]]

            p = multiprocessing.Process(target=plotBandwidth, args=(
                return_dict,
                ctx["writesNice"],
                ctx["readsNice"],
                convert_size(ctx["read_factor"]*ctx["reads"]
                             [-1], forceUnit=True),
                bandwidth["bridges"][0]["read_history"][i]["first"],
                bandwidth["bridges"][0]["read_history"][i]["last"],
                i
            ))
            jobs.append(p)
            p.start()

            p = multiprocessing.Process(target=plotClients, args=(
                return_dict,
                ctx["clientsNice"],
                clients["bridges"][0]["average_clients"][i]["first"],
                clients["bridges"][0]["average_clients"][i]["last"],
                i
            ))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        for i in return_dict:
            print(f"{ctx['fingerprint']}|{i}")
            cache.set(f"{ctx['fingerprint']}|{i}", return_dict[i], timeout=600)
            ctx[i] = return_dict[i]

    print("=== RENDERING END ===")
    if found:
        print("=== USED CACHE ===")
    else:
        print("=== DIDNT USE CACHE === ")

    return render(request, "../templates/relay.html", context=ctx)

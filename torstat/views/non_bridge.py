import multiprocessing
from datetime import datetime, timezone

import arrow
from django.core.cache import cache
from django.shortcuts import render

from ..common import convert_size
from ..plot import plotBandwidth, plotWeights


def relayHandler(request, name, details, bandwidth, weights):
    ctx = {
        "dataTypes": ["summary", "details", "uptime", "weights", "history"],
        "type_raw": "relay",
        "name": details["relays"][0]["nickname"],
        "platform": details["relays"][0]["platform"],
        "version_status": details["relays"][0]["version_status"],
        "measured": details["relays"][0]["measured"],
        "fingerprint": details["relays"][0]["fingerprint"],
        "or_addresses": details["relays"][0]["or_addresses"],
        "contact": details["relays"][0]["contact"],
        "dir_address": details["relays"][0].get("dir_address"),
        "exit_addresses": details["relays"][0].get("exit_addresses"),
        "flags": details["relays"][0].get("flags"),
        "flags_l": [i.lower() for i in details["relays"][0].get("flags")],
        "effective_family": details["relays"][0].get("effective_family"),
        "alleged_family": details["relays"][0].get("alleged_family"),
        "indirect_family": details["relays"][0].get("indirect_family"),
        "exit_policy_summary_accept": details["relays"][0].get("exit_policy_summary").get("accept"),
        "exit_policy_summary_reject": details["relays"][0].get("exit_policy_summary").get("reject"),
        "country": details["relays"][0].get("country"),
        "consensus_weight": details["relays"][0].get("consensus_weight"),
        "consensus_weight_fraction": details["relays"][0].get("consensus_weight_fraction")*100,
        "guard_probability": details["relays"][0].get("guard_probability")*100,
        "middle_probability": details["relays"][0].get("middle_probability")*100,
        "exit_probability": details["relays"][0].get("exit_probability")*100,
        "country_name": details["relays"][0].get("country_name"),
        "running": details["relays"][0].get("running"),
        "as_name": details["relays"][0].get("as_name"),
        "as_number": details["relays"][0].get("as"),
        "last_seen": details["relays"][0].get("last_seen"),
        "last_changed_address_or_port": details["relays"][0].get("last_changed_address_or_port"),
        "first_seen": details["relays"][0].get("first_seen"),
        "last_restarted": details["relays"][0].get("last_restarted"),
        "last_seen_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["relays"][0].get("last_seen")
        ),
        "last_changed_address_or_port_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["relays"][0].get("last_changed_address_or_port")
        ),
        "first_seen_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["relays"][0].get("first_seen")
        ),
        "last_restarted_ago": arrow.get(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))-arrow.get(
            details["relays"][0].get("last_restarted")
        ),
    }

    print("=== RENDERING START ===")

    found = False
    for j in ["plotData_", "plotDataLog_", "plotWeight_", "plotWeightLog_"]:
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
            if i not in bandwidth["relays"][0]["read_history"]:
                break

            ctx["writes"] = bandwidth["relays"][0]["write_history"][i]["values"]
            ctx["reads"] = bandwidth["relays"][0]["read_history"][i]["values"]

            ctx["writes"] = [x for x in ctx["writes"] if x is not None]
            ctx["reads"] = [x for x in ctx["reads"] if x is not None]

            ctx["write_factor"] = bandwidth["relays"][0]["write_history"][i]["factor"]
            ctx["read_factor"] = bandwidth["relays"][0]["read_history"][i]["factor"]

            ctx["writesNice"] = [convert_size(
                i*ctx["write_factor"], True) for i in ctx["writes"]]
            ctx["readsNice"] = [convert_size(
                i*ctx["read_factor"], True) for i in ctx["reads"]]

            ctx["consensus_weight_fraction_"] = [x for x in weights["relays"]
                                                 [0]["consensus_weight_fraction"][i]["values"] if x is not None]
            ctx["guard_probability_"] = [x for x in weights["relays"]
                                         [0]["guard_probability"][i]["values"] if x is not None]
            ctx["middle_probability_"] = [x for x in weights["relays"]
                                          [0]["middle_probability"][i]["values"] if x is not None]
            ctx["exit_probability_"] = [x for x in weights["relays"]
                                        [0]["exit_probability"][i]["values"] if x is not None]

            ctx["consensus_weight_fraction_"] = [x*weights["relays"][0]
                                                 ["consensus_weight_fraction"][i]["factor"] for x in ctx["consensus_weight_fraction_"]]
            ctx["guard_probability_"] = [x*weights["relays"][0]
                                         ["guard_probability"][i]["factor"] for x in ctx["guard_probability_"]]
            ctx["middle_probability_"] = [x*weights["relays"][0]
                                          ["middle_probability"][i]["factor"] for x in ctx["middle_probability_"]]
            ctx["exit_probability_"] = [x*weights["relays"][0]
                                        ["exit_probability"][i]["factor"] for x in ctx["exit_probability_"]]

            p = multiprocessing.Process(target=plotBandwidth, args=(
                return_dict,
                ctx["writesNice"],
                ctx["readsNice"],
                convert_size(ctx["read_factor"]*ctx["reads"]
                             [-1], forceUnit=True),
                bandwidth["relays"][0]["read_history"][i]["first"],
                bandwidth["relays"][0]["read_history"][i]["last"],
                i
            ))
            jobs.append(p)
            p.start()

            p = multiprocessing.Process(target=plotWeights, args=(
                return_dict,
                ctx["consensus_weight_fraction_"],
                ctx["guard_probability_"],
                ctx["middle_probability_"],
                ctx["exit_probability_"],
                weights["relays"][0]["consensus_weight_fraction"][i]["first"],
                weights["relays"][0]["consensus_weight_fraction"][i]["last"],
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
    ctx["writeTotal"] = 0
    ctx["readTotal"] = 0

    ctx["writes"] = bandwidth["relays"][0]["write_history"]["1_month"]["values"]
    ctx["reads"] = bandwidth["relays"][0]["read_history"]["1_month"]["values"]

    ctx["write_factor"] = bandwidth["relays"][0]["write_history"]["1_month"]["factor"]
    ctx["read_factor"] = bandwidth["relays"][0]["read_history"]["1_month"]["factor"]

    for i in ctx["writes"]:
        ctx["writeTotal"] += i*ctx["write_factor"] * \
            bandwidth["relays"][0]["write_history"]["1_month"]["interval"]

    for i in ctx["reads"]:
        ctx["readTotal"] += i*ctx["read_factor"] * \
            bandwidth["relays"][0]["read_history"]["1_month"]["interval"]

    ctx["writePerSecond"] = ctx["writes"][-1]*ctx["write_factor"]
    ctx["readPerSecond"] = ctx["reads"][-1]*ctx["read_factor"]

    ctx["writePerSecondNice"] = convert_size(
        ctx["writes"][-1]*ctx["write_factor"])
    ctx["readPerSecondNice"] = convert_size(
        ctx["reads"][-1]*ctx["read_factor"])

    ctx["bandwithRateNice"] = convert_size(
        details["relays"][0]["bandwidth_rate"])
    ctx["bandwidthBurstNice"] = convert_size(
        details["relays"][0]["bandwidth_burst"])

    ctx["bandwidthObservedNice"] = convert_size(
        details["relays"][0]["observed_bandwidth"])
    ctx["bandwidthAdvertisedNice"] = convert_size(
        details["relays"][0]["advertised_bandwidth"])

    return render(request, "../templates/relay.html", context=ctx)

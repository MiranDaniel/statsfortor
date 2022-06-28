from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
import requests
from django import forms
from django.http import HttpResponseNotFound
from .forms import Search
from binascii import a2b_hex
from hashlib import sha1
import socket
import math
from .plot import plot
from datetime import datetime, timezone
import arrow


def convert_size(B, forceFloat=False, forceUnit=False):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        if forceFloat:
            return B
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        if forceFloat:
            return B/KB
        if forceUnit:
            return "KB"
        return '{0:.2f} KB'.format(B / KB)
    elif MB <= B < GB:
        if forceFloat:
            return B/MB
        if forceUnit:
            return "MB"
        return '{0:.2f} MB'.format(B / MB)
    elif GB <= B < TB:
        if forceFloat:
            return B/GB
        if forceUnit:
            return "GB"
        return '{0:.2f} GB'.format(B / GB)
    elif TB <= B:
        if forceFloat:
            return B/TB
        if forceUnit:
            return "TB"
        return '{0:.2f} TB'.format(B / TB)


def index(request, name=""):
    ctx = {
        "index": True
    }
    return render(request, "../templates/index.html", context=ctx)

def donate(request, name=""):
    ctx = {
        "index": True,
        "donate": True
    }
    return render(request, "../templates/donate.html", context=ctx)


def relayRaw(request, name=""):
    form = Search(request.POST)

    if form.is_valid():
        return redirect(f"/relay/{form.data['relay']}")
    else:
        return redirect(f"/")


def relay(request, name=""):
    print("CALL")

    def bridgeHandler(name, details):
        ctx = {
            "type_raw": "bridge",
            "name": details["bridges"][0]["nickname"],
            "fingerprint": details["bridges"][0]["hashed_fingerprint"],
            "type": f"{', '.join(details['bridges'][0]['transports'])} bridge",
            "dataTypes": ["summary","details","uptime","weights","history"]
        }
        return render(request, "../templates/relay.html", context=ctx)

    def relayHandler(name, details, bandwidth):
        ctx = {
            "dataTypes": ["summary","details","uptime","weights","history"],
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

        ctx["type"] = "Middle"
        if "Exit" in details["relays"][0]["flags"]:
            ctx["type"] = "Exit"
        else:
            if "Guard" in details["relays"][0]["or_addresses"]:
                ctx["type"] = "Guard/Middle"
            else:
                ctx["type"] = "Middle"

        if "Authority" in details["relays"][0]["flags"]:
            ctx["type"] = "Authority"

        ctx["write_count"] = bandwidth["relays"][0]["write_history"]["6_months"]["count"]
        ctx["read_count"] = bandwidth["relays"][0]["read_history"]["6_months"]["count"]

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

            ctx[f"plotData_{i}"] = plot(
                ctx["writesNice"],
                ctx["readsNice"],
                convert_size(ctx["read_factor"]*ctx["reads"]
                             [-1], forceUnit=True),
                bandwidth["relays"][0]["read_history"][i]["first"],
                bandwidth["relays"][0]["read_history"][i]["last"],
                i
            )

            ctx[f"plotDataLog_{i}"] = plot(
                ctx["writesNice"],
                ctx["readsNice"],
                convert_size(ctx["read_factor"]*ctx["reads"]
                             [-1], forceUnit=True),
                bandwidth["relays"][0]["read_history"][i]["first"],
                bandwidth["relays"][0]["read_history"][i]["last"],
                i,
                True
            )

        ctx["writeTotal"] = 0
        ctx["readTotal"] = 0

        for i in ctx["writes"]:
            ctx["writeTotal"] += i*ctx["write_factor"] * \
                bandwidth["relays"][0]["write_history"]["6_months"]["interval"]

        for i in ctx["reads"]:
            ctx["readTotal"] += i*ctx["read_factor"] * \
                bandwidth["relays"][0]["read_history"]["6_months"]["interval"]

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

    prefix = ""
    if "." in name:
        try:
            socket.inet_aton(name)
        except socket.error:
            prefix = "host_name:"

    def _getDetails(name):
        print("DETAILS")
        r = requests.get(
            f"https://onionoo.torproject.org/details?search={prefix}{name}")
        print(f"{r.status_code=}")
        return r.json()

    def _getBandwidth(name):
        r = requests.get(
            f"https://onionoo.torproject.org/bandwidth?search={prefix}{name}")
        print(f"{r.status_code=}")
        return r.json()

    details = _getDetails(name)

    def check(details):
        if len(details["relays"]) == 0 and len(details["bridges"]) == 0:
            return error404(request, relay=name), False

        if len(details["relays"]) != 0:
            bandwidth = _getBandwidth(name)
            return relayHandler(name, details, bandwidth), True
        if len(details["bridges"]) != 0:
            return bridgeHandler(name, details), True

    res = check(details)
    if res[-1] != True:
        try:
            name = sha1(a2b_hex(name)).hexdigest().upper()
        except Exception:
            return error404(request, relay=name)
        return redirect(f"/relay/{name}")
    return res[0]


def error404(request, e=None, relay=None):
    if not relay:
        ctx = {"code": 404, "msg": "Not found :(", "relay": relay}
    else:
        ctx = {"code": 404, "msg": "Relay not found :(", "relay": relay}
    resp = render(None, "../templates/error.html", context=ctx)
    resp.status_code = 404
    return resp


def error500(request, e=None):
    ctx = {"code": 500, "msg": "Internal server error ;-;"}
    resp = render(None, "../templates/error.html", context=ctx
                  )
    resp.status_code = 500
    return resp


def error403(request, e=None):
    ctx = {"code": 403, "msg": "Forbidden. >:("}
    resp = render(None, "../templates/error.html", context=ctx
                  )
    resp.status_code = 403
    return resp


def error400(request, e=None):
    ctx = {"code": 400, "msg": "Bad request. How did you even do this?"}
    resp = render(None, "../templates/error.html", context=ctx
                  )
    resp.status_code = 400
    return resp

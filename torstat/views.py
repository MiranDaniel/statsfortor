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


def index(request, name=""):
    ctx = {
        "index": True
    }
    return render(request, "../templates/index.html", context=ctx)


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
            "type": f"{', '.join(details['bridges'][0]['transports'])} bridge"
        }
        return render(request, "../templates/relay.html", context=ctx)

    def relayHandler(name, details, bandwidth):
        ctx = {
            "type_raw": "relay",
            "name": details["relays"][0]["nickname"],
            "fingerprint": details["relays"][0]["fingerprint"],
            "or_addresses": details["relays"][0]["or_addresses"]
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

        ctx["writes"] = bandwidth["relays"][0]["write_history"]["6_months"]["values"]
        ctx["reads"] = bandwidth["relays"][0]["read_history"]["6_months"]["values"]

        ctx["write_factor"] = bandwidth["relays"][0]["write_history"]["6_months"]["factor"]
        ctx["read_factor"] = bandwidth["relays"][0]["read_history"]["6_months"]["factor"]

        ctx["write_count"] = bandwidth["relays"][0]["write_history"]["6_months"]["count"]
        ctx["read_count"] = bandwidth["relays"][0]["read_history"]["6_months"]["count"]

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
        return r.json()

    def _getBandwidth(name):
        r = requests.get(
            f"https://onionoo.torproject.org/bandwidth?search={prefix}{name}")
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
        name = sha1(a2b_hex(name)).hexdigest().upper()
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

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
import requests
from django import forms
from django.http import HttpResponseNotFound
from .forms import Search


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
    # if len(name) != 40:
    #    return HttpResponse(status=404)

    ctx = {}

    def _getDetails(name):
        r = requests.get(
            f"https://onionoo.torproject.org/details?search={name}")
        return r.json()

    def _getBandwidth(name):
        r = requests.get(
            f"https://onionoo.torproject.org/bandwidth?search={name}")
        return r.json()

    details = _getDetails(name)
    bandwidth = _getBandwidth(name)

    if len(details["relays"]) == 0:
        return error404(request, relay=name)

    ctx["name"] = details["relays"][0]["nickname"]
    ctx["fingerprint"] = details["relays"][0]["fingerprint"]
    ctx["or_addresses"] = details["relays"][0]["or_addresses"]

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

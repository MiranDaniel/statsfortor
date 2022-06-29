import socket
from binascii import a2b_hex
from hashlib import sha1

import requests
from django.core.cache import cache
from django.shortcuts import redirect, render

from ..forms import Search
from .bridge import bridgeHandler
from .errors import error404
from .non_bridge import relayHandler


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
        return redirect(f"/search/{form.data['relay']}")
    else:
        return redirect(f"/")


def node(request, name=""):
    c = cache.get(name)
    if c != None:
        print("Using cache")
        return c

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

    def _getWeights(name):
        r = requests.get(
            f"https://onionoo.torproject.org/weights?search={prefix}{name}")
        print(f"{r.status_code=}")
        return r.json()

    def _getClients(name):
        r = requests.get(
            f"https://onionoo.torproject.org/clients?search={prefix}{name}")
        print(f"{r.status_code=}")
        return r.json()

    def _getUptime(name):
        r = requests.get(
            f"https://onionoo.torproject.org/uptime?search={prefix}{name}")
        print(f"{r.status_code=}")
        return r.json()

    details = _getDetails(name)

    def check(details):
        if len(details["relays"]) == 0 and len(details["bridges"]) == 0:
            return error404(request, relay=name), False

        if len(details["relays"]) != 0:
            bandwidth = _getBandwidth(name)
            weights = _getWeights(name)
            uptime = _getUptime(name)
            return relayHandler(request, name, details, bandwidth, weights, uptime), True
        if len(details["bridges"]) != 0:
            bandwidth = _getBandwidth(name)
            clients = _getClients(name)
            uptime = _getUptime(name)
            return bridgeHandler(request, name, details, bandwidth, clients, uptime), True

    res = check(details)
    if res[-1] != True:
        try:
            name = sha1(a2b_hex(name)).hexdigest().upper()
        except Exception:
            return error404(request, relay=name)
        return redirect(f"/bridge/{name}")

    cache.set(name, res[0], timeout=30)
    return res[0]

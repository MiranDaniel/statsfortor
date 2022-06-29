from django.shortcuts import render


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
    resp = render(None, "../templates/error.html", context=ctx)
    resp.status_code = 500
    return resp


def error403(request, e=None):
    ctx = {"code": 403, "msg": "Forbidden. >:("}
    resp = render(None, "../templates/error.html", context=ctx)
    resp.status_code = 403
    return resp


def error400(request, e=None):
    ctx = {"code": 400, "msg": "Bad request. How did you even do this?"}
    resp = render(None, "../templates/error.html", context=ctx)
    resp.status_code = 400
    return resp

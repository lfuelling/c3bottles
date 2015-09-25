import json

from flask import render_template, request

from c3bottles import c3bottles, db
from model import DropPoint


@c3bottles.route("/")
def index():
    return render_template("index.html")


@c3bottles.route("/faq")
def faq():
    return render_template("faq.html")


@c3bottles.route("/numbers")
def statistics():
    return "TODO: Show some nice statistics"


@c3bottles.route("/list")
def dp_list():
    all_dps = []
    all_locations = []
    for dp in db.session.query(DropPoint).order_by(DropPoint.number).all():
        loc = dp.get_current_location()
        all_dps.append({
            "number": dp.number,
            "location": loc,
            "reports_total": dp.get_total_report_count(),
            "reports_new": dp.get_new_report_count(),
            "priority": dp.get_priority(),
            "last_state": dp.get_last_state(),
            "crates": dp.get_current_crate_count(),
            "removed": True if dp.removed else False
        })
        if loc.description not in all_locations and not dp.removed:
            all_locations.append(loc.description)
    return render_template(
        "list.html",
        all_dps=sorted(all_dps, key=lambda k: k["priority"], reverse=True),
        all_locations=sorted(all_locations),
        all_dps_geojson=DropPoint.get_all_dps_as_geojson()
    )


@c3bottles.route("/map")
def dp_map():
    return render_template(
        "map.html",
        all_dps_geojson=DropPoint.get_all_dps_as_geojson()
    )


@c3bottles.route("/view/<int:dp_number>")
def dp_view(dp_number):
    return render_template(
        "view.html",
        dp=db.session.query(DropPoint).get(dp_number)
    )


@c3bottles.route("/view")
def dp_view_base():
    return dp_view(0)


@c3bottles.route("/report/<int:dp_number>")
@c3bottles.route("/<int:dp_number>")
def dp_report(dp_number):
    return "TODO: Report drop point " + str(dp_number)


@c3bottles.route("/visit/<int:dp_number>")
def dp_visit(dp_number):
    return "TODO: Visit drop point " + str(dp_number)


@c3bottles.route("/create", methods=("GET", "POST"))
@c3bottles.route("/create/<string:lat>/<string:lng>")
def create_dp(
        number=None, description=None, lat=None,
        lng=None, level=None, crates=None, errors=None,
        success=None, center_lat=None, center_lng=None
):

    if request.method == "POST":

        number=request.form.get("number")
        description=request.form.get("description")
        lat=request.form.get("lat")
        lng=request.form.get("lng")
        level=request.form.get("level")
        crates=request.form.get("crates")

        try:
            DropPoint(
                number=number, description=description, lat=lat,
                lng=lng, level=level, crates=crates
            )
        except ValueError as e:
            errors = e.message
        else:
            db.session.commit()
            if request.form.get("action") == "stay":
                center_lat = lat
                center_lng = lng
                number = None
                description = None
                lat = None
                lng = None
                level = None
                crates = None
                success = True
            else:
                return render_template("creation_finished.html")

    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (ValueError, TypeError):
        lat_f = None
        lng_f = None

    if errors is not None:
        error_list={v for d in errors for v in d.values()}
        error_fields={k for d in errors for k in d.keys()}
    else:
        error_list = {}
        error_fields = {}

    return render_template(
        "create_dp.html",
        all_dps_geojson=DropPoint.get_all_dps_as_geojson(),
        number=number,
        description=description,
        center_lat=center_lat,
        center_lng=center_lng,
        lat=lat_f,
        lng=lng_f,
        level=level,
        crates=crates,
        error_list=error_list,
        error_fields=error_fields,
        success=success
    )


@c3bottles.route("/api", methods=("POST", "GET"))
def api():
    import api
    return api.process()

# vim: set expandtab ts=4 sw=4:

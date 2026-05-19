import csv
from io import StringIO

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from . import db
from .forms import MeasurementForm, PlantForm, VehicleForm
from .models import Measurement, Plant, User, Vehicle

main_bp = Blueprint("main", __name__)


def admin_only():
    if current_user.role != "admin":
        abort(403)


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard" if current_user.is_authenticated else "auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    measurements = Measurement.query.filter_by(user_id=current_user.id).order_by(Measurement.day.desc()).limit(10).all()
    total_prod = db.session.query(func.coalesce(func.sum(Measurement.production_kwh), 0)).filter_by(user_id=current_user.id).scalar()
    total_cons = db.session.query(func.coalesce(func.sum(Measurement.consumption_kwh), 0)).filter_by(user_id=current_user.id).scalar()
    return render_template("dashboard.html", measurements=measurements, total_prod=total_prod, total_cons=total_cons)


@main_bp.route("/plants", methods=["GET", "POST"])
@login_required
def plants():
    form = PlantForm()
    if form.validate_on_submit():
        plant = Plant(user_id=current_user.id, name=form.name.data, plant_type=form.plant_type.data, installed_kw=form.installed_kw.data, install_date=form.install_date.data)
        db.session.add(plant)
        db.session.commit()
        flash("Impianto salvato.", "success")
        return redirect(url_for("main.plants"))
    plants_list = Plant.query.filter_by(user_id=current_user.id).all()
    return render_template("plants.html", form=form, plants=plants_list)


@main_bp.route("/vehicles", methods=["GET", "POST"])
@login_required
def vehicles():
    form = VehicleForm()
    if form.validate_on_submit():
        vehicle = Vehicle(user_id=current_user.id, model=form.model.data, battery_kwh=form.battery_kwh.data)
        db.session.add(vehicle)
        db.session.commit()
        flash("Veicolo salvato.", "success")
        return redirect(url_for("main.vehicles"))
    vehicles_list = Vehicle.query.filter_by(user_id=current_user.id).all()
    return render_template("vehicles.html", form=form, vehicles=vehicles_list)


@main_bp.route("/measurements", methods=["GET", "POST"])
@login_required
def measurements():
    form = MeasurementForm()
    if form.validate_on_submit():
        m = Measurement(user_id=current_user.id, day=form.day.data, production_kwh=form.production_kwh.data, consumption_kwh=form.consumption_kwh.data, km_travelled=form.km_travelled.data)
        db.session.add(m)
        db.session.commit()
        flash("Dato registrato.", "success")
        return redirect(url_for("main.measurements"))
    entries = Measurement.query.filter_by(user_id=current_user.id).order_by(Measurement.day.desc()).all()
    return render_template("measurements.html", form=form, entries=entries)


@main_bp.route("/admin")
@login_required
def admin():
    admin_only()
    users = User.query.count()
    plants = Plant.query.count()
    vehicles = Vehicle.query.count()
    rows = Measurement.query.count()
    return render_template("admin.html", users=users, plants=plants, vehicles=vehicles, rows=rows)


@main_bp.route("/admin/export.csv")
@login_required
def export_csv():
    admin_only()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["user", "date", "production_kwh", "consumption_kwh", "km_travelled"])
    for r in Measurement.query.order_by(Measurement.day.desc()).all():
        writer.writerow([r.user_id, r.day.isoformat(), r.production_kwh, r.consumption_kwh, r.km_travelled])
    return Response(buffer.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})


@main_bp.route("/promote/<int:user_id>")
@login_required
def promote(user_id):
    admin_only()
    user = User.query.get_or_404(user_id)
    user.role = "admin"
    db.session.commit()
    flash(f"{user.full_name} promosso ad admin.", "success")
    return redirect(url_for("main.admin"))

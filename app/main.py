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
    if not current_user.is_admin:
        abort(403)


def owned_or_404(model, obj_id):
    obj = db.session.get(model, obj_id)
    if obj is None or obj.user_id != current_user.id:
        abort(404)
    return obj


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    measurements = (
        Measurement.query.filter_by(user_id=current_user.id)
        .order_by(Measurement.day.desc())
        .limit(10)
        .all()
    )
    totals = (
        db.session.query(
            func.coalesce(func.sum(Measurement.production_kwh), 0),
            func.coalesce(func.sum(Measurement.consumption_kwh), 0),
            func.coalesce(func.sum(Measurement.km_travelled), 0),
        )
        .filter_by(user_id=current_user.id)
        .first()
    )
    return render_template("dashboard.html", measurements=measurements, total_prod=totals[0], total_cons=totals[1], total_km=totals[2])


@main_bp.route("/plants", methods=["GET", "POST"])
@login_required
def plants():
    form = PlantForm()
    if form.validate_on_submit():
        db.session.add(
            Plant(
                user_id=current_user.id,
                name=form.name.data.strip(),
                plant_type=form.plant_type.data,
                installed_kw=form.installed_kw.data,
                install_date=form.install_date.data,
            )
        )
        db.session.commit()
        flash("Impianto salvato.", "success")
        return redirect(url_for("main.plants"))

    plants_list = Plant.query.filter_by(user_id=current_user.id).order_by(Plant.install_date.desc()).all()
    return render_template("plants.html", form=form, plants=plants_list)


@main_bp.route("/plants/<int:plant_id>/delete", methods=["POST"])
@login_required
def delete_plant(plant_id):
    plant = owned_or_404(Plant, plant_id)
    db.session.delete(plant)
    db.session.commit()
    flash("Impianto eliminato.", "info")
    return redirect(url_for("main.plants"))


@main_bp.route("/vehicles", methods=["GET", "POST"])
@login_required
def vehicles():
    form = VehicleForm()
    if form.validate_on_submit():
        db.session.add(Vehicle(user_id=current_user.id, model=form.model.data.strip(), battery_kwh=form.battery_kwh.data))
        db.session.commit()
        flash("Veicolo salvato.", "success")
        return redirect(url_for("main.vehicles"))

    vehicles_list = Vehicle.query.filter_by(user_id=current_user.id).order_by(Vehicle.id.desc()).all()
    return render_template("vehicles.html", form=form, vehicles=vehicles_list)


@main_bp.route("/vehicles/<int:vehicle_id>/delete", methods=["POST"])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = owned_or_404(Vehicle, vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    flash("Veicolo eliminato.", "info")
    return redirect(url_for("main.vehicles"))


@main_bp.route("/measurements", methods=["GET", "POST"])
@login_required
def measurements():
    form = MeasurementForm()
    if form.validate_on_submit():
        existing = Measurement.query.filter_by(user_id=current_user.id, day=form.day.data).first()
        if existing:
            flash("Esiste già una misurazione per questa data.", "warning")
        else:
            db.session.add(
                Measurement(
                    user_id=current_user.id,
                    day=form.day.data,
                    production_kwh=form.production_kwh.data,
                    consumption_kwh=form.consumption_kwh.data,
                    km_travelled=form.km_travelled.data,
                )
            )
            db.session.commit()
            flash("Dato registrato.", "success")
            return redirect(url_for("main.measurements"))

    entries = Measurement.query.filter_by(user_id=current_user.id).order_by(Measurement.day.desc()).all()
    return render_template("measurements.html", form=form, entries=entries)


@main_bp.route("/measurements/<int:measurement_id>/delete", methods=["POST"])
@login_required
def delete_measurement(measurement_id):
    measurement = owned_or_404(Measurement, measurement_id)
    db.session.delete(measurement)
    db.session.commit()
    flash("Misurazione eliminata.", "info")
    return redirect(url_for("main.measurements"))


@main_bp.route("/admin")
@login_required
def admin():
    admin_only()
    users = User.query.count()
    plants = Plant.query.count()
    vehicles = Vehicle.query.count()
    rows = Measurement.query.count()
    latest_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template("admin.html", users=users, plants=plants, vehicles=vehicles, rows=rows, latest_users=latest_users)


@main_bp.route("/admin/promote/<int:user_id>", methods=["POST"])
@login_required
def promote(user_id):
    admin_only()
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    user.role = "admin"
    db.session.commit()
    flash(f"{user.full_name} promosso ad admin.", "success")
    return redirect(url_for("main.admin"))


@main_bp.route("/admin/export.csv")
@login_required
def export_csv():
    admin_only()
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["user_email", "date", "production_kwh", "consumption_kwh", "km_travelled"])
    rows = (
        db.session.query(User.email, Measurement.day, Measurement.production_kwh, Measurement.consumption_kwh, Measurement.km_travelled)
        .join(Measurement, Measurement.user_id == User.id)
        .order_by(Measurement.day.desc())
        .all()
    )
    for row in rows:
        writer.writerow([row[0], row[1].isoformat(), row[2], row[3], row[4]])

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=autosolari_report.csv"},
    )

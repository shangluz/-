from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Accident, Vehicle, Driver

accidents_bp = Blueprint("accidents", __name__)

@accidents_bp.route("/")
@login_required
def list_accidents():
    rows = Accident.query.order_by(Accident.id.asc()).all()
    return render_template("accidents.html", accidents=rows)

@accidents_bp.route("/create", methods=["GET","POST"])
@login_required
def create_accident():
    vehicles = Vehicle.query.all()
    drivers = Driver.query.all()
    if request.method == "POST":
        vid = request.form.get("vehicle_id")
        did = request.form.get("driver_id")
        atime = request.form.get("accident_time") or None
        location = request.form.get("location","").strip()
        reason = request.form.get("reason","").strip()
        handle = request.form.get("handle_method","").strip()
        cost = request.form.get("cost") or None
        try:
            cost_val = float(cost) if cost not in (None, "") else None
        except Exception:
            flash("处理金额必须为数字", "warning")
            return render_template("accident_form.html", vehicles=vehicles, drivers=drivers)
        other = request.form.get("other_plate","").strip()
        a = Accident(vehicle_id=vid or None, driver_id=did or None, accident_time=atime,
                     location=location, reason=reason, handle_method=handle, cost=cost_val, other_plate=other)
        db.session.add(a)
        db.session.commit()
        flash("事故上报成功", "success")
        return redirect(url_for("accidents.list_accidents"))
    return render_template("accident_form.html", vehicles=vehicles, drivers=drivers, accident=None)

@accidents_bp.route("/<int:aid>/edit", methods=["GET","POST"])
@login_required
def edit_accident(aid):
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能编辑事故", "warning")
        return redirect(url_for("accidents.list_accidents"))
    a = Accident.query.get_or_404(aid)
    vehicles = Vehicle.query.all()
    drivers = Driver.query.all()
    if request.method == "POST":
        a.vehicle_id = request.form.get("vehicle_id") or None
        a.driver_id = request.form.get("driver_id") or None
        a.accident_time = request.form.get("accident_time") or None
        a.location = request.form.get("location","").strip()
        a.reason = request.form.get("reason","").strip()
        a.handle_method = request.form.get("handle_method","").strip()
        try:
            a.cost = float(request.form.get("cost")) if request.form.get("cost") else None
        except Exception:
            flash("处理金额必须为数字", "warning")
            return render_template("accident_form.html", vehicles=vehicles, drivers=drivers, accident=a)
        a.other_plate = request.form.get("other_plate","").strip()
        db.session.commit()
        flash("事故记录已更新", "success")
        return redirect(url_for("accidents.list_accidents"))
    return render_template("accident_form.html", vehicles=vehicles, drivers=drivers, accident=a)

@accidents_bp.route("/<int:aid>/delete", methods=["POST"])
@login_required
def delete_accident(aid):
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能删除事故", "warning")
        return redirect(url_for("accidents.list_accidents"))
    a = Accident.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    flash("已删除事故记录", "info")
    return redirect(url_for("accidents.list_accidents"))
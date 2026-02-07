from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Vehicle

vehicles_bp = Blueprint("vehicles", __name__)

@vehicles_bp.route("/")
@login_required
def list_vehicles():
    rows = Vehicle.query.order_by(Vehicle.id.asc()).all()
    return render_template("vehicles.html", vehicles=rows)

@vehicles_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_vehicle():
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能新增车辆", "warning")
        return redirect(url_for("vehicles.list_vehicles"))
    if request.method == "POST":
        plate = request.form.get("plate_number","").strip()
        vtype = request.form.get("type","").strip()
        status = request.form.get("status","空闲")
        if not plate or not vtype:
            flash("车牌和类型不能为空", "warning")
            return render_template("vehicle_form.html")
        v = Vehicle(plate_number=plate, type=vtype, status=status)
        db.session.add(v)
        db.session.commit()
        flash("新增车辆成功", "success")
        return redirect(url_for("vehicles.list_vehicles"))
    return render_template("vehicle_form.html", vehicle=None)

@vehicles_bp.route("/<int:vid>/edit", methods=["GET", "POST"])
@login_required
def edit_vehicle(vid):
    v = Vehicle.query.get_or_404(vid)
    if request.method == "POST":
        v.plate_number = request.form.get("plate_number","").strip()
        v.type = request.form.get("type","").strip()
        v.status = request.form.get("status","空闲")
        db.session.commit()
        flash("更新成功", "success")
        return redirect(url_for("vehicles.list_vehicles"))
    return render_template("vehicle_form.html", vehicle=v)

@vehicles_bp.route("/<int:vid>/delete", methods=["POST"])
@login_required
def delete_vehicle(vid):
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能删除车辆", "warning")
        return redirect(url_for("vehicles.list_vehicles"))
    v = Vehicle.query.get_or_404(vid)
    db.session.delete(v)
    db.session.commit()
    flash("已删除车辆", "info")
    return redirect(url_for("vehicles.list_vehicles"))
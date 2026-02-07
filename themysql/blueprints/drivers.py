from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db, login_manager
from models import Driver

drivers_bp = Blueprint("drivers", __name__)

@drivers_bp.route("/")
@login_required
def list_drivers():
    rows = Driver.query.order_by(Driver.id.asc()).all()
    return render_template("drivers.html", drivers=rows)

@drivers_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_driver():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        phone = request.form.get("phone","").strip()
        if not name:
            flash("姓名不能为空", "warning")
            return render_template("driver_form.html")
        d = Driver(name=name, phone=phone)
        db.session.add(d)
        db.session.commit()
        flash("新增司机成功", "success")
        return redirect(url_for("drivers.list_drivers"))
    return render_template("driver_form.html", driver=None)

@drivers_bp.route("/<int:did>/edit", methods=["GET","POST"])
@login_required
def edit_driver(did):
    d = Driver.query.get_or_404(did)
    if request.method == "POST":
        d.name = request.form.get("name","").strip()
        d.phone = request.form.get("phone","").strip()
        db.session.commit()
        flash("更新成功", "success")
        return redirect(url_for("drivers.list_drivers"))
    return render_template("driver_form.html", driver=d)

@drivers_bp.route("/<int:did>/delete", methods=["POST"])
@login_required
def delete_driver(did):
    d = Driver.query.get_or_404(did)
    db.session.delete(d)
    db.session.commit()
    flash("已删除司机", "info")
    return redirect(url_for("drivers.list_drivers"))
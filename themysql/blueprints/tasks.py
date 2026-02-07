from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import TransportTask, Vehicle, Driver
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

def parse_int(s, default=None):
    if s is None:
        return default
    s = str(s).strip()
    if s == "" or s.lower() == "none":
        return default
    try:
        return int(s)
    except Exception:
        return None

def parse_float(s, default=None):
    if s is None:
        return default
    s = str(s).strip()
    if s == "" or s.lower() == "none":
        return default
    try:
        return float(s)
    except Exception:
        return "INVALID"

def parse_datetime(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() == "none":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return "INVALID"


@tasks_bp.route("/")
@login_required
def list_tasks():
    rows = TransportTask.query.order_by(TransportTask.id.asc()).all()
    return render_template("tasks.html", tasks=rows)


@tasks_bp.route("/create", methods=["GET","POST"])
@login_required
def create_task():
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能新增任务", "warning")
        return redirect(url_for("tasks.list_tasks"))

    vehicles = Vehicle.query.all()
    drivers = Driver.query.all()
    if request.method == "POST":
        client = request.form.get("client_name","").strip()
        vtype = request.form.get("need_vehicle_type","").strip()

        nc = parse_int(request.form.get("need_count",""), default=0)
        if nc is None:
            flash("数量必须为整数", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=None)

        pm = parse_float(request.form.get("plan_mileage",""), default=None)
        if pm == "INVALID":
            flash("计划里程必须为数字", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=None)

        pst = parse_datetime(request.form.get("plan_start_time"))
        if pst == "INVALID":
            flash("计划开始时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=None)
        pet = parse_datetime(request.form.get("plan_end_time"))
        if pet == "INVALID":
            flash("计划结束时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=None)

        vid = parse_int(request.form.get("vehicle_id"), default=None)
        did = parse_int(request.form.get("driver_id"), default=None)

        status = request.form.get("status", "待安排") or "待安排"

        task = TransportTask(
            client_name=client or None,
            need_vehicle_type=vtype or None,
            need_count=nc,
            plan_mileage=pm,
            plan_start_time=pst,
            plan_end_time=pet,
            vehicle_id=vid,
            driver_id=did,
            status=status
        )
        db.session.add(task)
        db.session.commit()
        flash("新增任务成功", "success")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=None)


@tasks_bp.route("/<int:tid>/edit", methods=["GET","POST"])
@login_required
def edit_task(tid):
    task = TransportTask.query.get_or_404(tid)
    vehicles = Vehicle.query.all()
    drivers = Driver.query.all()

    if request.method == "POST":
        task.client_name = request.form.get("client_name","").strip() or None
        task.need_vehicle_type = request.form.get("need_vehicle_type","").strip() or None

        nc = parse_int(request.form.get("need_count",""), default=0)
        if nc is None:
            flash("数量必须为整数", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.need_count = nc

        pm = parse_float(request.form.get("plan_mileage",""), default=None)
        if pm == "INVALID":
            flash("计划里程必须为数字", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.plan_mileage = pm

        pst = parse_datetime(request.form.get("plan_start_time"))
        if pst == "INVALID":
            flash("计划开始时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        pet = parse_datetime(request.form.get("plan_end_time"))
        if pet == "INVALID":
            flash("计划结束时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.plan_start_time = pst
        task.plan_end_time = pet

        vid = parse_int(request.form.get("vehicle_id"), default=None)
        did = parse_int(request.form.get("driver_id"), default=None)
        task.vehicle_id = vid
        task.driver_id = did

        rst = parse_datetime(request.form.get("real_start_time"))
        if rst == "INVALID":
            flash("实际开始时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        ret = parse_datetime(request.form.get("real_end_time"))
        if ret == "INVALID":
            flash("实际结束时间格式错误，使用 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.real_start_time = rst
        task.real_end_time = ret

        rm = parse_float(request.form.get("real_mileage",""), default=None)
        if rm == "INVALID":
            flash("实际里程必须为数字", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.real_mileage = rm

        fu = parse_float(request.form.get("fuel_used",""), default=None)
        if fu == "INVALID":
            flash("耗油量必须为数字", "warning")
            return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)
        task.fuel_used = fu

        task.status = request.form.get("status") or task.status

        db.session.commit()
        flash("任务已更新", "success")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("task_form.html", vehicles=vehicles, drivers=drivers, task=task)

@tasks_bp.route("/<int:tid>/delete", methods=["POST"])
@login_required
def delete_task(tid):
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机不能删除任务", "warning")
        return redirect(url_for("tasks.list_tasks"))
    t = TransportTask.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    flash("已删除任务", "info")
    return redirect(url_for("tasks.list_tasks"))
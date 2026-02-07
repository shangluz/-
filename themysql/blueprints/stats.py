from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import TransportTask, Accident, Vehicle, Driver
from sqlalchemy import func
import io, csv
from datetime import datetime

stats_bp = Blueprint("stats", __name__)

def parse_date(s):
    if not s:
        return None
    s = s.strip()
    if s == "":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

@stats_bp.route("/admin")
@login_required
def admin_home():
    return render_template("admin_home.html")

@stats_bp.route("/overview")
@login_required
def overview():
    if current_user.role and "司机" in current_user.role:
        flash("权限不足：司机无法查看统计页面", "warning")
        return redirect(url_for("stats.admin_home"))
    start = parse_date(request.args.get("start_date"))
    end = parse_date(request.args.get("end_date"))
    vehicle_id = request.args.get("vehicle_id")
    driver_id = request.args.get("driver_id")
    status = request.args.get("status")
    tasks_q = db.session.query(TransportTask)
    acc_q = db.session.query(Accident)

    if start:
        tasks_q = tasks_q.filter(func.coalesce(TransportTask.plan_start_time, TransportTask.real_start_time) >= start)
        acc_q = acc_q.filter(Accident.accident_time >= start)
    if end:
        tasks_q = tasks_q.filter(func.coalesce(TransportTask.plan_end_time, TransportTask.real_end_time) <= end)
        acc_q = acc_q.filter(Accident.accident_time <= end)
    if vehicle_id:
        try:
            vid = int(vehicle_id)
            tasks_q = tasks_q.filter(TransportTask.vehicle_id == vid)
            acc_q = acc_q.filter(Accident.vehicle_id == vid)
        except Exception:
            pass
    if driver_id:
        try:
            did = int(driver_id)
            tasks_q = tasks_q.filter(TransportTask.driver_id == did)
            acc_q = acc_q.filter(Accident.driver_id == did)
        except Exception:
            pass
    if status:
        tasks_q = tasks_q.filter(TransportTask.status == status)
    total_tasks = tasks_q.count()
    filtered_tasks = tasks_q.all()
    plan_mileage_sum = sum([float(t.plan_mileage) for t in filtered_tasks if t.plan_mileage is not None])
    real_mileage_sum = sum([float(t.real_mileage) for t in filtered_tasks if t.real_mileage is not None])
    fuel_used_sum = sum([float(t.fuel_used) for t in filtered_tasks if t.fuel_used is not None])
    by_status = db.session.query(TransportTask.status, func.count(TransportTask.id)).select_from(TransportTask)
    if start:
        by_status = by_status.filter(func.coalesce(TransportTask.plan_start_time, TransportTask.real_start_time) >= start)
    if end:
        by_status = by_status.filter(func.coalesce(TransportTask.plan_end_time, TransportTask.real_end_time) <= end)
    if vehicle_id:
        try:
            by_status = by_status.filter(TransportTask.vehicle_id == int(vehicle_id))
        except Exception:
            pass
    if driver_id:
        try:
            by_status = by_status.filter(TransportTask.driver_id == int(driver_id))
        except Exception:
            pass
    by_status = by_status.group_by(TransportTask.status).all()

    by_vehicle = db.session.query(Vehicle.plate_number, func.count(TransportTask.id)).join(TransportTask, TransportTask.vehicle_id == Vehicle.id, isouter=True)
    if start:
        by_vehicle = by_vehicle.filter(func.coalesce(TransportTask.plan_start_time, TransportTask.real_start_time) >= start)
    if end:
        by_vehicle = by_vehicle.filter(func.coalesce(TransportTask.plan_end_time, TransportTask.real_end_time) <= end)
    if driver_id:
        try:
            by_vehicle = by_vehicle.filter(TransportTask.driver_id == int(driver_id))
        except Exception:
            pass
    by_vehicle = by_vehicle.group_by(Vehicle.plate_number).all()

    by_driver = db.session.query(Driver.name, func.count(TransportTask.id)).join(TransportTask, TransportTask.driver_id == Driver.id, isouter=True)
    if start:
        by_driver = by_driver.filter(func.coalesce(TransportTask.plan_start_time, TransportTask.real_start_time) >= start)
    if end:
        by_driver = by_driver.filter(func.coalesce(TransportTask.plan_end_time, TransportTask.real_end_time) <= end)
    if vehicle_id:
        try:
            by_driver = by_driver.filter(TransportTask.vehicle_id == int(vehicle_id))
        except Exception:
            pass
    by_driver = by_driver.group_by(Driver.name).all()

    acc_filtered = acc_q.all()
    acc_count = len(acc_filtered)
    acc_cost = sum([float(a.cost) for a in acc_filtered if a.cost is not None])
    acc_by_vehicle = db.session.query(Vehicle.plate_number, func.count(Accident.id)).join(Accident, Accident.vehicle_id == Vehicle.id, isouter=True)
    if start:
        acc_by_vehicle = acc_by_vehicle.filter(Accident.accident_time >= start)
    if end:
        acc_by_vehicle = acc_by_vehicle.filter(Accident.accident_time <= end)
    acc_by_vehicle = acc_by_vehicle.group_by(Vehicle.plate_number).all()
    acc_by_driver = db.session.query(Driver.name, func.count(Accident.id)).join(Accident, Accident.driver_id == Driver.id, isouter=True)
    if start:
        acc_by_driver = acc_by_driver.filter(Accident.accident_time >= start)
    if end:
        acc_by_driver = acc_by_driver.filter(Accident.accident_time <= end)
    acc_by_driver = acc_by_driver.group_by(Driver.name).all()
    vehicles = Vehicle.query.order_by(Vehicle.id.asc()).all()
    drivers = Driver.query.order_by(Driver.id.asc()).all()

    export = request.args.get("export")
    if export == "tasks":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["ID","客户名称","需要车型","需要数量","计划里程","计划开始","计划结束","车牌","司机","实际开始","实际结束","实际里程","耗油","状态"])
        for t in filtered_tasks:
            writer.writerow([
                t.id, t.client_name, t.need_vehicle_type, t.need_count, t.plan_mileage,
                t.plan_start_time.strftime("%Y-%m-%d %H:%M:%S") if t.plan_start_time else "",
                t.plan_end_time.strftime("%Y-%m-%d %H:%M:%S") if t.plan_end_time else "",
                t.vehicle.plate_number if t.vehicle else "", t.driver.name if t.driver else "",
                t.real_start_time.strftime("%Y-%m-%d %H:%M:%S") if t.real_start_time else "",
                t.real_end_time.strftime("%Y-%m-%d %H:%M:%S") if t.real_end_time else "",
                t.real_mileage if t.real_mileage is not None else "",
                t.fuel_used if t.fuel_used is not None else "",
                t.status
            ])
        mem = io.BytesIO()
        mem.write(buf.getvalue().encode("utf-8-sig"))
        mem.seek(0)
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="tasks_filtered.csv")

    if export == "accidents":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["ID","车牌","司机","时间","地点","原因","处理方式","费用","对方车号"])
        for a in acc_filtered:
            writer.writerow([
                a.id,
                a.vehicle.plate_number if a.vehicle else "",
                a.driver.name if a.driver else "",
                a.accident_time.strftime("%Y-%m-%d %H:%M:%S") if a.accident_time else "",
                a.location, a.reason, a.handle_method,
                ('%.2f' % a.cost) if a.cost is not None else "",
                a.other_plate or ""
            ])
        mem = io.BytesIO()
        mem.write(buf.getvalue().encode("utf-8-sig"))
        mem.seek(0)
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="accidents_filtered.csv")

    return render_template(
        "stats.html",
        total_tasks=total_tasks,
        plan_mileage_sum=plan_mileage_sum,
        real_mileage_sum=real_mileage_sum,
        fuel_used_sum=fuel_used_sum,
        by_status=by_status,
        by_vehicle=by_vehicle,
        by_driver=by_driver,
        acc_count=acc_count,
        acc_cost=acc_cost,
        acc_by_vehicle=acc_by_vehicle,
        acc_by_driver=acc_by_driver,
        vehicles=vehicles,
        drivers=drivers,
        filters={"start": request.args.get("start_date",""), "end": request.args.get("end_date",""), "vehicle_id": vehicle_id or "", "driver_id": driver_id or "", "status": status or ""}
    )
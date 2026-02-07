from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/")
def index():
    if current_user and getattr(current_user, "is_authenticated", False):
        return redirect(url_for("stats.admin_home"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("请输入用户名和密码", "warning")
            return render_template("login.html")
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            flash("用户名或密码错误", "danger")
            return render_template("login.html")
        login_user(user)
        flash("登录成功", "success")
        return redirect(url_for("stats.admin_home"))
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        name = request.form.get("name","").strip()
        role = request.form.get("role","司机")
        if not username or not password:
            flash("用户名和密码不能为空", "warning")
            return render_template("register.html")
        if User.query.filter_by(username=username).first():
            flash("用户名已存在", "warning")
            return render_template("register.html")
        u = User(username=username, password=password, name=name, role=role)
        db.session.add(u)
        db.session.commit()
        flash("注册成功，请登录", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已登出", "info")
    return redirect(url_for("auth.login"))
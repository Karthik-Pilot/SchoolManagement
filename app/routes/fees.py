from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from decimal import Decimal

from app import db
from app.models import FeeStructure, FeePayment, Student, SchoolClass
from app.forms.fee import FeeStructureForm, FeePaymentForm
from app.utils.permissions import admin_required

fees_bp = Blueprint("fees", __name__, url_prefix="/fees")


@fees_bp.route("/")
@login_required
@admin_required
def index():
    structures = FeeStructure.query.order_by(FeeStructure.academic_year.desc(), FeeStructure.class_id).all()
    return render_template("fees/index.html", structures=structures)


@fees_bp.route("/structure/new", methods=["GET", "POST"])
@login_required
@admin_required
def structure_create():
    form = FeeStructureForm()
    form.class_id.choices = [(c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()]
    if form.validate_on_submit():
        s = FeeStructure(
            class_id=form.class_id.data,
            fee_type=form.fee_type.data,
            amount=form.amount.data,
            academic_year=form.academic_year.data,
            term=form.term.data or None,
        )
        db.session.add(s)
        db.session.commit()
        flash("Fee structure created.", "success")
        return redirect(url_for("fees.index"))
    return render_template("fees/structure_form.html", form=form, title="New Fee Structure")


@fees_bp.route("/structure/<int:struct_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def structure_edit(struct_id):
    s = FeeStructure.query.get_or_404(struct_id)
    form = FeeStructureForm(obj=s)
    form.class_id.choices = [(c.id, str(c)) for c in SchoolClass.query.order_by(SchoolClass.name).all()]
    if form.validate_on_submit():
        s.class_id = form.class_id.data
        s.fee_type = form.fee_type.data
        s.amount = form.amount.data
        s.academic_year = form.academic_year.data
        s.term = form.term.data or None
        db.session.commit()
        flash("Fee structure updated.", "success")
        return redirect(url_for("fees.index"))
    form.class_id.data = s.class_id
    return render_template("fees/structure_form.html", form=form, structure=s, title="Edit Fee Structure")


@fees_bp.route("/payments")
@login_required
@admin_required
def payment_list():
    class_id = request.args.get("class_id", type=int)
    student_id = request.args.get("student_id", type=int)
    q = FeePayment.query
    if student_id:
        q = q.filter_by(student_id=student_id)
    if class_id:
        q = q.join(FeePayment.fee_structure).filter(FeeStructure.class_id == class_id)
    payments = q.order_by(FeePayment.payment_date.desc()).limit(200).all()
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    return render_template("fees/payment_list.html", payments=payments, classes=classes, class_filter=class_id, student_filter=student_id)


@fees_bp.route("/payments/new", methods=["GET", "POST"])
@login_required
@admin_required
def payment_create():
    form = FeePaymentForm()
    form.student_id.choices = [(s.id, str(s)) for s in Student.query.order_by(Student.admission_no).all()]
    form.fee_structure_id.choices = [(f.id, f"{f.school_class.name} - {f.fee_type} - {f.amount} ({f.academic_year})") for f in FeeStructure.query.join(FeeStructure.school_class).order_by(SchoolClass.name, FeeStructure.fee_type).all()]
    if form.validate_on_submit():
        fs = FeeStructure.query.get(form.fee_structure_id.data)
        if not fs:
            flash("Invalid fee structure.", "error")
            return render_template("fees/payment_form.html", form=form, title="New Payment")
        amount = form.amount_paid.data
        if amount > fs.amount:
            flash(f"Amount paid ({amount}) exceeds structure amount ({fs.amount}). Overpayment not allowed.", "error")
            return render_template("fees/payment_form.html", form=form, title="New Payment")
        p = FeePayment(
            student_id=form.student_id.data,
            fee_structure_id=form.fee_structure_id.data,
            amount_paid=amount,
            payment_date=form.payment_date.data,
            receipt_no=form.receipt_no.data or None,
            payment_mode=form.payment_mode.data or None,
        )
        db.session.add(p)
        db.session.commit()
        flash("Payment recorded.", "success")
        return redirect(url_for("fees.payment_list"))
    return render_template("fees/payment_form.html", form=form, title="New Payment")

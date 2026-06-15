from flask import Blueprint, jsonify, Response, request
from flask_jwt_extended import jwt_required
from app.service.hr_service import (
    get_all_leaves_detailed,
    generate_leaves_csv_report,
    generate_leaves_pdf_report,
    generate_leaves_xls_report,
    get_all_balances,
    create_balance_for_user,
    update_balance_total,
)
from app.model.user import User
from app.model.leave_type import LeaveType
from app.utils.decorators import role_required

hr_bp = Blueprint('hr', __name__)


@hr_bp.route('/leaves', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def list_all_leaves():
    leaves = get_all_leaves_detailed()
    return jsonify(leaves), 200


@hr_bp.route('/reports/csv', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def export_leaves_csv():
    csv_data = generate_leaves_csv_report()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=raport_urlopowy.csv"}
    )


@hr_bp.route('/reports/pdf', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def export_leaves_pdf():
    pdf_data = generate_leaves_pdf_report()
    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=raport_urlopowy.pdf"}
    )


@hr_bp.route('/reports/xls', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def export_leaves_xls():
    xls_data = generate_leaves_xls_report()
    return Response(
        xls_data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=raport_urlopowy.xlsx"}
    )


@hr_bp.route('/balances', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def list_balances():
    return jsonify(get_all_balances()), 200


@hr_bp.route('/balances', methods=['POST'])
@jwt_required()
@role_required('HR', 'ADMIN')
def add_balance():
    data = request.get_json()
    try:
        balance = create_balance_for_user(
            user_id=data['user_id'],
            leave_type_id=data['leave_type_id'],
            year=data['year'],
            total_days=data['total_days'],
        )
        return jsonify({"msg": "Balance created", "id": balance.id}), 201
    except (ValueError, KeyError) as e:
        return jsonify({"msg": str(e)}), 400


@hr_bp.route('/balances/<int:balance_id>', methods=['PATCH'])
@jwt_required()
@role_required('HR', 'ADMIN')
def edit_balance(balance_id):
    data = request.get_json()
    try:
        balance = update_balance_total(balance_id, data['total_days'])
        return jsonify({
            "msg": "Balance updated",
            "id": balance.id,
            "total_days": balance.total_days,
        }), 200
    except (ValueError, KeyError) as e:
        return jsonify({"msg": str(e)}), 400


@hr_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def list_users():
    users = User.query.order_by(User.last_name).all()
    return jsonify([{
        "id": u.id,
        "name": f"{u.first_name} {u.last_name}",
        "email": u.email,
        "role": u.role.value,
    } for u in users]), 200


@hr_bp.route('/leave-types', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def list_leave_types():
    types = LeaveType.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in types]), 200

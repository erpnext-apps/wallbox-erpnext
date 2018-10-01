# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	"""return columns"""
	columns = [
		_("Customer")+":Link/Customer:120",
		_("Sales Order")+":Link/Sales Order:150",
		_("Sales Order Date")+":Date:100",
		_("Sales Order Submission Date")+":Datetime:100",
		_("Sales Order Status")+":Data:50",
		_("Item")+":Link/Item:100",
		_("Item Name")+"::150",
		_("Item Group")+":Link/Item Group:100",
		_("Status")+":Data:100",
		_("Qty")+":Int:50",
		_("Delivered")+":Int:50",
		_("Booked")+":Int:50",
		_("Expected Delivery")+":Date:100",
		_("Work Order Date")+":Date:100",
		_("Work Order Delivery Date")+":Date:100",
		_("Delivery Note Date")+":Date:100",
		_("Delivery Note Submission Date")+":Datetime:100",
		_("Delay")+":Int:50"
	]
	return columns


def get_conditions(filters):
	conditions = []
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))
	conditions.append("so.transaction_date>=%(from_date)s")
	if filters.get("to_date"):
		conditions.append("so.transaction_date<=%(to_date)s")
	else:
		frappe.throw(_("'To Date' is required"))
	if filters.get("customer"):
		conditions.append("so.customer=%(customer)s")
	if filters.get("item_group"):
		conditions.append("soi.item_group=%(item_group)s")
	if filters.get("item_code"):
		conditions.append("soi.item_code=%(item_code)s")
	return conditions


def get_data(filters):
	data=[]
	conditions = get_conditions(filters)

	so_details = frappe.db.sql("""select so.customer, so.name, so.transaction_date,
		soi.item_code, soi.item_name, soi.item_group, so.status, so.delivery_status, 
		so.wb_submission_date, soi.qty, soi.delivered_qty, soi.delivery_date, 
		wo.planned_start_date, wo.expected_delivery_date
		from `tabSales Order Item` soi join `tabSales Order` so on soi.parent=so.name
		left join `tabWork Order` wo on (soi.item_code=wo.production_item and
		so.name=wo.sales_order) where {}""".format(" and ".join(conditions)), filters, as_dict=1)
	if so_details:
		for item in so_details:
			report_data = []
			booked_qty = frappe.db.sql("""select count(*) from `tabSerial No` where
				delivery_date IS NULL and sales_order=%s and item_code=%s""",
				(item["name"], item["item_code"]))
			if booked_qty and booked_qty[0]:
				booked_qty = booked_qty[0][0]
			else:
				booked_qty = 0
			report_data = [item["customer"], item["name"], item["transaction_date"],
				item["wb_submission_date"], item["status"], item["item_code"], item["item_name"], 
				item["item_group"],	item["delivery_status"], item["qty"], item["delivered_qty"], booked_qty,
				item["delivery_date"], item["planned_start_date"], item["expected_delivery_date"]]
			dni = frappe.db.sql("""select dn.posting_date, dn.wb_submission_date from `tabDelivery Note Item`
				dni join `tabDelivery Note` dn on dni.parent=dn.name where
				dni.against_sales_order=%s and dni.item_code=%s order by
				dn.wb_submission_date desc limit 1""", (item["name"], item["item_code"]))
			if dni and dni[0]:
				report_data.append(dni[0][0])
				report_data.append(dni[0][1])
				report_data.append(date_diff(dni[0][0], item["expected_delivery_date"]))
			data.append(report_data)
	return data

import frappe
from frappe.utils import now

def update_submission(doc, method):
	doc.db_set("wb_submission_date", now())
	doc.db_set("wb_submitted_by", frappe.session.user)

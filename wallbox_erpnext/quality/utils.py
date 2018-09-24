import frappe
from frappe.utils import now, getdate, add_days

# TODO remove method update_submission and add a patch to 
# copy data from wb_submission_date, wb_submitted_by into 
# field added in frappe, remove custom fields

# Update the fields in manufacturing lead time report to 
# submission fields in frappe

# remove method call on_submit of SO, DN from hooks

def update_submission(doc, method):
	doc.db_set("wb_submission_date", now())
	doc.db_set("wb_submitted_by", frappe.session.user)

def update_delivery_by_lead_days(doc, method):
	if doc.wb_apply_lead_time:
		so_delivery_date = getdate()
		item_group = None
		group_lead_time = None
		group_qty = {}
		if doc.wb_lead_time_by_item_group:
			group_qty = get_qty_by_item_group(doc)

		def get_key(item):
			return item.qty

		for item in doc.items:
			if item.item_group != item_group:
				lead_time = frappe.db.exists("Wallbox Manufacturing Lead Time", 
					{"item_group": item.item_group, "enabled": 1})
				if lead_time:
					lead_time = frappe.get_doc("Wallbox Manufacturing Lead Time", lead_time)
					group_lead_time = lead_time
					group_lead_time.lead_days = sorted(group_lead_time.lead_days, key=get_key)
				else:
					group_lead_time = None
				item_group = item_group
			if group_lead_time:
				for lead in group_lead_time.lead_days:
					if doc.wb_lead_time_by_item_group:
						if lead.qty >= group_qty[item.item_group]:
							item.delivery_date = add_days(getdate(), lead.days)
							break
					else:
						if lead.qty >= item.qty:
							item.delivery_date = add_days(getdate(), lead.days)
							break
				if frappe.db.get_value("Item", item.item_code, "wb_is_not_standard"):
					if group_lead_time.lead_days_for_custom:
						item.delivery_date = add_days(item.delivery_date, 
							group_lead_time.lead_days_for_custom)
			if getdate(so_delivery_date) < getdate(item.delivery_date):
				so_delivery_date = item.delivery_date
		doc.delivery_date = so_delivery_date

def get_qty_by_item_group(doc):
	group_qty = {}
	for item in doc.items:
		if item.item_group in group_qty:
			group_qty[item.item_group] += item.qty
		else:
			group_qty[item.item_group] = item.qty
	return group_qty

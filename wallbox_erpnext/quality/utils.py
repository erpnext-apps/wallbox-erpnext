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
		group_delivery_date = {}
		holidays = []
		holiday_list = frappe.get_value("Company", doc.company, "default_holiday_list")
		if holiday_list:
			from_date, to_date =  frappe.get_value("Holiday List", holiday_list,
				["from_date", "to_date"])
			if so_delivery_date > getdate(from_date) and so_delivery_date < getdate(to_date):
				holidays = frappe.db.sql_list("""select holiday_date from tabHoliday
					where parent=%s""", (holiday_list))
		if doc.wb_lead_time_by_item_group:
			group_qty = get_qty_by_item_group(doc)

		def get_key(item):
			return item.qty

		for item in doc.items:
			# update group_lead_time if item group changed from that of last iteration
			if item.item_group != item_group:
				lead_time = frappe.db.exists("Wallbox Manufacturing Lead Time", 
					{"company":doc.company, "item_group": item.item_group, "enabled": 1})
				if lead_time:
					lead_time = frappe.get_doc("Wallbox Manufacturing Lead Time", lead_time)
					group_lead_time = lead_time
					group_lead_time.lead_days = sorted(group_lead_time.lead_days, key=get_key)
				else:
					group_lead_time = None
				item_group = item_group
			if group_lead_time:
				grp_qty=0
				if doc.wb_lead_time_by_item_group:
					grp_qty = group_qty[item.item_group]

				item.delivery_date = calc_lead_date(group_lead_time, item.qty, 
					holidays, True, grp_qty)

				# add lead time for non standard Items
				if frappe.db.get_value("Item", item.item_code, "wb_is_not_standard") and\
					group_lead_time.lead_days_for_custom:
					if holidays:
						item.delivery_date = get_working_lead_date(holidays, 
							item.delivery_date, group_lead_time.lead_days_for_custom)
					else:
						item.delivery_date = add_days(item.delivery_date, 
							group_lead_time.lead_days_for_custom)

					# if lead time by item group update all items in same 
					# item group with largest delivery date
					if doc.wb_lead_time_by_item_group:
						if item.item_group not in group_delivery_date:
							group_delivery_date[item.item_group] = item.delivery_date
						elif getdate(group_delivery_date[item.item_group]) < getdate(item.delivery_date):
							group_delivery_date[item.item_group] = item.delivery_date
			if getdate(so_delivery_date) < getdate(item.delivery_date):
				so_delivery_date = item.delivery_date
		doc.delivery_date = so_delivery_date

def calc_lead_date(lead_time, qty, holidays, by_group=False, grp_qty=0):
	for lead in lead_time.lead_days:
		if by_group:
			if lead.qty >= grp_qty:
				if holidays:
					return get_working_lead_date(holidays, getdate(), lead.days)
				else:
					return add_days(getdate(), lead.days)
		else:
			if lead.qty >= qty:
				if holidays:
					return get_working_lead_date(holidays, getdate(), lead.days)
				else:
					return add_days(getdate(), lead.days)

def get_qty_by_item_group(doc):
	group_qty = {}
	for item in doc.items:
		if item.item_group not in group_qty:
			group_qty[item.item_group] = item.qty
		elif group_qty[item.item_group] < item.qty:
			group_qty[item.item_group] = item.qty
	return group_qty

def get_working_lead_date(holidays, lead_date, lead_days):
	days_working = 0
	while days_working < lead_days:
		lead_date = add_days(lead_date, 1)
		if lead_date not in holidays:
			days_working += 1
	return lead_date
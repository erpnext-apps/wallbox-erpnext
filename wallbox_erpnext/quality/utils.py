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
		lead_time = None
		item_group_lt = {}
		holidays = []
		holiday_list = frappe.get_value("Company", doc.company, "default_holiday_list")
		# get list of holidays
		if holiday_list:
			from_date, to_date =  frappe.get_value("Holiday List", holiday_list,
				["from_date", "to_date"])
			if so_delivery_date > getdate(from_date) and so_delivery_date < getdate(to_date):
				holidays = frappe.db.sql_list("""select holiday_date from tabHoliday
					where parent=%s""", (holiday_list))
		# if lead time by group find the highest lead date
		if doc.wb_lead_time_by_item_group:
			item_group_lt = get_data_by_item_group(doc)
			for item_group in item_group_lt:
				lead_time = get_lead_time(doc.company, item_group)
				if lead_time:
					item_group_lt[item_group]["delivery_date"] = calc_lead_date(lead_time, 0,
						holidays, True, item_group_lt[item_group]["qty"])
					if "has_custom" in item_group_lt[item_group] and lead_time.lead_days_for_custom:
						item_group_lt[item_group]["delivery_date"] = get_working_lead_date(holidays, 
							item_group_lt[item_group]["delivery_date"], lead_time.lead_days_for_custom)
					# update delivery_date of SO if date greater
					if getdate(so_delivery_date) < getdate(item_group_lt[item_group]["delivery_date"]):
						so_delivery_date = item_group_lt[item_group]["delivery_date"]

		for item in doc.items:
			# if lead time by group apply the lt in item_group_lt
			if doc.wb_lead_time_by_item_group:
				if "delivery_date" in item_group_lt[item.item_group]:
					item.delivery_date = item_group_lt[item.item_group]["delivery_date"]
				continue
			# update lead_time if item group changed from that of last iteration
			if item.item_group != item_group:
				lead_time = get_lead_time(doc.company, item.item_group)
				item_group = item.item_group
			if lead_time:
				item.delivery_date = calc_lead_date(lead_time, item.qty, holidays)

				# add lead time for non standard Items
				if frappe.db.get_value("Item", item.item_code, "wb_is_not_standard") and\
					lead_time.lead_days_for_custom:
					if holidays:
						item.delivery_date = get_working_lead_date(holidays, 
							item.delivery_date, lead_time.lead_days_for_custom)
					else:
						item.delivery_date = add_days(item.delivery_date, 
							lead_time.lead_days_for_custom)

			# update delivery_date of SO if date greater
			if getdate(so_delivery_date) < getdate(item.delivery_date):
				so_delivery_date = item.delivery_date
		doc.delivery_date = so_delivery_date

def get_lead_time(company, item_group):
	lead_time = frappe.db.exists("Wallbox Manufacturing Lead Time",
		{"company":company, "item_group": item_group, "enabled": 1})

	def get_key(item):
		return item.qty

	if lead_time:
		lead_time = frappe.get_doc("Wallbox Manufacturing Lead Time", lead_time)
		lead_time.lead_days = sorted(lead_time.lead_days, key=get_key)
	return lead_time

def calc_lead_date(lead_time, qty, holidays, by_group=False, grp_qty=0):
	lead_date = None
	lead_days = 0
	for lead in lead_time.lead_days:
		lead_days = lead.days
		if by_group:
			if lead.qty >= grp_qty:
				lead_date = get_lead_days(holidays, lead.days)
				break
		else:
			if lead.qty >= qty:
				lead_date = get_lead_days(holidays, lead.days)
				break
	# if qty grater than the largest configured, lead date will be None
	# apply the days for largest configured qty
	if lead_date:
		return lead_date
	else:
		return get_lead_days(holidays, lead_days)

def get_lead_days(holidays, lead_days):
	if holidays:
		lead_date = get_working_lead_date(holidays, getdate(), lead_days)
	else:
		lead_date = add_days(getdate(), lead_days)
	return lead_date

def get_data_by_item_group(doc):
	item_group_lt = {}
	for item in doc.items:
		if item.item_group not in item_group_lt:
			item_group_lt[item.item_group] = {}
			item_group_lt[item.item_group]["qty"] = item.qty
		elif item_group_lt[item.item_group]["qty"] < item.qty:
			item_group_lt[item.item_group]["qty"] = item.qty
		if frappe.db.get_value("Item", item.item_code, "wb_is_not_standard"):
			item_group_lt[item.item_group]["has_custom"] = 1
	return item_group_lt

def get_working_lead_date(holidays, lead_date, lead_days):
	days_working = 0
	while days_working < lead_days:
		lead_date = add_days(lead_date, 1)
		if lead_date not in holidays:
			days_working += 1
	return lead_date
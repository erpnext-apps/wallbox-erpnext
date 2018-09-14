from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Stock Reports"),
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Serialized Stock Balance",
					"doctype": "Stock Ledger Entry"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Manufacturing Lead Time",
					"doctype": "Sales Order"
				}
			]
		}
	]

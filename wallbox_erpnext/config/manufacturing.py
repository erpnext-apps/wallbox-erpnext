from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Setup"),
			"items": [
				{
					"type": "doctype",
					"name": "Wallbox Manufacturing Lead Time",
					"doctype": "Wallbox Manufacturing Lead Time"
				}
			]
		}
	]
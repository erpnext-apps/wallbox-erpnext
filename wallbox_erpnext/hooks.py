# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "wallbox_erpnext"
app_title = "wallbox"
app_publisher = "Frappe"
app_description = "Wallbox erpnext app"
app_icon = "search"
app_color = "#5F9EA0"
app_email = "info@frappe.io"
app_license = "MIT"

#fixtures = [{"dt":"Custom Field", "filters": [["fieldname", "in", ("wb_submission_date", 
#	"wb_submitted_by", "wb_is_not_standard", "wb_apply_lead_time", "wb_lead_time_by_item_group")]]}]

doc_events = {
	"Sales Order": {
		"before_submit": "wallbox_erpnext.quality.utils.update_delivery_by_lead_days",
		"on_submit": "wallbox_erpnext.quality.utils.update_submission"
	},
	"Delivery Note": {
		"on_submit": "wallbox_erpnext.quality.utils.update_submission"
	}
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/wallbox_erpnext/css/wallbox_erpnext.css"
# app_include_js = "/assets/wallbox_erpnext/js/wallbox_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/wallbox_erpnext/css/wallbox_erpnext.css"
# web_include_js = "/assets/wallbox_erpnext/js/wallbox_erpnext.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "wallbox_erpnext.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "wallbox_erpnext.install.before_install"
# after_install = "wallbox_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "wallbox_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"wallbox_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"wallbox_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"wallbox_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"wallbox_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"wallbox_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "wallbox_erpnext.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "wallbox_erpnext.event.get_events"
# }


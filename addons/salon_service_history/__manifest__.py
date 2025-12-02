{
    "name": "Salon Service History",
    "version": "19.0.1.0.0",
    "summary": "Lịch sử giao dịch dịch vụ salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management", "salon_customer", "salon_employee"],
    "data": [
        "security/ir.model.access.csv",
        "views/service_history_views.xml",
        "views/service_history_menu.xml",
    ],
    "installable": True,
    "application": False,
}


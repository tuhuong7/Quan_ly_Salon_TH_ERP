{
    "name": "Salon Service Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý dịch vụ salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/service_sequence.xml",
        "views/salon_service_tree_view.xml",
        "views/salon_service_search_view.xml",
        "views/salon_service_form_view.xml",
        "views/salon_service_menu.xml",
    ],
    "installable": True,
    "application": False,
}

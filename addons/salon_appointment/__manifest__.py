{
    "name": "Salon Appointment Management",
    "version": "19.0.1.0.2",
    "summary": "Quản lý lịch hẹn Salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management", "salon_employee", "salon_customer", "salon_service"],
    "data": [
        "security/ir.model.access.csv",
        "data/appointment_sequence.xml",
        "views/salon_appointment_tree_view.xml",
        "views/salon_appointment_search_view.xml",
        "views/salon_appointment_kanban_view.xml",
        "views/salon_appointment_form_view.xml",
        "views/salon_appointment_menu.xml",
        "views/appointment_cancel_wizard_view.xml",
    ],
    "installable": True,
    "application": False,
}

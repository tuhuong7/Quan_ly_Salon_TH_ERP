{
    "name": "Salon Employee Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý nhân viên salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/employee_sequence.xml",
        "views/employee_views.xml",
        "views/employee_kanban_view.xml",
        "views/shift_views.xml",
    ],
    "installable": True,
    "application": False,
}


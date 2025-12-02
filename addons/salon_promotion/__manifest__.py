{
    "name": "Salon Promotion Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý khuyến mãi salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/promotion_sequence.xml",
        "views/promotion_views.xml",
        "views/promotion_kanban_view.xml",
    ],
    "installable": True,
    "application": False,
}


{
    "name": "Salon Promotion Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý khuyến mãi salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/promotion_sequence.xml",
        "views/promotion_tree_view.xml",
        "views/promotion_search_view.xml",
        "views/promotion_form_view.xml",
        "views/promotion_menu.xml",
    ],
    "installable": True,
    "application": False,
}


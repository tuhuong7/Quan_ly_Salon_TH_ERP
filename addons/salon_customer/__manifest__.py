{
    "name": "Salon Customer Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý khách hàng salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management", "salon_membership_rank"],
    "data": [
        "security/ir.model.access.csv",
        "security/customer_rules.xml",
        "data/customer_sequence.xml",
        "views/customer_tree_view.xml",
        "views/customer_form_view.xml",
        "views/customer_search_view.xml",
        "views/customer_kanban_view.xml",
        "views/customer_menu.xml",
    ],
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "salon_customer/static/src/scss/customer_theme.scss",
        ],
        "web.assets_frontend": [
            "salon_customer/static/src/scss/customer_theme.scss",
        ],
    },
    "installable": True,
    "application": False,
}


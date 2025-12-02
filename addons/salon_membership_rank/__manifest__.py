{
    "name": "Salon Membership Rank Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý hạng thành viên salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/membership_rank_sequence.xml",
        "views/membership_rank_tree_view.xml",
        "views/membership_rank_search_view.xml",
        "views/membership_rank_form_view.xml",
        "views/membership_rank_menu.xml",
    ],
    "installable": True,
    "application": False,
}


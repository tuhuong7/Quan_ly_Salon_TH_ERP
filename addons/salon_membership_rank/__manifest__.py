{
    "name": "Salon Membership Rank Management",
    "version": "19.0.1.0.0",
    "summary": "Quản lý hạng thành viên salon",
    "author": "Tú Hương",
    "depends": ["base", "mail", "salon_management"],
    "data": [
        "security/ir.model.access.csv",
        "data/membership_rank_sequence.xml",
        "views/membership_rank_views.xml",
    ],
    "installable": True,
    "application": False,
}


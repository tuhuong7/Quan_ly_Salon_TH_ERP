{
    "name": "Salon Invoice Extend",
    "version": "19.0.1.0.1",
    "summary": "Mở rộng chức năng hóa đơn salon",
    "author": "Tú Hương",
    "depends": ["base", "account", "salon_management", "salon_customer", "salon_service", "salon_appointment", "salon_service_history", "salon_employee"],
    "data": [
        "security/ir.model.access.csv",
        "data/invoice_sequence.xml",
        "views/sale_invoice_views.xml",
        "views/payment_confirm_wizard_view.xml",
        "reports/invoice_report.xml",
    ],
    "installable": True,
    "application": False,
}


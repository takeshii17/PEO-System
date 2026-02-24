from django.conf import settings
from django.db import models


class Document(models.Model):
    TYPE_SITE_INSTRUCTION = "site_instruction"
    TYPE_NCR = "ncr"
    TYPE_DED_PACKAGE = "ded_package"
    TYPE_BILLING_PACKET = "billing_packet"
    TYPE_WORK_ORDER = "work_order"
    TYPE_REPORT = "report"
    TYPE_CONTRACT = "contract"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [
        (TYPE_SITE_INSTRUCTION, "Site Instruction"),
        (TYPE_NCR, "NCR"),
        (TYPE_DED_PACKAGE, "DED Package"),
        (TYPE_BILLING_PACKET, "Billing Packet"),
        (TYPE_WORK_ORDER, "Work Order"),
        (TYPE_REPORT, "Report"),
        (TYPE_CONTRACT, "Contract"),
        (TYPE_OTHER, "Other"),
    ]

    DIV_ADMIN = "admin"
    DIV_PLANNING = "planning"
    DIV_CONSTRUCTION = "construction"
    DIV_QUALITY = "quality"
    DIV_MAINTENANCE = "maintenance"
    DIVISION_CHOICES = [
        (DIV_ADMIN, "Admin Division"),
        (DIV_PLANNING, "Planning Division"),
        (DIV_CONSTRUCTION, "Construction Division"),
        (DIV_QUALITY, "Quality Division"),
        (DIV_MAINTENANCE, "Maintenance Division"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_FOR_REVIEW = "for_review"
    STATUS_ROUTED = "routed"
    STATUS_PROCESSING = "processing"
    STATUS_APPROVED = "approved"
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_FOR_REVIEW, "For Review"),
        (STATUS_ROUTED, "Routed"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    document_name = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    division = models.CharField(max_length=20, choices=DIVISION_CHOICES, default=DIV_ADMIN)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    description = models.TextField(blank=True)

    date_received_by_peo = models.DateField(null=True, blank=True)
    date_released_to_admin = models.DateField(null=True, blank=True)
    date_received_from_admin = models.DateField(null=True, blank=True)
    date_released_to_accounting = models.DateField(null=True, blank=True)

    billing_type = models.CharField(max_length=120, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    contract_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    revised_contract_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    period_covered = models.CharField(max_length=120, blank=True)
    date_started = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.document_name

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def _scan_upload_path(instance, filename):
    project = instance.project or getattr(instance.document, "project", None)
    project_slug = "unassigned-project"
    if project:
        project_slug = f"{project.id}_{slugify(project.project_title)[:60] or 'project'}"

    document_slug = "document"
    if instance.document:
        document_slug = f"doc_{instance.document_id}_{slugify(instance.document.document_name)[:60] or 'document'}"

    return f"project_scans/{project_slug}/{document_slug}/{filename}"


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
    location = models.CharField(max_length=255, blank=True)
    doc_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
    division = models.CharField(max_length=20, choices=DIVISION_CHOICES, default=DIV_ADMIN)
    project = models.ForeignKey(
        "PlanningProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    description = models.TextField(blank=True)

    date_received_by_peo = models.DateField(null=True, blank=True)
    date_released_to_admin = models.DateField(null=True, blank=True)
    date_received_from_admin = models.DateField(null=True, blank=True)
    date_released_to_accounting = models.DateField(null=True, blank=True)

    billing_type = models.CharField(max_length=120, blank=True)
    contractor_name = models.CharField(max_length=255, blank=True)
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


class DocumentScan(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="scans")
    project = models.ForeignKey(
        "PlanningProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scanned_files",
    )
    file = models.FileField(upload_to=_scan_upload_path)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_scans",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.document.document_name} - {self.file.name}"


class ConstructionStatusReport(models.Model):
    project_name = models.CharField(max_length=255)
    location = models.CharField(max_length=150, blank=True)
    mun = models.CharField(max_length=50, blank=True)
    contractor = models.CharField(max_length=255, blank=True)
    contract_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    ntp_date = models.DateField(null=True, blank=True)
    cd = models.IntegerField(null=True, blank=True)
    original_expiry_date = models.DateField(null=True, blank=True)
    additional_cd = models.IntegerField(null=True, blank=True)
    revised_expiry_date = models.CharField(max_length=120, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    revised_contract_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status_previous = models.CharField(max_length=40, blank=True)
    status_current = models.CharField(max_length=40, blank=True)
    percent_time_elapsed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    slippage_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.project_name


class PlanningBudget(models.Model):
    FUND_20_DEV = "20-development-fund"
    FUND_SEF = "sef-fund"
    FUND_CHOICES = [
        (FUND_20_DEV, "20% Development Fund"),
        (FUND_SEF, "SEF"),
    ]

    STATUS_APPROVED = "approved"
    STATUS_FOR_REVIEW = "for_review"
    STATUS_CHOICES = [
        (STATUS_APPROVED, "Approved"),
        (STATUS_FOR_REVIEW, "For Review"),
    ]

    name = models.CharField(max_length=255)
    fund = models.CharField(max_length=40, choices=FUND_CHOICES, default=FUND_20_DEV)
    total_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    allocated_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    fiscal_year = models.CharField(max_length=20, default="FY 2026")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    @property
    def allocated_value(self):
        return getattr(self, "computed_allocated", self.allocated_amount or 0)

    @property
    def remaining_amount(self):
        return (self.total_budget or 0) - self.allocated_value

    @property
    def utilization_percent(self):
        if not self.total_budget:
            return 0
        try:
            return max(0, min(100, (self.allocated_value / self.total_budget) * 100))
        except Exception:
            return 0

    def __str__(self):
        return self.name


class PlanningProject(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_FOR_REVIEW = "for_review"
    STATUS_APPROVED = "approved"
    STATUS_FOR_BIDDING = "for_bidding"
    STATUS_AWARDED = "awarded"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_FOR_REVIEW, "For Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_FOR_BIDDING, "For Bidding"),
        (STATUS_AWARDED, "Awarded"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    project_title = models.CharField(max_length=255)
    fund = models.CharField(
        max_length=40,
        choices=PlanningBudget.FUND_CHOICES,
        default=PlanningBudget.FUND_20_DEV,
    )
    budget_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.project_title

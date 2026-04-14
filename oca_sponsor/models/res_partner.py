# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, exceptions, fields, models
from odoo.osv.expression import NOT_OPERATOR

SPONSOR_WEBSITE_FIELDS = [
    # editable fields by the sponsor from the portal
    "name",
    "sponsor_name",
    "email",
    "phone",
    "website",
    "website_description_why_sponsoring",
    "website_short_description",
    "website_long_description",
    "image_1920",
]


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "html.field.history.mixin"]
    _html_field_history_size_limit = 20

    grade_id = fields.Many2one(
        comodel_name="res.partner.grade",
        string="Sponsor Level",
    )
    is_sponsor = fields.Boolean(
        compute="_compute_is_sponsor",
        search="_search_is_sponsor",
    )
    is_sponsor_reviewer = fields.Boolean(compute="_compute_is_sponsor_reviewer")
    sponsor_to_review = fields.Boolean(
        string="To review",
        compute="_compute_sponsor_to_review",
        store=True,
        default=False,
        help="After the sponsor modifies its data from the web portal in autonomy, "
        "the changes must be reviewed before being published on the website.",
        tracking=True,
    )
    sponsor_review_data = fields.Html(
        # For history wizzard
        compute="_compute_sponsor_review_data",
        sanitize=True,
    )
    sponsorship_line_ids = fields.One2many(
        string="Sponsorship history",
        comodel_name="sponsorship.line",
        inverse_name="partner_id",
    )
    # Website fields
    sponsor_name = fields.Char(
        string="Alternate name", help="If empty, the company name is displayed instead."
    )
    sponsor_child_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="sponsor_parent_id",
        string="Sponsored companies",
        domain=[("is_company", "=", True), ("is_sponsor", "=", False)],
        help="Choose company who are included in the sponsorship, like branch, "
        "subsidiaries or commercial partners.",
    )
    sponsor_parent_id = fields.Many2one(
        comodel_name="res.partner",
        string="Sponsoring company",
        ondelete="set null",
        domain=[("is_sponsor", "=", True)],
    )
    sponsor_country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="res_partner_country_rel",
        column1="partner_id",
        column2="country_id",
        string="Countries",
        compute="_compute_sponsor_country_ids",
        store=True,
        readonly=False,
    )
    sponsor_industry_ids = fields.Many2many(
        comodel_name="res.partner.industry",
        relation="res_partner_partner_industry_rel",
        column1="partner_id",
        column2="industry_id",
        string="Industries",
        compute="_compute_sponsor_industry_ids",
        store=True,
        readonly=False,
        help="On the website, 1 partner may have several industries. "
        "Their description is the same for all sponsors.",
    )
    website_long_description = fields.Text(
        string="Sponsor long description",
        translate=True,
    )
    website_description_why_sponsoring = fields.Text(
        string="Why sponsoring description",
        translate=True,
    )
    blog_post_ids = fields.One2many(
        string="Blog posts",
        comodel_name="blog.post",
        inverse_name="author_id",
    )
    blog_post_count = fields.Integer(
        string="Blog posts count",
        compute="_compute_blog_post_count",
    )

    # ====== Compute ======#
    @api.depends("grade_id")
    def _compute_is_sponsor(self):
        for partner in self:
            partner.is_sponsor = bool(partner.grade_id)

    @api.model
    def _search_is_sponsor(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise NotImplementedError("Operation not supported.")
        _not = []
        if operator == "!=" and value or operator == "=" and not value:
            _not = [NOT_OPERATOR]
        return _not + [("grade_id", "!=", False)]

    @api.depends("country_id", "grade_id")
    def _compute_sponsor_country_ids(self):
        self._compute_sponsor_replace_in("country_id", "sponsor_country_ids")

    @api.depends("industry_id", "grade_id")
    def _compute_sponsor_industry_ids(self):
        self._compute_sponsor_replace_in("industry_id", "sponsor_industry_ids")

    def _compute_sponsor_replace_in(self, origin_field, sponsor_field):
        """Replace `sponsor._origin[field]` by `sponsor[field]`
        in `sponsor[sponsor_field]`, or add it if no origin value"""
        sponsors = self.filtered(lambda x: x.is_sponsor)
        for sponsor in sponsors:
            old, new = sponsor._origin[origin_field], sponsor[origin_field]._origin
            current = sponsor[sponsor_field]._origin
            if new and new not in current:
                sponsor[sponsor_field] = [Command.link(new.id)]
            if old and old != new and old in current:
                sponsor[sponsor_field] = [Command.unlink(old.id)]

    @api.depends("blog_post_ids")
    def _compute_blog_post_count(self):
        for partner in self:
            partner.blog_post_count = len(partner.blog_post_ids)

    @api.depends_context("uid")
    def _compute_is_sponsor_reviewer(self):
        """Field needed in the view"""
        self.is_sponsor_reviewer = self.env.user._is_sponsor_reviewer()

    @api.depends("html_field_history")
    def _compute_sponsor_to_review(self):
        """When `html.field.history.mixin` writes a new revision in `html_field_history`
        this means fields have changed, and thus require a review"""
        self._set_sponsor_to_review()

    @api.depends(*SPONSOR_WEBSITE_FIELDS)
    def _compute_sponsor_review_data(self):
        for partner in self:
            partner.sponsor_review_data = partner._get_sponsor_review_data()

    def _get_sponsor_review_data(self):
        return "\n\n".join(
            [
                '<h1 class="mt-4">{name}</h1>\n{content}'.format(
                    name=self._fields[field].string,
                    content=self[field] or "",
                )
                for field in SPONSOR_WEBSITE_FIELDS
            ]
        )

    # ====== ORM ======#
    @api.model_create_multi
    def create(self, vals_list):
        """The ORM recomputes stored field right after create
        => Prevent it for `sponsor_to_review` to stick to default value (False)"""
        records = super().create(vals_list)
        self.env.remove_to_compute(self._fields["sponsor_to_review"], records)
        return records

    def write(self, vals):
        """Hack to trigger logics of `html.field.history.mixin`
        without storing `sponsor_review_data`"""
        if not fields.first(self).is_sponsor_reviewer and set(vals).intersection(
            SPONSOR_WEBSITE_FIELDS
        ):
            return all(
                super(ResPartner, partner).write(
                    vals | {"sponsor_review_data": partner.sponsor_review_data}
                )
                for partner in self
            )
        return super().write(vals)

    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Order res.partner sponsor view in Kanban and List
        with the ones to review at first"""
        if self._context.get("membership_sponsor"):
            delimiter = "" if not order else ", "
            order = "sponsor_to_review DESC" + delimiter + (order or "")
        return super().search_fetch(domain, field_names, offset, limit, order)

    # ===== Actions & buttons =====#
    def button_sponsor_review_accept(self):
        if not self.env.user._is_sponsor_reviewer():
            raise exceptions.AccessError(_("You are not a Sponsor Reviewer."))
        self._sponsor_review_accept()

    # ===== Business logics =====#
    def _get_versioned_fields(self):
        """For `html.field.history.mixin`"""
        return ["sponsor_review_data"]

    def _set_sponsor_to_review(self):
        """Pause the syncing of new sponsors data until their review,
        when their data are updated from the portal,
        and notify reviewers with an activity"""
        if self.env.user._is_sponsor_reviewer():
            return

        sponsors = self.filtered(lambda x: x.is_sponsor and not x.sponsor_to_review)
        if sponsors:
            sponsors.sponsor_to_review = True
            sponsors._sponsor_reviewers_notify()

    def _sponsor_reviewers_notify(self, unnotify=None):
        reviewer_team = self.env["res.users"]._get_sponsor_reviewer_team()
        if unnotify:
            self.activity_ids.filtered(
                lambda x: x.team_id == reviewer_team
            ).action_cancel()
        else:
            self.activity_schedule(
                team_id=reviewer_team.id,
                note=_(
                    "The sponsor changed its information from its profile. "
                    "Please review those changes to publish them on the website."
                ),
                act_type_xmlid="mail.mail_activity_data_warning",
            )

    def _sponsor_review_accept(self):
        self._sponsor_reviewers_notify(unnotify=True)
        self.sudo().write(
            {  # 'sudo' to bypass AccessError of 'website.published.multi.mixin'
                "is_published": True,
                "sponsor_to_review": False,
            }
        )

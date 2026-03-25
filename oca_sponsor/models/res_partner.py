# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, exceptions, _
from odoo.osv.expression import NOT_OPERATOR

from hashlib import md5

SPONSOR_WEBSITE_FIELDS = {
    # editable fields by the sponsor from the portal
    "name",
    "email",
    "phone",
    "website",
    "country_id", "sponsor_country_ids",
    "website_short_description",
    "website_long_description",
    "website_description_why_sponsoring",
    "industry_id", "sponsor_industry_ids",
    "avatar_1920", "avatar_1024", "avatar_512", "avatar_256", "avatar_128",
}

class ResPartner(models.Model):
    _inherit = ["res.partner"]

    grade_id = fields.Many2one(
        comodel_name="res.partner.grade",
        string="Sponsor Level",
    )
    is_sponsor = fields.Boolean(
        compute="_compute_is_sponsor",
        search="_search_is_sponsor",
    )
    sponsor_to_review = fields.Boolean(
        string="To review",
        default=False,
        help="After the sponsor modifies its data from the web portal in autonomy, "
             "the changes must be reviewed before being published on the website.",
    )
    sponsorship_line_ids = fields.One2many(
        string="Sponsorship history",
        comodel_name="sponsorship.line",
        inverse_name="partner_id",
    )
    # Website fields
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
    industry_id = fields.Many2one(
        compute="_compute_industry_id",
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

    #====== Compute ======#
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
        """Put new `country_id` in `sponsor_country_ids`"""
        self._compute_sponsor_field_ids("country_id")
    
    @api.depends("sponsor_industry_ids", "grade_id")
    def _compute_industry_id(self):
        """`industry_id`, if empty, is filled in by `sponsor_industry_ids`"""
        for partner in self:
            industries = partner.sponsor_industry_ids
            if industries and partner.industry_id not in industries:
                partner.industry_id = fields.first(industries)
    
    @api.depends("industry_id", "grade_id")
    def _compute_sponsor_industry_ids(self):
        """Put new `industry_id` in `sponsor_industry_ids`"""
        self._compute_sponsor_field_ids("industry_id")
    
    def _compute_sponsor_field_ids(self, field):
        """Called for both `sponsor_country_ids` and `sponsor_industry_ids`"""
        for sponsor in self.filtered(lambda x: x.is_sponsor):
            sponsor_field = "sponsor_" + field + "s"
            old, new = sponsor._origin[field], sponsor[field]
            if not new in sponsor[sponsor_field]:
                sponsor[sponsor_field] |= new
            if old != new and old in sponsor[sponsor_field]:
                sponsor[sponsor_field] -= old
    
    @api.depends("blog_post_ids")
    def _compute_blog_post_count(self):
        for partner in self:
            partner.blog_post_count = len(partner.blog_post_ids)

    #====== CRUD ======#
    def write(self, vals):
        """Set in review the sponsor whose relevant data changed"""
        keys = set(vals) & SPONSOR_WEBSITE_FIELDS
        
        if keys:
            before = self._get_hashes(keys)
        
        res = super().write(vals)
        
        if keys and (partners := self._compare_hashes(keys, before)):
            partners._set_sponsor_to_review()
        
        return res
    
    def _get_hashes(self, keys, before=None):
        return {
            partner.id: md5(str(self.read(list(keys))).encode()).hexdigest()
            for partner in self
        }
    def _compare_hashes(self, keys, before):
        after = self._get_hashes(keys)
        return self.browse([
            partner_id
            for partner_id, after in after.items()
            if before[partner_id] != after
        ])
    
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """Order res.partner sponsor view in Kanban and List
        with the ones to review as firsts"""
        if self._context.get("membership_sponsor"):
            delimiter = "" if not order else ", "
            order = "sponsor_to_review DESC" + delimiter + (order or '')
        return super().search_fetch(domain, field_names, offset, limit, order)

    #===== Business logics =====#
    def button_sponsor_review_accept(self):
        if not self.env.user.has_groups("membership_extension.group_membership_manager"):
            raise exceptions.AccessError(_(
                "Only a membership manager may publish sponsor information to the website."
            ))
        self._sponsor_review_accept()
    
    def action_open_blog_post(self):
        return {
            'name': _("Blog posts"),
            'type': 'ir.actions.act_window',
            'res_model': "blog.post",
            'view_mode': 'list,form',
            'domain': [("author_id", "=", self.id)],
        }

    def _sponsor_review_accept(self):
        # Re-enable syncing
        self.sudo().write({ # 'sudo' to bypass AccessError of 'website.published.multi.mixin'
            "is_published": True,
            "sponsor_to_review": False,
        })

        # Finish review
        activity_type = self.env.ref("oca_sponsor.mail_activity_review_sponsor_oca")
        self.activity_ids.filtered(
            lambda x: x.activity_type_id == activity_type
        ).sudo().action_done() # 'sudo' because activities of other users

    def _set_sponsor_to_review(self):
        """Pause the syncing of new sponsors data until their review,
        when their data are updated from the portal,
        and notify reviewers with an activity"""
        if (
            self._context.get("skip_sponsor_review")
            or self.env.user.has_groups("membership_extension.group_membership_manager")
        ):
            return
        self = self.with_context(skip_sponsor_review=True) # prevent infinite loop
        
        # Pause syncing
        sponsors = self.filtered(
            lambda x: x.is_sponsor and not x.sponsor_to_review
        )
        if sponsors:
            sponsors.sponsor_to_review = True

            # Notify reviewers
            users = self.env.ref("membership_extension.group_membership_manager").users
            for user in users:
                # We use a specific activity template for custom done/cancel logic of mail.activity
                sponsors.activity_schedule(
                    act_type_xmlid="oca_sponsor.mail_activity_review_sponsor_oca",
                    user_id=user.id,
                    note=_("The sponsor changes its information from its profile. "
                        "Please review the change to publish them on the website."),
                )

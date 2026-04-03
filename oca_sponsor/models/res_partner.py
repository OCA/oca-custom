# Copyright 2026 AKRETION
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, Command, exceptions, _
from odoo.osv.expression import NOT_OPERATOR
from odoo.tools.safe_eval import safe_eval

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
    is_sponsor_reviewer = fields.Boolean(
        compute="_compute_is_sponsor_reviewer"
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
             "Their description is the same for all sponsors."
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
            if new and not new in current:
                sponsor[sponsor_field] = [Command.link(new.id)]
            if old and old != new and old in current:
                sponsor[sponsor_field] = [Command.unlink(old.id)]

    @api.depends("blog_post_ids")
    def _compute_blog_post_count(self):
        for partner in self:
            partner.blog_post_count = len(partner.blog_post_ids)

    #====== CRUD & ORM ======#
    def write(self, vals):
        """Set the sponsor in review as soon as the sponsors fields are touched
        by a non-authorized person"""
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
        with the ones to review at first"""
        if self._context.get("membership_sponsor"):
            delimiter = "" if not order else ", "
            order = "sponsor_to_review DESC" + delimiter + (order or '')
        return super().search_fetch(domain, field_names, offset, limit, order)

    #===== Actions & buttons =====#
    def action_open_blog_post(self):
        action = self.env.ref("website_blog.action_blog_post").sudo().read([])[0]
        action.update({
            "domain": [("author_id", "=", self.id)],
            "context": (
                safe_eval(action.get("context", "{}")) |
                {
                    "default_author_id": self.id,
                }
            )
        })
        return action

    def button_sponsor_review_accept(self):
        if not self.env.user._is_sponsor_reviewer():
            raise exceptions.AccessError(_("You are not a Sponsor Reviewer."))
        self._sponsor_review_accept()

    #===== Business logics =====#
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

    def _sponsor_reviewers_notify(self, notify=True):
        """`notify=True`: notify the reviewers when review starts
        `notify=False`: remove the activity at review validation"""
        reviewer_team = self.env["res.users"]._get_sponsor_reviewer_team()
        if not notify:
            self.activity_ids.filtered(lambda x: x.team_id == reviewer_team).sudo().unlink()
        else:
            self.sudo().activity_schedule(
                team_id=reviewer_team.id,
                note=_("The sponsor changed its information from its profile. "
                       "Please review those changes to publish them on the website."
                ),
            )

    def _sponsor_review_accept(self):
        self._sponsor_reviewers_notify(notify=False)
        self.sudo().write({ # 'sudo' to bypass AccessError of 'website.published.multi.mixin'
            "is_published": True,
            "sponsor_to_review": False,
        })

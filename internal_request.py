from email.policy import default

from odoo import fields,models,api
from odoo.exceptions import ValidationError
from odoo.orm.decorators import readonly
from odoo.exceptions import UserError
from odoo.tools.safe_eval import datetime
from datetime import datetime, timedelta


class InternalRequest(models.Model):
    _name='internal.request'
    _description='Internal Request'
    _inherit = ['mail.thread','mail.activity.mixin']

    request_id=fields.Many2one('res.user',string='Request Id',request=True,default=lambda self:self.env.usre)
    requester=fields.Char('Requester')
    reason=fields.Char('Reason')
    approver_id=fields.Many2one('res.user',srting='Approver By',readonly=True)
    request_date=fields.Datetime(string='Request Date',default=fields.Datetime.now())
    decision_date=fields.Datetime(string='Decision Date',readonly=True)
    state=fields.Selection([
       ('draft','Draft'),
       ('submitted','Submitted'),
       ('approved','Approved'),
       ('rejected','Rejected'),
    ],default='draft')


    def action_submit(self):
        for rec in self:
            if not rec.approver_id:
                raise ValidationError('You must choose an approver before submitting')
            if not rec.reason:
                raise ValidationError('You must fill in the reason before submitting')

            if rec.state=='draft':
                rec.state='submitted'

                rec.message_post(
                    body='تم إرسال الطلب وبحاجة إلى موافقة المدير',
                    subject='request submitted by %s'%self.env.user.name,
                    subtype_xmlid="mail.mt_comment",
                )

                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=rec.approver_id.id,
                    summary=("Approve Internal Request"),
                    note=('please review and apporve thise request'),
                    date_deadline=datetime.now()+timedelta(days=2),

                    )


    def action_approve(self):
        for rec in self:
            if rec.state!='submitted':
                raise ValidationError("can't approve this request")

            rec.state='approved'

            activities = rec.activity_ids.filtered(
                lambda a: a.activity_type_id.xml_id == 'mail.mail_activity_data_todo'
            )
            activities.action_done()

            rec.approver_id=self.env.user
            rec.decision_date=fields.Datetime.now()
            rec.message_post(
                body='تمت الموافقة على الطلب',
                subject='Request approved by %s'%self.env.user.name,
                subtype_xmlid='mail.mt_comment',
            )


    def action_reject(self):
        for rec in self:
            if rec.state!='submitted':
                raise ValidationError("can't reject this request")

            rec.state='rejected'
            activities = rec.activity_ids.filtered(
                lambda a: a.activity_type_id.xml_id == 'mail.mail_activity_data_todo'
            )
            activities.action_done()

            rec.approver_id=self.env.user
            rec.decision_date=fields.Datetime.now()
            rec.message_post(
                body='تم رفض الطلب',
                subject=f'Request rejected by{self.env.user.name}',
                type='notification',
                subtype_xmlid='mail.mt_comment',
            )



    def write(self,vals):
        for rec in self:
            if rec.state !='draft':
                raise ValidationError("can't update")
        super(InternalRequest,self).write(vals)


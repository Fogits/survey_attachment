import base64

from odoo import api, fields, models


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_attachment = fields.Binary('Question attachment')
    type = fields.Selection(
        selection_add=[('upload_file', 'Upload file')])


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input_line'

    answer_type = fields.Selection(
        selection_add=[('upload_file', 'Upload file')])

    file = fields.Binary('Upload file')
    file_type = fields.Selection([('image', 'image'), ('pdf', 'pdf')])

    @api.model
    def save_line_upload_file(self, user_input_id, question, post, answer_tag):
        vals = {
            'user_input_id': user_input_id,
            'question_id': question.id,
            'survey_id': question.survey_id.id,
            'skipped': False
        }
        file_name = str(post[answer_tag])
        file_type = file_name.find("('application/pdf')")
        image_type = file_name.find("('image/png')")
        if file_type > -1:
            vals.update({'file_type': 'pdf'})
        if image_type > -1:
            vals.update({'file_type': 'image'})

        if question.constr_mandatory:
            file = base64.encodebytes(post[answer_tag].read())
        else:
            file = base64.encodebytes(post[answer_tag].read()) if post[answer_tag] else None
        if answer_tag in post:
            vals.update({'answer_type': 'upload_file', 'file': file})
        else:
            vals.update({'answer_type': None, 'skipped': True})
        old_uil = self.search([
            ('user_input_id', '=', user_input_id),
            ('survey_id', '=', question.survey_id.id),
            ('question_id', '=', question.id)
        ])
        if old_uil:
            old_uil.write(vals)
        else:
            old_uil.create(vals)
        return True

from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema


class ThemeRequestSchema(Schema):
    title = fields.Str(required=True)


class ThemeSchema(Schema):
    id = fields.Int()
    title = fields.Str()


class ThemeResponseSchema(OkResponseSchema):
    data = fields.Nested(ThemeSchema)


class ThemeListSchema(Schema):
    themes = fields.List(fields.Nested(ThemeSchema))


class ThemeListResponseSchema(OkResponseSchema):
    data = fields.Nested(ThemeListSchema)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionRequestSchema(Schema):
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.List(fields.Nested(AnswerSchema, required=True), required=True)


class QuestionSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    theme_id = fields.Int()
    answers = fields.List(fields.Nested(AnswerSchema))


class QuestionResponseSchema(OkResponseSchema):
    data = fields.Nested(QuestionSchema)


class QuestionListSchema(Schema):
    questions = fields.List(fields.Nested(QuestionSchema))


class QuestionListResponseSchema(OkResponseSchema):
    data = fields.Nested(QuestionListSchema)

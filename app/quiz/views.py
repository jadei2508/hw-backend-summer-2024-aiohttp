from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema, docs

from app.quiz.models import Answer
from app.quiz.schemes import ThemeSchema, QuestionSchema, ThemeResponseSchema, ThemeRequestSchema, \
    ThemeListResponseSchema, QuestionResponseSchema, QuestionRequestSchema, QuestionListResponseSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=["theme"], summary="create theme")
    @request_schema(ThemeRequestSchema)
    @response_schema(ThemeResponseSchema, 200)
    async def post(self):
        title = self.data["title"]
        theme = await self.store.quizzes.get_theme_by_title(title)
        if theme is not None:
            raise HTTPConflict
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=["theme"], summary="list theme")
    @response_schema(ThemeListResponseSchema, 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data={'themes': ThemeSchema(many=True).dump(themes)})


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=["question"], summary="create question")
    @request_schema(QuestionRequestSchema)
    @response_schema(QuestionResponseSchema, 200)
    async def post(self):
        title = self.data['title']
        theme_id = self.data['theme_id']
        answers = [
            Answer(
                title=answer['title'],
                is_correct=answer['is_correct']
            ) for answer in self.data['answers']
        ]
        question = await self.validate_question(title, theme_id, answers)
        return json_response(data=QuestionSchema().dump(question))

    async def validate_question(self, title, theme_id, answers):
        if sum([answer.is_correct for answer in answers]) != 1:
            raise HTTPBadRequest
        if len(answers) <= 1:
            raise HTTPBadRequest
        if await self.store.quizzes.get_question_by_title(title):
            raise HTTPConflict
        if not await self.store.quizzes.get_theme_by_id(theme_id):
            raise HTTPNotFound
        question = await self.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=answers
        )
        return question


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=["question"], summary="list question")
    @response_schema(QuestionListResponseSchema, 200)
    async def get(self):
        questions = await self.store.quizzes.list_questions()
        return json_response(data={'questions': QuestionSchema(many=True).dump(questions)})

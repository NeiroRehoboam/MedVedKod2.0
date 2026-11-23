from django.contrib import admin

from .models import BaseQuestion, BaseQuestionOption


class BaseQuestionOptionInline(admin.TabularInline):
    model = BaseQuestionOption
    extra = 1
    fields = ("text", "order")


@admin.register(BaseQuestion)
class BaseQuestionAdmin(admin.ModelAdmin):
    inlines = [BaseQuestionOptionInline]
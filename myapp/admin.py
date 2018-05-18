from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from django import forms

# from .widgets import RichTextEditorWidget


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False # 用户没了，这个自然就没了，否则这个不能删

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

class ArticleInline(admin.TabularInline):
    # 如果从 StackedInline 继承，比较占版面，而 TabularInline 则显示得更加紧凑。
    model = Article
    extra = 3
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
                            attrs = {
                            'rows': 20,
                            'cols': 150,
                            'style': 'height: 5em;'
                            }
            ) },
    }

class BranchCommentInline(admin.TabularInline):
    model = BranchComment
    extra = 1

class BranchAdmin(admin.ModelAdmin):
    model = Branch
    inlines = [ArticleInline, BranchCommentInline]
    # list_display 是用于设置 Branch 对象的 index 页面显示的栏目。
    list_display = ('title', 'pub_date')

# class ArticleAdmin(admin.ModelAdmin):
#     fieldsets = [
#         ('法条信息', {'fields': ['Branch', 'Article_text'], 'classes': ('wide', 'extrapretty')}),
#     ]
#     list_display = ('Branch', 'Article_text')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Topic)
# admin.site.register(Article, ArticleAdmin)
admin.site.register(Branch, BranchAdmin)









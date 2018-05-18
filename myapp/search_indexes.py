import datetime
from haystack import indexes
from myapp.models import *

from haystack.query import SearchQuerySet

class BranchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True) # document=True 使得该条目成为主键
    title = indexes.CharField(model_attr='title')
    chairman = indexes.CharField(model_attr='chairman')
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    
    def get_model(self):
        return Branch

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    article_text = indexes.CharField(model_attr='article_text')
    num = indexes.IntegerField(model_attr='num')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
import logging
from django import forms
from . import models

logger = logging.getLogger('app')


class CategoryFrom(forms.ModelForm):
    parent_id = forms.ChoiceField(choices=models.Category.objects.none(), label="Родительская категория", required=False)

    class Meta:
        model = models.Category
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(CategoryFrom, self).__init__(*args, **kwargs)
        choice_list = [(None, "Выберите родительскую категорию")]
        choice_list.extend(models.Category.objects.filter(parent_id__isnull=True).values_list("id", "name"))
        self.fields['parent_id'].choices = choice_list

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['parent_id']:
            cleaned_data.pop('parent_id')


class ProductFrom(forms.ModelForm):
    category_id = forms.ChoiceField(choices=models.Category.objects.none(), label="Родительская категория")

    class Meta:
        model = models.Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductFrom, self).__init__(*args, **kwargs)
        choice_list = [(None, "Выберите категорию")]
        choice_list.extend(models.Category.objects.filter(parent_id__isnull=False).values_list("id", "name"))
        self.fields['category_id'].choices = choice_list

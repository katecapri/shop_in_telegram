import uuid
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('app')


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125, verbose_name=_("Имя пользователя"))
    phone = models.CharField(max_length=125, verbose_name=_("Телефон"))
    chat_id = models.IntegerField(verbose_name=_("ID чата"))

    class Meta:
        db_table = 'users'
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125, verbose_name=_("Название категории"))
    parent_id = models.UUIDField(verbose_name=_("Родительская категория"), null=True)

    class Meta:
        db_table = 'categories'
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125, verbose_name=_("Название товара"))
    description = models.CharField(max_length=255, verbose_name=_("Описание товара"))
    price = models.FloatField(max_length=125, verbose_name=_("Цена"))
    photo = models.ImageField(verbose_name=_("Изображение"))
    category_id = models.UUIDField(verbose_name=_("Категория товара"))

    class Meta:
        db_table = 'products'
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        self.photo.name = str(self.id) + '.' + self.photo.name.split('.')[-1]
        super().save(**kwargs)


class CartProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(verbose_name=_("Пользователь"))
    product_id = models.UUIDField(verbose_name=_("Товар"))
    count = models.IntegerField(verbose_name=_("Количество"))

    class Meta:
        db_table = 'cart_products'
        verbose_name = _('Товар в корзине')
        verbose_name_plural = _('Товары в корзинах')


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255, verbose_name=_("Вопрос"))
    answer = models.CharField(max_length=255, verbose_name=_("Ответ"))

    class Meta:
        db_table = 'faq'
        verbose_name = _('Частозадаваемый вопрос')
        verbose_name_plural = _('Частозадаваемые вопросы')

    def __str__(self):
        return self.question
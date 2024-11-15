from datetime import datetime
from uuid import uuid4
from sqlalchemy import MetaData, Column, String, Integer, ForeignKey, Float
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base(metadata=MetaData())


class User(Base):
    __tablename__ = 'users'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    phone = Column(String(), nullable=False)
    chat_id = Column(Integer())
    name = Column(String(), nullable=False)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    name = Column(String(), nullable=False)
    parent_id = Column(postgresql.UUID(as_uuid=True), nullable=True)


class Product(Base):
    __tablename__ = 'products'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    name = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
    price = Column(Float(), nullable=False)
    category_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Category.id, ondelete="PROTECT"))
    photo = Column(String(), nullable=False)

    category = relationship(Category, backref='category_products')


class CartProduct(Base):
    __tablename__ = 'cart_products'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    user_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False,)
    product_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    count = Column(Integer(), nullable=False)

    user = relationship(User, backref='user_cart_products')


class FAQ(Base):
    __tablename__ = 'faq'

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4())
    question = Column(String(), nullable=False)
    answer = Column(String(), nullable=False)


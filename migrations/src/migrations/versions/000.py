"""Create tables

Revision ID: 000
Revises:
Create Date: 2023-12-09 10:00:00

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table('users',
                    sa.Column('id', postgresql.UUID(as_uuid=True), default=uuid4(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('phone', sa.String(), nullable=False),
                    sa.Column('chat_id', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('categories',
                    sa.Column('id', postgresql.UUID(as_uuid=True), default=uuid4(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('products',
                    sa.Column('id', postgresql.UUID(as_uuid=True), default=uuid4(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Float(), nullable=True),
                    sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('photo', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('cart_products',
                    sa.Column('id', postgresql.UUID(as_uuid=True), default=uuid4(), nullable=False),
                    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
                    sa.Column('count', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))

    op.create_table('faq',
                    sa.Column('id', postgresql.UUID(as_uuid=True), default=uuid4(), nullable=False),
                    sa.Column('question', sa.String(), nullable=False),
                    sa.Column('answer', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))


def downgrade() -> None:
    op.drop_table('faq')
    op.drop_table('cart_products')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('users')
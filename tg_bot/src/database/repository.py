import uuid
from sqlalchemy import select, delete

from src.database.models import User, Category, Product, CartProduct, FAQ


class Repository:
    def __init__(self, session):
        self.session = session
        self.model_user = User
        self.model_category = Category
        self.model_product = Product
        self.model_cart_product = CartProduct
        self.model_faq = FAQ

    async def get_user_by_chat_id(self, chat_id):
        query = select(self.model_user).where(self.model_user.chat_id == chat_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def create_user(self, chat_id, name, phone_number):
        new_user = self.model_user(
            id=uuid.uuid4(),
            phone=phone_number,
            chat_id=chat_id,
            name=name,
        )
        self.session.add(new_user)
        await self.session.commit()
        return new_user.id

    async def get_main_categories(self):
        query = select(self.model_category).where(self.model_category.parent_id == None)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_subcategories_by_category_id(self, main_category_id):
        query = select(self.model_category).where(self.model_category.parent_id == main_category_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_products_for_subcategory(self, subcategory_id):
        query = select(self.model_product).where(self.model_product.category_id == subcategory_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_product_by_id(self, product_id):
        query = select(self.model_product).where(self.model_product.id == product_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def add_product_to_cart(self, user_id, product_id, count):
        new_cart_product = self.model_cart_product(
            id=uuid.uuid4(),
            user_id=user_id,
            product_id=product_id,
            count=count
        )
        self.session.add(new_cart_product)
        await self.session.commit()

    async def get_cart_products_for_user(self, user_id):
        query = select(self.model_cart_product).where(self.model_cart_product.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_cart_product_by_id(self, cart_product_id):
        query = select(self.model_cart_product).where(self.model_cart_product.id == cart_product_id)
        result = await self.session.execute(query)
        return result.scalar()

    async def delete_cart_product_by_id(self, cart_product_id):
        query = delete(self.model_cart_product).where(self.model_cart_product.id == cart_product_id)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_cart_for_user(self, user_id):
        query = delete(self.model_cart_product).where(self.model_cart_product.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_faq_by_question_word(self, word):
        query = select(self.model_faq).where(self.model_faq.question.ilike(f"%{word.lower()}%"))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_faq_questions(self):
        query = select(self.model_faq)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_faq_question_by_id(self, faq_question_id):
        query = select(self.model_faq).where(self.model_faq.id == faq_question_id)
        result = await self.session.execute(query)
        return result.scalar()

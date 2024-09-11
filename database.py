from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger

# Настройка соединения с асинхронной базой данных
DATABASE_URL = "postgresql+asyncpg://postgres:qwerty@localhost:5432/test_work_tg_bot"

engine = create_async_engine(DATABASE_URL)
# Создание асинхронной сессии для взаимодействия с БД
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Базовый класс для таблиц
Base = declarative_base()


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_tariff = Column(String, default="1")
    is_topic = Column(String, default="2")
    subscription_end = Column(DateTime, nullable=True)
    notification_enabled = Column(Boolean, default=True)
    facts = Column(String, nullable=True)


# Асинхронное создание таблиц
async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Пример получения сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        return session


# Функция для регистрации пользователя
async def register_user(telegram_id, username, first_name, last_name):
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                return False
            else:
                new_user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)  # Обновляем объект нового пользователя
                return True
        except Exception as e:
            print(f"Ошибка регистрации пользователя: {e}")
            await session.rollback()
            return False


async def get_tariff_by_id(telegram_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user.is_tariff
            else:
                return None


# Функция для обновления тарифа пользователя
async def update_user_tariff(telegram_id, new_tariff_value):
    async with AsyncSessionLocal() as session:
        try:
            # Находим пользователя по telegram_id
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем значение поля is_tariff
                user.is_tariff = new_tariff_value

                # Фиксируем изменения
                await session.commit()

                return True  # Возвращаем True, если успешно обновлено
            else:
                return False  # Пользователь не найден
        except Exception as e:
            print(f"Ошибка при обновлении тарифа пользователя: {e}")
            await session.rollback()
            return False


# Функция для обновления конца подписки
async def update_user_subscription_end(telegram_id, new_subscription_end):
    async with AsyncSessionLocal() as session:
        try:
            # Находим пользователя по telegram_id
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем значение поля subscription_end
                user.subscription_end = new_subscription_end

                # Фиксируем изменения
                await session.commit()

                return True  # Возвращаем True, если успешно обновлено
            else:
                return False  # Пользователь не найден
        except Exception as e:
            print(f"Ошибка при обновлении тарифа пользователя: {e}")
            await session.rollback()
            return False


async def get_topic_by_id(telegram_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user.is_topic
            else:
                return None


# Функция для обновления темы
async def update_user_is_topic(telegram_id, new_is_topic):
    async with AsyncSessionLocal() as session:
        try:
            # Находим пользователя по telegram_id
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем значение поля is_topic
                user.is_topic = new_is_topic

                # Фиксируем изменения
                await session.commit()

                return True  # Возвращаем True, если успешно обновлено
            else:
                return False  # Пользователь не найден
        except Exception as e:
            print(f"Ошибка при обновлении тарифа пользователя: {e}")
            await session.rollback()
            return False


# Функция для обновления темы
async def update_user_notification_enabled(telegram_id, new_notification_enabled):
    async with AsyncSessionLocal() as session:
        try:
            # Находим пользователя по telegram_id
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем значение поля notification_enabled
                user.new_notification_enabled = new_notification_enabled

                # Фиксируем изменения
                await session.commit()

                return True  # Возвращаем True, если успешно обновлено
            else:
                return False  # Пользователь не найден
        except Exception as e:
            print(f"Ошибка при обновлении тарифа пользователя: {e}")
            await session.rollback()
            return False


async def get_notification_enabled_by_id(telegram_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user.notification_enabled
            else:
                return None


# Функция для получения всех telegram_id из таблицы users
async def get_all_telegram_ids():
    async with AsyncSessionLocal() as session:
        try:
            # Выполняем запрос для получения всех telegram_id
            stmt = select(User.telegram_id)
            result = await session.execute(stmt)

            # Получаем все telegram_id как список
            telegram_ids = [row[0] for row in result.fetchall()]

            return telegram_ids  # Возвращаем список идентификаторов
        except Exception as e:
            print(f"Ошибка при получении списка telegram_id: {e}")
            return []


# Функция для обновления фактов
async def update_user_facts(telegram_id, new_facts):
    async with AsyncSessionLocal() as session:
        try:
            # Находим пользователя по telegram_id
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                # Обновляем значение поля facts
                user.facts = new_facts

                # Фиксируем изменения
                await session.commit()

                return True  # Возвращаем True, если успешно обновлено
            else:
                return False  # Пользователь не найден
        except Exception as e:
            print(f"Ошибка при обновлении тарифа пользователя: {e}")
            await session.rollback()
            return False


async def get_facts_by_id(telegram_id):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(User).filter_by(telegram_id=telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                return user.facts
            else:
                return None

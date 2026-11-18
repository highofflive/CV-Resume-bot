import os
from dotenv import load_dotenv
from sqlalchemy import BigInteger, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# Завантажуємо змінні оточення з файлу .env у пам'ять програми
load_dotenv()

# Дістаємо адресу бази даних із .env.
# Якщо змінної там ще немає — автоматично створиться локальний файл cv.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cv.db")

# Налаштування безпеки потоків: SQLite вимагає цей параметр, оскільки
# pyTelegramBotAPI обробляє повідомлення користувачів у різних потоках.
# Для PostgreSQL цей словник залишиться порожнім автоматично.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Створюємо "двигун" — головне з'єднання Python із базою даних
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Створюємо фабрику сесій — через неї будемо відкривати робочі сеанси
# для запису, читання або оновлення анкет у базі
SessionLocal = sessionmaker(bind=engine)


# Базовий клас для всіх наших таблиць.
# SQLAlchemy бачить усі таблиці, які наслідуються від цього класу
class Base(DeclarativeBase):
    pass


# Описуємо таблицю 'cvs' у вигляді класу Python (ORM-модель)
class CV(Base):
    # Назва таблиці всередині самої бази даних
    __tablename__ = "cvs"

    # Унікальний ID чату в Telegram (первинний ключ).
    # Використовуємо BigInteger, бо ID нових користувачів у Telegram перевищують ліміт звичайного Integer
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Короткі текстові поля з обмеженням до 100 символів (обов'язкова вимога для String у PostgreSQL)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(100))

    # Довгі текстові поля без жорсткого обмеження довжини (тип Text)
    contacts: Mapped[str] = mapped_column(Text)
    skills: Mapped[str] = mapped_column(Text)
    experience: Mapped[str] = mapped_column(Text)


# Функція ініціалізації бази даних
def init_db():
    # Перевіряє базу і створює всі таблиці, описані через Base, якщо їх ще немає
    Base.metadata.create_all(bind=engine)


# Тестовий блок: спрацює ТІЛЬКИ якщо запустити цей файл напряму
if __name__ == "__main__":
    init_db()
    print("✅ Базу даних та таблицю 'cvs' успішно створено!")
# Hw11_web_FastAPI
# Hw12_web_FastAPI
# Hw13_web_FastAPI

REST API for contacts storage and managemant

Мета цього домашнього завдання — створити REST API для зберігання та управління контактами. API повинен бути побудований з використанням інфраструктури FastAPI та використовувати SQLAlchemy для управління базою даних.

Контакти повинні зберігатися в базі даних та містити в собі наступну інформацію:
    Ім'я
    Прізвище
    Електронна адреса
    Номер телефону
    День народження
    Додаткові дані (необов'язково)

API повинен мати можливість виконувати наступні дії:
    Створити новий контакт
    Отримати список всіх контактів
    Отримати один контакт за ідентифікатором
    Оновити існуючий контакт
    Видалити контакт

На придачу до базового функціоналу CRUD API також повинен мати наступні функції:
    Контакти повинні бути доступні для пошуку за іменем, прізвищем чи адресою електронної пошти (Query).
    API повинен мати змогу отримати список контактів з днями народження на найближчі 7 днів.

Загальні вимоги
    Використання фреймворку FastAPI для створення API
    Використання ORM SQLAlchemy для роботи з базою даних
    В якості бази даних слід використовувати PostgreSQL.
    Підтримка CRUD операцій для контактів
    Підтримка зберігання дати народження контакту
    Надання документів для API
    Використання модуля перевірки достовірності даних Pydantic



Виконано:
Первинне налаштування структури папок
Створення класу моделі контактів
Асинхронне підключення до БД PostgreSQL
Асинхронне підключення Alembic

Виконання міграцій:
 alembic init migration
 -- редагування файлу env.py для підключення до БД
 -- редагування файлу env.py і зміна для роботи у асинхронному режимі
 alembic revision --autogenerate -m 'Init'

Ствонення роутерів:
-- створення шляхів у src/routes/contacts.py
-- підключення роутерів до застосунку шляхом імпорту шляхів у файл main.py

Реалізація роботи репозиторія із БД:
uvicorn main:app --reload
http://localhost:8000/docs

Додано  /api/healthchecker у файл main.py

Додавання можливості валідації за допомогою Pydantic:
-- формування схем створення і оновлення у файлі src/schemas/contact.py

Реалізація всіх основних функцій для операцій роботи із БД у src/repository/contacts.py відповідно до асинхронних функцій із src/routes/contacts.py

Наповнення роботи шляхів у src/routes/contacts.py



# Hw12_web_FastAPI
Authentication and authorisation addition to application Hw11_web_FastAPI

Домашнє завдання #12

У цьому домашньому завданні ми продовжуємо допрацьовувати наш REST API застосунок із домашнього завдання 11.
Завдання

    реалізуйте механізм аутентифікації в застосунку;
    реалізуйте механізм авторизації за допомогою JWT токенів, щоб усі операції з контактами проводились лише зареєстрованими користувачами;
    користувач має доступ лише до своїх операцій з контактами;

Загальні вимоги

-При реєстрації, якщо користувач вже існує з таким email, сервер поверне помилку HTTP 409 Conflict;

    Сервер хешує пароль і не зберігає його у відкритому вигляді в базі даних;
    У разі успішної реєстрації користувача сервер повинен повернути HTTP статус відповіді 201 Created та дані нового користувача;
    Для всіх операцій POST створення нового ресурсу, сервер повертає статус 201 Created;
    При операції POST - аутентифікація користувача, сервер приймає запит із даними користувача (email, пароль) у тілі запиту;
    Якщо користувач не існує або пароль не збігається, повертається помилка HTTP 401 Unauthorized;
    механізм авторизації за допомогою JWT токенів реалізований парою токенів: токена доступу access_token і токен оновлення refresh_token;


Виконано:
бібліотека JWT (jwt.io):
poetry add python-jose[cryptography]

Бібліотека для шифрування пароля (passlib.readthedocs.io):
bcrypt - функція алгоритму шифрування

Створення моделей користувачів у src/entity/models.py
створення другої міграції і виконання:
alembic revision --autogenerate -m "add table users"

створення файлів роутера:
src/routes/auth.py (не зовсім правильно)
створення файлу репозиторію:
src/repository/users.py (назва users.py, оскільки робота у репозиторії із сущностями, що знаходяться у БД - таблицею users)

додавання відповідних шляхів для автентифікації у main.py

Створення файлу сервісів аутентифікації (Аутентифікація та створення токенів​)
src/services/auth.py
додано бібліотеку:
poetry add passlib[bcrypt]


створення функції отримання користувача за email у файлі: src/repository/users.py 
Створення шляхів signup і login у файлі: src/routes/auth.py
Додавання сервісу gravatar.com:
poetry add libgravatar

Робота у Postman:
прописування токенів

Зазначення у маршрутах файлу src/routes/contacts.py залежності, що дозволяє працювати із маршрутами лише зареєстрованим користувачам: 
user: User = Depends(auth_service.get_current_user)


Імпорт HTTPBearer у src/routes/auth.py і робота із кастомним токеном:
get_refresh_token = HTTPBearer()
який дістає токен із запиту, при цьому якщо все добре - повертає credentials (властивості)
Додавання get_refresh_token до шляху @router.get('/refresh_token') у функцію HTTPAuthorizationCredentials = Security(get_refresh_token)


Визначення ролей і їх призначення через Depends() (або Security())

створення нового сервісу src/services/role.py
- додавання у src/entity/models.py для користувачів нових ролей
class Role(Enum.enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

створення міграції
редагування файлу міграції
            def upgrade() -> None:
                # ### commands auto generated by Alembic - please adjust! ###
                op.execute("CREATE TYPE role as ENUM('admin', 'moderator', 'user')")
                op.add_column('users', sa.Column('role', sa.Enum('admin', 'moderator', 'user', name='role'), nullable=True))
                # ### end Alembic commands ###

            def downgrade() -> None:
                # ### commands auto generated by Alembic - please adjust! ###
                op.drop_column('users', 'role')
                op.execute("DROP TYPE role")
                # ### end Alembic commands ###
проведення міграцій
присвоєння існуючим користувачам ролей напряму у БД


Заповнення файлу src/services/role.py
Створення класу RoleAccess

Створення об'єкту: access_to_rote_all = RoleAccess([Role.admin, Role.moderator])
у файлі: src/routes/contacts.py
Який буде спрацьовувати і попускати лише тих користувачів, ролі яких співпадають
У декораторі прописуються ролі для кожної із операцій:
dependencies=[Depends(access_to_rote_all)]



Домашнє завдання №13
Перша частина

У цьому домашньому завданні ми продовжуємо доопрацьовувати застосунок REST API із домашнього завдання 12.

Завдання

    Реалізуйте механізм верифікації електронної пошти зареєстрованого користувача;
    Обмежуйте кількість запитів до своїх маршрутів контактів. Обов’язково обмежте швидкість - створення контактів для користувача;
    Увімкніть CORS для свого REST API;
    Реалізуйте можливість оновлення аватара користувача. Використовуйте сервіс Cloudinary;

Загальні вимоги

    Усі змінні середовища повинні зберігатися у файлі .env. Всередині коду не повинно бути конфіденційних даних у «чистому» вигляді;
    Для запуску всіх сервісів і баз даних у застосунку використовується Docker Compose;

Додаткове завдання

    Реалізуйте механізм кешування за допомогою бази даних Redis. Виконайте кешування поточного користувача під час авторизації;
    Реалізуйте механізм скидання паролю для застосунку REST API;

Друга частина

У цьому домашньому завданні необхідно доопрацювати застосунок Django із домашнього завдання 10.

Завдання

    Реалізуйте механізм скидання паролю для зареєстрованого користувача;
    Усі змінні середовища повинні зберігатися у файлі .env та використовуватися у файлі settings.py;



1. Додавання поля для користувача у файлі src/entity/models.py:
confirmed = Column(Boolean, default=False, nullable=True)
проведення міграції
alembic revision --autogenerate -m "add user verification"
alembic upgrade head

Редагування src/routes/auth.py із додаванням перевірки під час логіну, чи верифікований користувач
Додавання BackgroundTasks 

створення функції верифікації користувача у src/repository/users.py
async def confirmed_email(email: str, db: AsyncSession)

додавання до роутів запиту на відправку листа:
bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

Створення src/services/email.py для надсилання email
src/services/templates/verify_email.html

Створення обробки маршруту <a href="{{host}}api/auth/confirmed_email/{{token}}">
Додавання     async def get_email_from_token(self, token: str):


2. Створення сервісу повторної відправки листа для верифікації
додавання схеми у src/schemas/user.py
додавання маршруту у src/routes/auth.py



3. Створення і редагування docker-compose.yml
Найпоширеніші команди для роботи з файлом docker-compose.yml:

    docker-compose up – запуск служб, визначених у файлі docker-compose.yml. Ця команда створить і запустить контейнери для кожного сервісу, а також створить мережу для взаємодії контейнерів.
    docker-compose down – зупинити і видалити контейнери, мережі і томи, створені командою docker-compose up.
    docker-compose ps – виведе список контейнерів, створених docker-compose up, а також їхній статус та іншу інформацію.
    docker-compose logs – перегляд логів контейнерів, створених docker-compose up.
    docker-compose exec <ім’я служби> <команда> – виконати команду в запущеному контейнері, створеному docker-compose up. Наприклад, docker-compose exec redis redis-cli запустить команду redis-cli в контейнері redis.
    docker-compose build – перебудувати образи, визначені у файлі docker-compose.yml. Це може бути корисно, якщо ви внесли зміни до своїх сервісів і хочете переконатися, що образи актуальні.


Запуск сервісу docker compose:
docker compose up -d


4. Налаштування dotenv
poetry add python-dotenv
.env

Налаштування redis
poetry add redis


5. Обмеження кількості запитів
poetry add fastapi-limiter
src/routes/users.py

6. Додавання CORS

7. Додавання головної сторінки index.html

8. Cloudinary
poetry add cloudinary
додавання сервісу

9. Додавання кешування за допомогою redis у src/services/auth.py



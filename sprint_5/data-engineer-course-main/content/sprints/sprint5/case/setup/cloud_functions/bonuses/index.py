import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import psycopg
from psycopg import Connection
from psycopg.rows import class_row
from pydantic import BaseModel

OUTBOX_TTL_DAYS = 32


class PgConnect:
    def __init__(self, host: str, port: int, db_name: str, user: str, pw: str) -> None:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pw = pw

    def url(self) -> str:
        return """
            host={host}
            port={port}
            dbname={db_name}
            user={user}
            password={pw}
            target_session_attrs=read-write
            sslmode=require
        """.format(
            host=self.host,
            port=self.port,
            db_name=self.db_name,
            user=self.user,
            pw=self.pw)

    def client(self):
        return psycopg.connect(self.url())


class User(BaseModel):
    id: int
    order_user_id: str


def get_user(conn: Connection, user_id: str) -> User:
    user = load_user(conn, user_id)
    if user:
        return user

    init_user(conn, user_id)

    user = load_user(conn, user_id)
    if not user:
        raise KeyError(f"Cannot init user for {user_id}.")

    return user


def init_user(conn: Connection, user_id: str):
    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO users(order_user_id)
                        VALUES (%(id)s);
                    """,
                    {"id": user_id},
                    )


def load_user(conn: Connection, user_id: str) -> Optional[User]:
    with conn.cursor(row_factory=class_row(User)) as cur:
        cur.execute("""
                        SELECT
                            u.id            AS id,
                            u.order_user_id AS order_user_id
                        FROM users AS u
                        WHERE u.order_user_id = %(id)s;
                    """,
                    {"id": user_id},
                    )
        obj = cur.fetchone()
    return obj


class UserRank(BaseModel):
    id: int
    user_id: str
    rank_id: str
    rank_name: str
    rank_award: float


def send_rank_event(conn: Connection, old_rank: Optional[UserRank], new_rank: UserRank) -> None:
    rank_changed = not old_rank or old_rank.rank_id != new_rank.rank_id
    if not rank_changed:
        return

    rank_event = {
        "user_id": new_rank.user_id,
        "rank_id": new_rank.rank_id,
        "rank_name": new_rank.rank_name,
        "rank_award": new_rank.rank_award
    }

    with conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO outbox(event_ts, event_type, event_value)
                VALUES(%(event_ts)s, %(event_type)s, %(event_value)s);
            """,
            {
                "event_ts": datetime.utcnow(),
                "event_type": "user_rank",
                "event_value": json.dumps(rank_event)
            }
        )


def get_user_rank(conn: Connection, user_id: int) -> UserRank:
    cur_rank = load_user_rank(conn, user_id)
    if cur_rank:
        return cur_rank

    init_rank(conn, user_id)

    cur_rank = load_user_rank(conn, user_id)
    if not cur_rank:
        raise KeyError(f"Cannot init rank for {user_id}.")

    send_rank_event(conn, None, cur_rank)
    return cur_rank


def init_rank(conn: Connection, user_id: int):
    with conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO user_ranks(user_id, rank_id)
                VALUES (%(id)s, 0);
            """,
            {"id": user_id},
        )


def load_user_rank(conn: Connection, user_id: int) -> Optional[UserRank]:
    with conn.cursor(row_factory=class_row(UserRank)) as cur:
        cur.execute("""
                        SELECT
                            u.id            AS id,
                            u.user_id       AS user_id,
                            r.id            AS rank_id,
                            r.name          AS rank_name,
                            r.bonus_percent AS rank_award
                        FROM user_ranks as u
                            INNER JOIN ranks AS r
                                ON u.rank_id = r.id
                        WHERE u.user_id = %(id)s;
                    """,
                    {"id": user_id},
                    )
        obj = cur.fetchone()
    return obj


class UserBalance(BaseModel):
    id: int
    user_id: int
    balance: float


def get_user_balance(conn: Connection, user_id: int) -> UserBalance:
    cur_balance = load_user_balance(conn, user_id)
    if cur_balance:
        return cur_balance

    init_balance(conn, user_id)
    cur_balance = load_user_balance(conn, user_id)
    if not cur_balance:
        raise KeyError(f"Cannot init balance for {user_id}.")

    return cur_balance


def init_balance(conn: Connection, user_id: int):
    with conn.cursor() as cur:
        cur.execute("""
                        INSERT INTO bonus_balance(user_id, balance)
                        VALUES (%(id)s, 0);
                    """,
                    {
                        "id": user_id
                    },
                    )


def load_user_balance(conn: Connection, user_id: int) -> Optional[UserBalance]:
    with conn.cursor(row_factory=class_row(UserBalance)) as cur:
        cur.execute("""
                        SELECT id, user_id, balance
                        FROM bonus_balance
                        WHERE user_id = %(id)s;
                    """,
                    {"id": user_id},
                    )
        obj = cur.fetchone()
        print(f"type of obj: {type(obj)}")
        return obj


def fix_payment(conn: Connection,
                user_id: int,
                order_id: str,
                product_id: str,
                product_price: float,
                product_count: float,
                order_ts: datetime,
                bonus_payment: float,
                bonus_grant: float,
                order_sum: float
                ) -> None:

    with conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO bonus_transactions(
                    user_id,
                    order_id,
                    product_id,
                    product_price,
                    product_count,
                    order_ts,
                    payment_sum,
                    granted_sum,
                    order_sum)
                VALUES(
                    %(user_id)s,
                    %(order_id)s,
                    %(product_id)s,
                    %(product_price)s,
                    %(product_count)s,
                    %(order_ts)s,
                    %(bonus_payment)s,
                    %(bonus_grant)s,
                    %(order_sum)s);
            """,
            {
                "user_id": user_id,
                "order_id": order_id,
                "product_id": product_id,
                "product_price": product_price,
                "product_count": product_count,
                "order_ts": order_ts,
                "bonus_payment": bonus_payment,
                "bonus_grant": bonus_grant,
                "order_sum": order_sum
            }
        )


def update_current_rank(conn: Connection, user_rank: UserRank, min_date: datetime):
    with conn.cursor() as cur:
        cur.execute(
            """
                ;WITH new_rank_sum AS (
                    SELECT user_id, SUM(order_sum) AS paid_sum
                    FROM bonus_transactions
                    WHERE user_id = %(user_id)s AND order_ts > %(min_date)s
                    GROUP BY user_id
                ),
                new_rank AS (
                    SELECT user_id, rank_id
                    FROM (
                        SELECT
                            s.user_id   AS user_id,
                            r.id        AS rank_id,
                            ROW_NUMBER() OVER(PARTITION BY s.user_id ORDER BY r.min_payment_threshold ASC) AS rn
                        FROM new_rank_sum AS s
                            CROSS JOIN ranks AS r
                        WHERE s.paid_sum >= r.min_payment_threshold
                    ) AS t
                )
                UPDATE user_ranks AS ur
                SET rank_id = nr.rank_id
                FROM new_rank AS nr
                WHERE nr.user_id = ur.user_id AND nr.rank_id != ur.rank_id;
            """,
            {
                "user_id": user_rank.user_id,
                "min_date": min_date
            }
        )


def update_current_balance(conn: Connection, user_balance: UserBalance, bonus_payment: float, bonus_grant: float) -> None:
    balance_event = {
        "user_id": user_balance.user_id,
        "balance": user_balance.balance - bonus_payment + bonus_grant
    }

    with conn.cursor() as cur:
        cur.execute(
            """
                UPDATE bonus_balance
                SET balance = %(balance)s
                WHERE user_id = %(user_id)s;
            """,
            balance_event
        )

        cur.execute(
            """
                INSERT INTO outbox(event_ts, event_type, event_value)
                VALUES(%(event_ts)s, %(event_type)s, %(event_value)s);
            """,
            {
                "event_ts": datetime.utcnow(),
                "event_type": "user_balance",
                "event_value": json.dumps(balance_event)
            }
        )


class OrderItem:
    def __init__(self, json) -> None:
        self.id: str = json['id']
        self.name: str = json['name']
        self.price: float = json['price']
        self.quantity: int = json['quantity']

    def __str__(self) -> str:
        return f"{self.id};{self.name};{self.price};{self.quantity}"


class Order:
    def __init__(self, json: Dict) -> None:
        self.id = json['id']
        self.date = datetime.strptime(json['order_ts'], "%Y-%m-%d %H:%M:%S")
        self.user_id = json['user_id']
        self.cost = json['cost']
        self.status = json['status']
        self.order_items = [OrderItem(d) for d in json['items']]


def init_schema(conn: Connection):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                order_user_id text NOT NULL
            );

            GRANT SELECT ON public.users TO student;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ranks (
                id int NOT NULL PRIMARY KEY,
                name varchar(2048) NOT NULL,
                bonus_percent numeric(19, 5) NOT NULL DEFAULT 0 CHECK(bonus_percent >= 0),
                min_payment_threshold numeric(19, 5) NOT NULL DEFAULT 0 CHECK(bonus_percent >= 0)
            );

            GRANT SELECT ON public.ranks TO student;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ranks (
                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                user_id INT NOT NULL REFERENCES users(id),
                rank_id INT NOT NULL REFERENCES ranks(id)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS IDX_user_ranks__user_id ON user_ranks (user_id);
            CREATE INDEX IF NOT EXISTS IDX_user_ranks__rank_id ON user_ranks (rank_id);

            GRANT SELECT ON public.user_ranks TO student;
        """)

        cursor.execute("""
            ;WITH t_ranks_data AS (
                SELECT 0 AS rank_id, 'JUNIOR' AS name, 0.05 AS percentage, 0 AS threshold
                UNION ALL SELECT 1 AS rank_id, 'MIDDLE' AS name, 0.1 AS percentage, 5000 AS threshold
                UNION ALL SELECT 2 AS rank_id, 'SENIOR' AS name, 0.15 AS percentage, 15000 AS threshold
            )
            INSERT INTO ranks(id, name, bonus_percent, min_payment_threshold)
            SELECT rank_id, name, percentage, threshold
            FROM t_ranks_data AS t
            WHERE NOT EXISTS (
                SELECT 1/0
                FROM ranks AS r
                WHERE r.id = t.rank_id
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bonus_transactions (
                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                user_id INT NOT NULL REFERENCES users(id),
                order_id varchar NOT NULL,
                product_id varchar NOT NULL,
                product_price numeric(19, 5) NOT NULL DEFAULT 0 CHECK(product_price >= 0),
                product_count int NOT NULL DEFAULT 0 CHECK(product_count >= 0),
                order_ts timestamp NOT NULL,
                order_sum numeric(19, 5) NOT NULL DEFAULT 0 CHECK(payment_sum >= 0),
                payment_sum numeric(19, 5) NOT NULL DEFAULT 0 CHECK(payment_sum >= 0 AND payment_sum <= order_sum),
                granted_sum numeric(19, 5) NOT NULL DEFAULT 0 CHECK(granted_sum >= 0 AND granted_sum <= order_sum)
            );

            CREATE INDEX IF NOT EXISTS IDX_bonus_transactions__user_id__order_id ON bonus_transactions (user_id, order_id);
            CREATE INDEX IF NOT EXISTS IDX_bonus_transactions__order_id ON bonus_transactions (order_id);

            GRANT SELECT ON public.bonus_transactions TO student;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bonus_balance (
                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                user_id INT NOT NULL REFERENCES users(id),
                balance numeric(19, 5) NOT NULL DEFAULT 0 CHECK(balance >= 0)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS IDX_bonus_balance__user_id ON bonus_balance (user_id);

            GRANT SELECT ON public.bonus_balance TO student;
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outbox (
                id int NOT NULL PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                event_ts timestamp NOT NULL,
                event_type varchar NOT NULL,
                event_value text NOT NULL
            );

            CREATE INDEX IF NOT EXISTS IDX_outbox__event_ts ON outbox (event_ts);

            GRANT SELECT ON public.outbox TO student;
        """)

        cursor.execute(
            """
                DELETE FROM outbox
                WHERE event_ts < %(last_ts)s
            """,
            {
                "last_ts": datetime.utcnow() - timedelta(days=OUTBOX_TTL_DAYS)
            }
        )

        cursor.execute(
            """
                DELETE FROM bonus_transactions
                WHERE order_ts < %(delete_threshold)s
            """,
            {
                "delete_threshold": datetime.utcnow() - timedelta(days=OUTBOX_TTL_DAYS)
            }
        )

        conn.commit()


class ProductPayment:
    def __init__(self, item: OrderItem, balance: float, rank_award: float) -> None:
        self.product_id: str = item.id
        self.product_name: str = item.name
        self.price: float = item.price
        self.quantity: int = item.quantity

        self.product_cost = self.price * self.quantity
        self.bonus_payment = min(self.product_cost, balance)
        self.bonus_grant = round((self.product_cost - self.bonus_payment) * rank_award)


class OrderPayment:
    def __init__(self, user: User, order: Order, user_balance: UserBalance, user_rank: UserRank) -> None:
        self.user_id: int = user.id
        self.order_id: str = order.id
        self.order_date: datetime = order.date
        self.product_payments: List[ProductPayment] = []

        balance = user_balance.balance
        for it in order.order_items:
            prod = ProductPayment(it, balance, user_rank.rank_award)
            balance -= prod.bonus_payment
            self.product_payments.append(prod)

    def bonus_payment(self) -> float:
        return sum([p.bonus_payment for p in self.product_payments])

    def bonus_grant(self) -> float:
        return sum([p.bonus_grant for p in self.product_payments])


def send_payment_event(conn: Connection, order: OrderPayment) -> None:
    prods = []
    for p in order.product_payments:
        prods.append({
            "product_id": p.product_id,
            "product_name": p.product_name,
            "price": p.price,
            "quantity": p.quantity,
            "product_cost": p.product_cost,
            "bonus_payment": p.bonus_payment,
            "bonus_grant": p.bonus_grant
        })

    transaction_params = {
        "user_id": order.user_id,
        "order_id": order.order_id,
        "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "product_payments": prods
    }

    with conn.cursor() as cur:
        cur.execute(
            """
                INSERT INTO outbox(event_ts, event_type, event_value)
                VALUES(%(event_ts)s, %(event_type)s, %(event_value)s);
            """,
            {
                "event_ts": datetime.utcnow(),
                "event_type": "bonus_transaction",
                "event_value": json.dumps(transaction_params)
            }
        )


def run(db_connect: PgConnect, order: Order):

    with db_connect.client() as conn:
        init_schema(conn)

        user = get_user(conn, order.user_id)

        if order.status != "CLOSED":
            bonus_payment = 0
            bonus_grant = 0
        else:
            user_rank = get_user_rank(conn, user.id)
            user_balance = get_user_balance(conn, user.id)

            order_payment = OrderPayment(user, order, user_balance, user_rank)

            for payment in order_payment.product_payments:
                fix_payment(conn,
                            order_payment.user_id,
                            order_payment.order_id,
                            payment.product_id,
                            payment.price,
                            payment.quantity,
                            order_payment.order_date,
                            payment.bonus_payment,
                            payment.bonus_grant,
                            payment.product_cost)

            update_current_rank(conn, user_rank, order.date - timedelta(days=30))
            new_rank = get_user_rank(conn, user.id)
            send_rank_event(conn, user_rank, new_rank)

            bonus_payment = order_payment.bonus_payment()
            bonus_grant = order_payment.bonus_grant()

            update_current_balance(conn, user_balance, bonus_payment, bonus_grant)
            send_payment_event(conn, order_payment)

        conn.commit()

    return {
        'statusCode': 200,
        'body': {
            'bonus_payment_response': {
                'user_id': order.user_id,
                'bonus_payment': bonus_payment,
                'bonus_grant': bonus_grant
            }
        },
    }


def handler(event, context):
    req = json.loads(event['body'])['order_request']
    order = Order(req)

    host = str(os.getenv('PG_HOST'))
    port = int(str(os.getenv('PG_PORT')))
    db_name = str(os.getenv('PG_DATABASE_NAME'))
    user = str(os.getenv('PG_USER'))
    password = str(os.environ.get('PG_PASSWORD'))
    connector = PgConnect(host, port, db_name, user, password)

    resp = run(connector, order)

    return {
        'statusCode': 200,
        'body': {
            'event': resp
        },
    }

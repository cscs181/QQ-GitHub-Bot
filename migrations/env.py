from typing import cast

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.util import await_fallback
from sqlalchemy.ext.asyncio import AsyncEngine
from nonebot_plugin_orm import AlembicConfig, plugin_config

# Alembic Config 对象，它提供正在使用的 .ini 文件中的值。
config = cast(AlembicConfig, context.config)

# 默认 AsyncEngine
engine: AsyncEngine = config.attributes["engines"][""]

# 模型的 MetaData，用于 'autogenerate' 支持。
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = config.attributes["metadatas"][""]

# 其他来自 config 的值，可以按 env.py 的需求定义，例如可以获取：
# my_important_option = config.get_main_option("my_important_option")
# ... 等等。


def run_migrations_offline() -> None:
    """在“离线”模式下运行迁移。

    虽然这里也可以获得 Engine，但我们只需要一个 URL 即可配置 context。
    通过跳过 Engine 的创建，我们甚至不需要 DBAPI 可用。

    在这里调用 context.execute() 会将给定的字符串写入到脚本输出。
    """
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **plugin_config.alembic_context,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        **plugin_config.alembic_context,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在“在线”模式下运行迁移。

    这种情况下，我们需要为 context 创建一个连接。
    """
    async with engine.begin() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    await_fallback(run_migrations_online())

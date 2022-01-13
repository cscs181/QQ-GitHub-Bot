import pytest


@pytest.fixture(autouse=True)
async def load_plugins(nonebug_init):
    import nonebot
    from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_Adapter

    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11_Adapter)

    config = driver.config
    nonebot.load_all_plugins(set(config.plugins), set(config.plugin_dirs))

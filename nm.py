import asyncio

from dbus_next import BusType
from dbus_next.aio import MessageBus


NETWORK_MANAGER = "org.freedesktop.NetworkManager"
NETWORK_MANAGER_OBJECT = "/org/freedesktop/NetworkManager"
SETTINGS_OBJECT = "/org/freedesktop/NetworkManager/Settings"
SETTINGS_INTERFACE = "org.freedesktop.NetworkManager.Settings"
CONNECTION_INTERFACE = "org.freedesktop.NetworkManager.Settings.Connection"


async def get_connections(bus):
    print("Getting the connections...")
    settings_introspection = await bus.introspect(NETWORK_MANAGER, SETTINGS_OBJECT)
    settings_proxy = bus.get_proxy_object(
        NETWORK_MANAGER, SETTINGS_OBJECT, settings_introspection
    )
    settings = settings_proxy.get_interface(SETTINGS_INTERFACE)
    connections = await settings.call_list_connections()
    for connection in connections:
        connection_introspection = await bus.introspect(NETWORK_MANAGER, connection)
        connection_proxy = bus.get_proxy_object(
            NETWORK_MANAGER, connection, connection_introspection
        )
        settings_connection = connection_proxy.get_interface(CONNECTION_INTERFACE)
        connection_setting = await settings_connection.call_get_settings()

        con = connection_setting["connection"]
        print(f"-> {con['id'].value}: {con['uuid'].value} ({con['type'].value})")


async def get_state(bus):
    network_manager_introspection = await bus.introspect(
        NETWORK_MANAGER, NETWORK_MANAGER_OBJECT
    )
    network_manager_proxy = bus.get_proxy_object(
        NETWORK_MANAGER, NETWORK_MANAGER_OBJECT, network_manager_introspection
    )
    manager = network_manager_proxy.get_interface(NETWORK_MANAGER)
    state = await manager.call_state()
    print(f"NetworkManager state: {state}")
    for device in await manager.call_get_devices():
        print(device)


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    await get_state(bus)
    await get_connections(bus)


asyncio.get_event_loop().run_until_complete(main())

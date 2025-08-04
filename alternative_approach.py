# This is actually a different attempt, different from the one in aiolocust
# This is set up as a locustfile
from locust import User, events


@events.init.add_listener
def on_init(environment, **kwargs):
    # Set up the event loop

    import asyncio
    import gevent.selectors

    class EventLoop(asyncio.SelectorEventLoop):
        def __init__(self, environment):
            self.__environment = environment
            super().__init__(gevent.selectors.DefaultSelector())

        def run_forever(self):
            greenlet = self.__environment.runner.greenlet.spawn(super(EventLoop, self).run_forever)
            greenlet.join()

    loop = EventLoop(environment)
    environment.loop = loop
    asyncio.set_event_loop(loop)

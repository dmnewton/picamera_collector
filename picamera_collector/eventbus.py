import logging
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

import eventlet

class EventBus():
    def __init__(self):
      self.listeners = {}

    def listener_exists(self,event_name):
      return event_name in self.listeners

    def add_listener(self, event_name, listener):
      logger.info("adding %s",event_name)
      if not self.listeners.get(event_name, None):
          self.listeners[event_name] = {listener}
      else:
          self.listeners[event_name].add(listener)

    def remove_listener(self, event_name, listener):
        self.listeners[event_name].remove(listener)
        if len(self.listeners[event_name]) == 0:
          del self.listeners[event_name]

    def emit(self, event_name, *args):
        listeners = self.listeners.get(event_name, [])
        for listener in listeners:
            eventlet.spawn_n(listener,*args)
            eventlet.sleep()
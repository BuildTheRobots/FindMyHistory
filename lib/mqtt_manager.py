from paho.mqtt import client as mqtt_client
import json

class MqttManager(object):
    def __init__(self, ip, port, username=None, password=None):
        self._client = mqtt_client.Client()
        if (username is not None and password is not None):
            self._client.username_pw_set(username, password)
        self._client.connect(ip, port)
        self._client.loop_start()

    def publish(self, topic, payload):
        if isinstance(payload, dict):
            payload = json.dumps(payload)

            self._client.publish(
                topic=topic,
                payload=payload,
                qos=0,
                retain=True
            )

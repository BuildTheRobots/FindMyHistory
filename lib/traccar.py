import requests


class Traccar(object):
    class LatestUpdate(object):
        def __init__(self, timestamp: int, latest_traccar: bool) -> None:
            self.timestamp = timestamp
            self.latest_traccar = latest_traccar

    def __init__(self, url):
        self._url = url
        self._updates: dict[str, self.LatestUpdate] = {}

    def _find_some_id(self, data) -> str:
        if data["serialNumber"] != "NULL":
            return data["serialNumber"]
        if data["identifier"] != "NULL":
            return data["identifier"]
        if data["deviceDiscoveryId"] != "NULL":
            return data["deviceDiscoveryId"]
        if data["id"] != "NULL":
            return data["id"]

        raise Exception("Found no valid identifier to use in your device' data.")

    def send(self, data) -> tuple[bool, str]:
        timestamp = data["location|timeStamp"]
        id = self._find_some_id(data)
        lastupdate = self._updates.get(id, self.LatestUpdate("NULL", False))

        if timestamp == "NULL":
            # ignore data without timestamp
            return (lastupdate.latest_traccar, id)

        if lastupdate.timestamp == timestamp:
            # ignore when timestamp havent changed since last time
            return (lastupdate.latest_traccar, id)

        formdata = {
            "id": id,
            "timestamp": int(timestamp / 1000),
            "lat": data["location|latitude"],
            "lon": data["location|longitude"],
            "accuracy": data["location|horizontalAccuracy"],
            "positiontype": data["location|positionType"],
            "devicedisplayname": data["deviceDisplayName"],
            "devicemodel": data["deviceModel"],
            "name": data["name"],
        }

        result = requests.post(self._url, data=formdata, timeout=5)
        self._updates[id] = self.LatestUpdate(timestamp, result.ok)
        return (result.ok, formdata["id"])

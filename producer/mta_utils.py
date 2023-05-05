from datetime import datetime
import datetime
from zoneinfo import ZoneInfo

def map_schedule_relationship(r):
    if r == 0:
        return "SCHEDULED"
    elif r == 1:
        return "ADDED"
    elif r == 2:
        return "UNSCHEDULED"
    elif r == 3:
        return "CANCELED"

    return None


def map_stop_status(r):
    if r == 0:
        return "INCOMING_AT"
    elif r == 1:
        return "STOPPED_AT"
    elif r == 2:
        return "IN_TRANSIT_TO"

    return None


def map_congestion_lvl(r):
    if r == 0:
        return "UNKNOWN_CONGESTION_LEVEL"
    elif r == 1:
        return "RUNNING_SMOOTHLY"
    elif r == 2:
        return "STOP_AND_GO"
    elif r == 3:
        return "CONGESTION"
    elif r == 4:
        return "SEVERE_CONGESTION"

    return None


def map_occupancy_status(r):
    if r == 0:
        return "EMPTY"
    elif r == 1:
        return "MANY_SEATS_AVAILABLE"
    elif r == 2:
        return "FEW_SEATS_AVAILABLE"
    elif r == 3:
        return "STANDING_ROOM_ONLY"
    elif r == 4:
        return "CRUSHED_STANDING_ROOM_ONLY"
    elif r == 5:
        return "FULL"
    elif r == 6:
        return "NOT_ACCEPTING_PASSENGERS"

    return None


def parse_vehicle_entity(entity, ref=None):
    if not entity.HasField("vehicle"):
        return None

    vehicle_ev = {}
    v = entity.vehicle
    vehicle_ev["entity_id"] = entity.id
    # trip descriptor
    trip_desc = {}

    trip_desc["trip_id"] = v.trip.trip_id
    trip_desc["route_id"] = v.trip.route_id
    trip_desc["route_long_name"] = ref.lookup_route(v.trip.route_id, "route_long_name")
    trip_desc["direction_id"] = v.trip.direction_id
    trip_time = datetime.datetime.strptime(
        f"{v.trip.start_date} {v.trip.start_time}", "%Y%m%d %H:%M:%S"
    )
    trip_time = trip_time.replace(tzinfo=ZoneInfo("US/Eastern"))

    trip_desc["start_time"] = trip_time.astimezone(tz=ZoneInfo("utc")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    trip_desc["schedule_relation"] = map_schedule_relationship(
        v.trip.schedule_relationship
    )
    vehicle_ev["trip"] = trip_desc
    # vehicle descriptor
    v_desc = {}
    v_desc["id"] = v.vehicle.id
    v_desc["label"] = v.vehicle.label
    v_desc["license_plate"] = v.vehicle.license_plate
    vehicle_ev["vehicle"] = v_desc

    # position
    pos = {}
    pos["lon"] = v.position.longitude
    pos["lat"] = v.position.latitude
    pos["bearing"] = v.position.bearing
    pos["speed"] = v.position.speed
    pos["odometer"] = v.position.odometer
    vehicle_ev["position"] = pos

    # status
    vehicle_ev["stop_id"] = v.stop_id
    vehicle_ev["stop_name"] = ref.lookup_stop(v.stop_id, "stop_name")
    vehicle_ev["stop_lon"] = ref.lookup_stop(v.stop_id, "stop_lon")
    vehicle_ev["stop_lat"] = ref.lookup_stop(v.stop_id, "stop_lat")
    vehicle_ev["current_status"] = map_stop_status(v.current_status)
    vehicle_ev["pos_timestamp"] = datetime.datetime.fromtimestamp(v.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    vehicle_ev["congestion_level"] = map_congestion_lvl(v.congestion_level)
    vehicle_ev["occupancy_status"] = map_occupancy_status(v.occupancy_status)

    return vehicle_ev

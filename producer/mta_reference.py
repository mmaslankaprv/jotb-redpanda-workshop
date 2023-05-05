import os
import sys

class MTAReference:
    def __init__(self, base_dir):
        if not os.path.isdir(base_dir):
            sys.exit(f"Reference data directory '{base_dir}' does not exist")
        self.routes = self._load_ref(f"{base_dir}/routes.txt")
        self.stops = self._load_ref(f"{base_dir}/stops.txt")
        self.stops = self._load_ref(f"{base_dir}/stops.txt")

    # Load reference data
    # http://web.mta.info/developers/data/nyct/subway/google_transit.zip
    def _load_ref(self, file):
        ref = {}
        with open(file, mode="r") as ref_file:
            header = [v.strip() for v in ref_file.readline().split(",")]
            for row in ref_file.readlines():
                data = [v.strip() for v in row.split(",")]
                ref[data[0]] = {k: v for k, v in zip(header, data)}
        print(f"Loaded {len(ref)} entries from reference file: {file}")
        return ref

    # Lookup reference data
    def _lookup(self, ref, key, field):
        if not isinstance(ref, dict):
            return None
        entry = dict(ref).get(key, None)
        if not isinstance(entry, dict):
            return None
        value = dict(entry).get(field, None)
        return value

    def lookup_route(self, key, field):
        return self._lookup(self.routes, key, field)

    def lookup_stop(self, key, field):
        return self._lookup(self.stops, key, field)

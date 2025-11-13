import json
import typing
from collections import defaultdict

import av

def gsi_dump(dump_path):
    with open(dump_path, 'rb') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            gsi_dict = json.loads(line)
            yield gsi_dict

def process_condition(gsi: dict) -> bool:
    return gsi["allplayers"]["76561198240027748"]["state"]["round_kills"] == 1

def find_gsi_numbers(cond: typing.Callable, gsi_dump: typing.Iterable) -> list[int]:
    numbers = []
    previous_state = False
    for gsi in gsi_dump:
        current_state = cond(gsi)
        if not previous_state and current_state:
            numbers.append(gsi["gsi_number"])
        previous_state = current_state
    return numbers

def sync_video(
        gsi_dump: typing.Iterable,
        video_path: str,
        sync_gsi_number: int,
        sync_frame_number: int,
) -> tuple[dict, float]:
    container = av.open(video_path)
    stream = container.streams.video[0]
    timestamps_sets = defaultdict(list)
    for gsi in gsi_dump:
        ts = gsi["provider"]["timestamp"]
        timestamps_sets[ts].append(gsi)

    gsi2ts = {}
    for ts, gsi_records in timestamps_sets.items():
        min_gsi_number = min(gr["gsi_number"] for gr in gsi_records)
        for gsi_record in gsi_records:
            ts = gsi_record["provider"]["timestamp"]
            ts += (gsi_record["gsi_number"] - min_gsi_number) / len(gsi_records)
            gsi2ts[gsi_record.pop("gsi_number")] = (ts, gsi_record)

    t0 = 0
    for i, frame in enumerate(container.decode(stream)):
        if i == sync_frame_number:
            t0 = frame.time
            break

    t_delta = t0 - gsi2ts[sync_gsi_number][0]
    framerate = float(stream.average_rate)
    frame2gsi = {}
    last_frame = stream.frames
    for gsi_number, (ts, gsi_record) in gsi2ts.items():
        frame_number = int((ts + t_delta) * framerate)
        if 0 <= frame_number <= last_frame:
            frame2gsi[frame_number] = gsi_record
    return frame2gsi, framerate



def build_synced_dump_json(frame2gsi: dict, result_path: str, framerate) ->  None:
    data = {
        "fps": framerate,
        "events": [
            {"frame": frame, "payload": payload}
            for frame, payload in frame2gsi.items()
        ]
    }
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)




if __name__ == '__main__':
    DUMP_PATH = r'./dump.ndjson'
    VIDEO_PATH = r'C:\Users\ilya\Videos\trimed.mp4'
    NEW_DUMP_PATH = r'./dump_sync.ndjson'
    SYNC_FRAME = 1958

    #Find some gsi records for sync
    numbers = find_gsi_numbers(process_condition, gsi_dump(DUMP_PATH))
    print(f"Candidate frames for synchronization: {numbers}")
    sync_gsi_number = numbers[0]
    print(f"Synchronization gsi number: {sync_gsi_number}")
    frame2gsi, framerate = sync_video(
        gsi_dump(DUMP_PATH),
        VIDEO_PATH,
        sync_gsi_number,
        SYNC_FRAME,
    )
    build_synced_dump_json(frame2gsi, NEW_DUMP_PATH, framerate)

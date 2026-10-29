"""Bounded fixed-frame receiver core; adapters supply all I/O and time."""
import hashlib
FRAME=b'FIRETABS_ACM_STATUS_V1\nSOURCE_SETUP=complete\nHOST_RECEIPT=unverified\nEND\n'

def receive(read,now,pause,*,timeout=1.0,max_attempts=128):
    if not 0<timeout<=5 or not 1<=max_attempts<=256:
        raise ValueError('invalid bounded capture policy')
    start=now();deadline=start+timeout;data=bytearray()
    for attempt in range(max_attempts):
        if now()>=deadline:raise TimeoutError('status frame deadline')
        try:chunk=read(len(FRAME)-len(data)+1)
        except InterruptedError:continue
        except BlockingIOError:
            pause(min(0.01,max(0,deadline-now())))
            continue
        if now()>=deadline:raise TimeoutError('late read cannot qualify frame')
        if not isinstance(chunk,bytes) or not chunk:raise ValueError('invalid/EOF read before complete frame')
        if len(chunk)>len(FRAME)-len(data)+1:raise ValueError('read callback exceeded requested bound')
        data.extend(chunk)
        if not FRAME.startswith(data):raise ValueError('unexpected/trailing status data')
        if data==FRAME:
            return {'frame_observed':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                    'attempts':attempt+1,'boot_qualified':False,'runtime_qualified':False,'raw':bytes(data)}
    raise TimeoutError('status frame attempt budget')

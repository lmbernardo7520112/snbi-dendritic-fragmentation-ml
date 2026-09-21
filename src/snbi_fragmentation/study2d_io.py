"""Study2-D TRAIN-only directed cache reads; no decoder or whole-file hash."""
from copy import deepcopy
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

POSITIVE = 'data/derived/study2b/multimodal_patches_uint8.bin'
BACKGROUND = 'data/derived/study2c/cachetrain_dev.bin'
FILES = {POSITIVE: 139425000, BACKGROUND: 73827650}
ROW_BYTES = 8450
CHANNEL_BYTES = 4225

class TrainAccessError(ValueError):
    """Any failed admission permanently closes this access instance."""

def require(condition, message):
    if not condition:
        raise TrainAccessError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def is_hex(value, size):
    return type(value) is str and len(value)==size and all(c in '0123456789abcdef' for c in value)

def validate_rows(rows):
    require(type(rows) is list and bool(rows), 'explicit nonempty TRAIN allowlist required')
    ids=set(); locations=set(); groups={}
    for row in rows:
        require(type(row) is dict and row.get('split')=='TRAIN', 'DEV/TEST/unknown split forbidden')
        label=row.get('label'); tier=row.get('tier'); kind=row.get('kind')
        require(type(label) is int and label in (0,1), 'binary int label required')
        require((label,tier,kind) in {(1,'GOLD','positive'),(0,'BACKGROUND','background')}, 'SILVER/unlabeled forbidden')
        sid=row.get('sample_id'); gid=row.get('group_id'); acquisition=row.get('acquisition_id')
        require(type(sid) is str and sid and sid not in ids and type(gid) is str and gid, 'invalid/duplicate identity')
        require(acquisition in {'bottom_up_anti_parallel','top_down_parallel'}, 'unknown acquisition')
        require(gid not in groups or groups[gid]==(label,acquisition), 'group identity inconsistent')
        groups[gid]=(label,acquisition); ids.add(sid)
        s=row.get('storage')
        require(type(s) is dict, 'frozen row locator required')
        expected=POSITIVE if label else BACKGROUND
        require(s.get('path')==expected and type(s.get('expected_file_bytes')) is int and s['expected_file_bytes']==FILES[expected], 'container outside fixed allowlist')
        index=s.get('row_index')
        require(type(index) is int and index>=0 and (index+1)*ROW_BYTES<=FILES[expected], 'row index outside container')
        require(type(s.get('offset')) is int and s['offset']==index*ROW_BYTES, 'offset must equal exact row boundary')
        require(s.get('shape')==[2,65,65] and all(type(n) is int for n in s['shape']) and s.get('dtype')=='uint8', 'native uint8 shape required')
        require(all(is_hex(s.get(k),64) for k in ('pair_sha256','structural_patch_sha256','solutal_patch_sha256')), 'three row hashes required')
        if label:
            require(row.get('positive_row_index')==index and type(row.get('positive_row_index')) is int, 'positive locator changed')
            require(all(row.get(k)==s[k] for k in ('pair_sha256','structural_patch_sha256','solutal_patch_sha256')), 'positive provenance changed')
        require((expected,index) not in locations, 'duplicate physical row')
        locations.add((expected,index))
    return groups

def _open_file(root, relative):
    # Both relative paths are constants admitted above; walk without symlinks.
    root=Path(root)
    require(not root.is_symlink(), 'root symlink')
    descriptor=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        parts=PurePosixPath(relative).parts
        for part in parts[:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=descriptor)
            os.close(descriptor); descriptor=child
        return os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=descriptor)
    finally:
        os.close(descriptor)

def _fingerprint(fd):
    s=os.fstat(fd)
    require(stat.S_ISREG(s.st_mode), 'regular container required')
    return (s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

class TrainCorpusAccess:
    """Inert reader; load requires a receipt-bound controller grant first.

    The complete allowed row metadata is immutable inside the instance. No API
    accepts arbitrary offsets, arbitrary paths, another split, or a second load.
    Instrumentation measures application pread ranges, not kernel page caching.
    """
    def __init__(self, root, rows, grant=None, audit=None):
        require(audit is None or (type(audit) is dict and not audit), 'fresh audit required')
        self.root=root; self.rows=deepcopy(rows); self.grant=grant
        self.audit={} if audit is None else audit
        self.audit.update({'state':'NOT_USED','container_opens':0,'row_attempts':0,'rows_read':0,
            'bytes_read':0,'rows_authenticated':0,'TRAIN_GOLD_ROWS_READ':0,'TRAIN_BG_ROWS_READ':0,
            'DEV_GROUPS_READ':0,'TEST_GROUPS_READ':0,'DEV_ROWS_READ':0,'TEST_ROWS_READ':0,
            'TEST_CACHE_ROWS_READ':0,'TEST_FEATURES_COMPUTED':0,'EXPERIMENTAL_SOURCE_OPENS':0,
            'FFMPEG_RUNS':0,'ESM1_OPENS':0,'ESM2_OPENS':0,'ESM3_OPENS':0,'ESM4_OPENS':0,
            'ESM5_OPENS':0,'ESM6_OPENS':0,'pixels_written':0,'full_container_hashes':0,'access_records':[],
            'scope':'Only exact authorized TRAIN row pread ranges; no whole-container authentication or memory mapping.'})
        self.closed=False; self.used=False; self.fds={}

    def load(self):
        require(not self.closed and not self.used, 'reader already consumed')
        self.used=True
        try:
            require(callable(self.grant), 'controller grant required before paths')
            proof=self.grant('LOAD_TRAIN_ROWS',deepcopy(self.rows))
            require(type(proof) is dict and proof.get('authorized') is True
                and is_hex(proof.get('execution_receipt_sha256'),64)
                and is_hex(proof.get('method_freeze_sha'),40), 'valid receipt/head grant required')
            groups=validate_rows(self.rows)
            import numpy as np
            pairs=np.empty((len(self.rows),2,65,65),dtype=np.uint8)
            fps={}
            for i,row in enumerate(self.rows):
                s=row['storage']; path=s['path']
                if path not in self.fds:
                    fd=_open_file(self.root,path); self.fds[path]=fd
                    self.audit['container_opens']+=1
                    fps[path]=_fingerprint(fd)
                    require(fps[path][3]==FILES[path], 'container size changed')
                self.audit['row_attempts']+=1
                b=os.pread(self.fds[path],ROW_BYTES,s['offset'])
                self.audit['bytes_read']+=len(b)
                require(len(b)==ROW_BYTES, 'short row read')
                self.audit['rows_read']+=1
                self.audit['TRAIN_GOLD_ROWS_READ' if row['label'] else 'TRAIN_BG_ROWS_READ']+=1
                hashes={'pair_sha256':digest(b),'structural_patch_sha256':digest(b[:CHANNEL_BYTES]),
                        'solutal_patch_sha256':digest(b[CHANNEL_BYTES:])}
                require(all(hashes[k]==s[k] for k in hashes), 'row payload hash divergence')
                self.audit['rows_authenticated']+=1
                pairs[i]=np.frombuffer(b,dtype=np.uint8).reshape(2,65,65)
                self.audit['access_records'].append({'sample_id':row['sample_id'],'group_id':row['group_id'],
                    'path':path,'offset':s['offset'],'bytes':len(b),**hashes})
            for path,fd in self.fds.items():
                require(_fingerprint(fd)==fps[path], 'container changed during selected reads')
            self.audit.update(TRAIN_GROUPS_READ=len(groups),state='COMPLETED',receipt_sha256=proof['execution_receipt_sha256'])
            self.close()
            return pairs
        except BaseException:
            self.audit['state']='FAILED_CONSUMED'; self.close(); raise

    def close(self):
        for fd in self.fds.values(): os.close(fd)
        self.fds={}; self.closed=True
        self.audit['all_descriptors_closed']=True

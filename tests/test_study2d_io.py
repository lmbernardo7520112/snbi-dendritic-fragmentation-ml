"""Synthetic directed-read/firewall contracts; never real experimental paths."""
from copy import deepcopy
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from snbi_fragmentation import study2d_io as io

NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None

PAYLOADS=[bytes(8450),bytes([17])*8450]
def fixtures():
    rows=[]
    for i,label in enumerate((1,0)):
        b=PAYLOADS[i]; path=io.POSITIVE if label else io.BACKGROUND
        hashes={'pair_sha256':hashlib.sha256(b).hexdigest(),
            'structural_patch_sha256':hashlib.sha256(b[:4225]).hexdigest(),
            'solutal_patch_sha256':hashlib.sha256(b[4225:]).hexdigest()}
        row={'sample_id':f's{i}','group_id':f'g{i}','label':label,'split':'TRAIN',
            'tier':'GOLD' if label else 'BACKGROUND','kind':'positive' if label else 'background',
            'acquisition_id':'bottom_up_anti_parallel','storage':{'path':path,'row_index':3+i,
            'offset':(3+i)*8450,'shape':[2,65,65],'dtype':'uint8','expected_file_bytes':io.FILES[path],**hashes}}
        if label: row.update(positive_row_index=3,**hashes)
        rows.append(row)
    return rows

def grant(*args):
    return {'authorized':True,'execution_receipt_sha256':'a'*64,'method_freeze_sha':'b'*40}

class ExplodingRoot:
    def __fspath__(self): raise AssertionError('root accessed before denial')

class TrainIOTests(unittest.TestCase):
    def test_inert_constructor(self):
        with patch.object(io,'_open_file') as op:
            io.TrainCorpusAccess(ExplodingRoot(),fixtures())
        op.assert_not_called()

    def test_missing_grant_before_path(self):
        x=io.TrainCorpusAccess(ExplodingRoot(),fixtures())
        with self.assertRaises(io.TrainAccessError): x.load()
        self.assertEqual(x.audit['container_opens'],0)
        self.assertTrue(x.closed)

    def test_false_grant_before_path(self):
        x=io.TrainCorpusAccess(ExplodingRoot(),fixtures(),lambda *a:{'authorized':False})
        with self.assertRaises(io.TrainAccessError): x.load()

    def test_truthy_nonboolean_grant_denied(self):
        g=grant(); g['authorized']=1
        with self.assertRaises(io.TrainAccessError): io.TrainCorpusAccess(ExplodingRoot(),fixtures(),lambda *a:g).load()

    def test_invalid_receipt_before_path(self):
        g=grant(); g['execution_receipt_sha256']=''
        with self.assertRaises(io.TrainAccessError): io.TrainCorpusAccess(ExplodingRoot(),fixtures(),lambda *a:g).load()

    def check_mutation(self,change):
        rows=fixtures(); change(rows)
        with patch.object(io,'_open_file') as op:
            with self.assertRaises(io.TrainAccessError): io.TrainCorpusAccess(ExplodingRoot(),rows,grant).load()
        op.assert_not_called()

    def test_dev_denied(self): self.check_mutation(lambda r:r[0].update(split='DEVELOPMENT'))
    def test_test_denied(self): self.check_mutation(lambda r:r[0].update(split='TEST'))
    def test_silver_denied(self): self.check_mutation(lambda r:r[0].update(tier='SILVER'))
    def test_unlabeled_denied(self): self.check_mutation(lambda r:r[0].update(tier='PRE_FIRST'))
    def test_wrong_kind_denied(self): self.check_mutation(lambda r:r[0].update(kind='background'))
    def test_duplicate_id_denied(self): self.check_mutation(lambda r:r[1].update(sample_id='s0'))
    def test_conflicting_group_denied(self): self.check_mutation(lambda r:r[1].update(group_id='g0'))
    def test_mp4_denied(self): self.check_mutation(lambda r:r[0]['storage'].update(path='source.mp4'))
    def test_test_cache_denied(self): self.check_mutation(lambda r:r[1]['storage'].update(path='data/derived/study2c/cachetest.bin'))
    def test_bad_offset_denied(self): self.check_mutation(lambda r:r[0]['storage'].update(offset=0))
    def test_bool_index_denied(self): self.check_mutation(lambda r:r[0]['storage'].update(row_index=True))
    def test_bad_shape_denied(self): self.check_mutation(lambda r:r[0]['storage'].update(shape=[2,64,65]))
    def test_missing_hash_denied(self): self.check_mutation(lambda r:r[0]['storage'].pop('pair_sha256'))
    def test_row_out_of_extent_denied(self): self.check_mutation(lambda r:r[0]['storage'].update(row_index=16500,offset=16500*8450))
    def test_positive_locator_denied(self): self.check_mutation(lambda r:r[0].update(positive_row_index=4))
    def test_unknown_acquisition_denied(self): self.check_mutation(lambda r:r[0].update(acquisition_id='x'))

    def execute_mocked(self,rows=None,payloads=None,fingerprint_change=False):
        rows=fixtures() if rows is None else rows
        x=io.TrainCorpusAccess('/synthetic',rows,grant)
        def fingerprint(fd):
            size=io.FILES[io.POSITIVE if fd==10 else io.BACKGROUND]
            if fingerprint_change and x.audit['rows_read']==2: size+=1
            return (1,fd,33188,size,5,6)
        contexts=[patch.object(io,'_open_file',side_effect=[10,11]),patch.object(io,'_fingerprint',side_effect=fingerprint),
            patch.object(io.os,'pread',side_effect=PAYLOADS if payloads is None else payloads),patch.object(io.os,'close')]
        mocks=[c.start() for c in contexts]
        try:
            result=x.load()
            return x,result,mocks[2].call_args_list,mocks[3].call_args_list
        finally:
            for c in reversed(contexts): c.stop()

    @unittest.skipUnless(NUMPY_AVAILABLE, "optional NumPy unavailable; fully required by Study2-D scientific synthetic CI")
    def test_exact_directed_reads_and_hashes(self):
        x,arr,calls,closed=self.execute_mocked()
        self.assertEqual(arr.shape,(2,2,65,65)); self.assertEqual(str(arr.dtype),'uint8')
        self.assertEqual([c.args for c in calls],[(10,8450,25350),(11,8450,33800)])
        self.assertEqual(x.audit['bytes_read'],16900)
        self.assertEqual(x.audit['rows_authenticated'],2)
        self.assertEqual(x.audit['DEV_ROWS_READ'],0); self.assertEqual(x.audit['TEST_ROWS_READ'],0)
        self.assertEqual({c.args[0] for c in closed},{10,11})
        self.assertTrue((arr[1]==17).all())
        with self.assertRaises(io.TrainAccessError): x.load()

    @unittest.skipUnless(NUMPY_AVAILABLE, "optional NumPy unavailable; fully required by Study2-D scientific synthetic CI")
    def test_short_read_closes(self):
        with self.assertRaisesRegex(io.TrainAccessError,'short row'): self.execute_mocked(payloads=[b''])

    @unittest.skipUnless(NUMPY_AVAILABLE, "optional NumPy unavailable; fully required by Study2-D scientific synthetic CI")
    def test_hash_mismatch_closes(self):
        with self.assertRaisesRegex(io.TrainAccessError,'hash divergence'): self.execute_mocked(payloads=[bytes([1])*8450])

    @unittest.skipUnless(NUMPY_AVAILABLE, "optional NumPy unavailable; fully required by Study2-D scientific synthetic CI")
    def test_fingerprint_change_denied(self):
        with self.assertRaisesRegex(io.TrainAccessError,'changed during'): self.execute_mocked(fingerprint_change=True)

    def test_input_copy_immutable(self):
        rows=fixtures(); x=io.TrainCorpusAccess('/synthetic',rows,grant)
        rows[0]['split']='TEST'
        self.assertEqual(x.rows[0]['split'],'TRAIN')

    def test_symlink_file_denied(self):
        root=Path('.bootstrap-test-tmp/study2d-io-tests'); root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as t:
            target=Path(t)/'target'; target.write_bytes(b'synthetic')
            p=Path(t)/io.POSITIVE; p.parent.mkdir(parents=True); p.symlink_to(target.absolute())
            with self.assertRaises(OSError): io._open_file(t,io.POSITIVE)

    def test_symlink_directory_denied(self):
        root=Path('.bootstrap-test-tmp/study2d-io-tests'); root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as t:
            p=Path(t); (p/'actual').mkdir(); (p/'data').symlink_to((p/'actual').absolute(),target_is_directory=True)
            with self.assertRaises(OSError): io._open_file(t,io.POSITIVE)

    def test_no_decoder_or_bulk_reader_in_module(self):
        import ast
        tree=ast.parse(Path('src/snbi_fragmentation/study2d_io.py').read_text())
        calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
        self.assertNotIn('read',calls); self.assertNotIn('read_bytes',calls)
        self.assertNotIn('memmap',calls); self.assertNotIn('mmap',calls)
        self.assertIn('pread',calls)

if __name__=='__main__': unittest.main()

import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from usb_acm_frame import receive,FRAME
class Clock:
 def __init__(self):self.t=0
 def now(self):return self.t
 def pause(self,n):self.t+=n
class Receiver(unittest.TestCase):
 def test_complete_and_all_split_points(self):
  for split in range(1,len(FRAME)):
   chunks=[FRAME[:split],FRAME[split:]];c=Clock();r=receive(lambda n:chunks.pop(0),c.now,c.pause);self.assertTrue(r['frame_observed']);self.assertFalse(r['runtime_qualified']);self.assertEqual(r['raw'],FRAME)
 def test_failure_inputs(self):
  for b in [b'',b'x'+FRAME,FRAME+b'x',FRAME.replace(b'\n',b'\r\n'),b'END\n',b'x'*1024]:
   c=Clock()
   with self.assertRaises(ValueError):receive(lambda n:b,c.now,c.pause)
 def test_deadline_eintr_attempts_and_late_read(self):
  c=Clock()
  def again(n):raise BlockingIOError()
  with self.assertRaises(TimeoutError):receive(again,c.now,c.pause)
  c=Clock()
  def intr(n):raise InterruptedError()
  with self.assertRaises(TimeoutError):receive(intr,c.now,c.pause,max_attempts=5)
  def late(n):c.t+=2;return FRAME
  with self.assertRaises(TimeoutError):receive(late,c.now,c.pause)
 def test_recovery_after_transient_errors(self):
  chunks=[InterruptedError(),BlockingIOError(),FRAME];c=Clock()
  def read(n):
   v=chunks.pop(0)
   if isinstance(v,Exception):raise v
   return v
  self.assertEqual(receive(read,c.now,c.pause)['attempts'],3)
if __name__=='__main__':unittest.main()

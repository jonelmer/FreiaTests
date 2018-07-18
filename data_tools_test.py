import unittest
from data_tools import *
from pprint import pprint

length = 10

class TestFindNearestIndex(unittest.TestCase):

    def test_ints(self):
        array = range(length)
        
        for v in range(length):
            self.assertEqual(find_nearest_index(array, v), v)
            self.assertEqual(find_nearest_index(array, v, seq=True), v)
            
    def test_datetime(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(seconds=a) for a in range(length)]
        
        for v in range(length):
            val = now + datetime.timedelta(seconds=v)
            self.assertEqual(find_nearest_index(array, val), v)
            self.assertEqual(find_nearest_index(array, val, seq=True), v)
            
    def test_ints_half(self):
        array = range(length)
        
        for v in range(length):
            val = v+0.5
            self.assertEqual(find_nearest_index(array, val), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_datetime_half(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(seconds=a) for a in range(length)]
        
        for v in range(length):
            val = now + datetime.timedelta(seconds=v+0.5)
            self.assertEqual(find_nearest_index(array, val), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_ints_high(self):
        array = range(length)
        
        for v in range(length):
            val = v+0.99
            self.assertEqual(find_nearest_index(array, val), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_datetime_high(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(seconds=a) for a in range(length)]
        
        for v in range(length):
            val = now + datetime.timedelta(seconds=v+0.99)
            self.assertEqual(find_nearest_index(array, val), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_ints_low(self):
        array = range(length)
        
        for v in range(length):
            val = v+0.01
            self.assertEqual(find_nearest_index(array, val), v)
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), v)
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_datetime_low(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(seconds=a) for a in range(length)]
        
        for v in range(length):
            val = now + datetime.timedelta(seconds=v+0.01)
            self.assertEqual(find_nearest_index(array, val), v)
            self.assertEqual(find_nearest_index(array, val, seek=False), v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), v)
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), v)
            
    def test_ints_dbl(self):
        array = range(length)
        
        for v in range(round(length/2)):
            val = 2*v+0.5
            self.assertEqual(find_nearest_index(array, val), min(2*v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), 2*v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(2*v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), 2*v)
            
    def test_datetime_dbl(self):
        now = datetime.datetime.now()
        array = [now + datetime.timedelta(seconds=a) for a in range(length)]
        
        for v in range(round(length/2)):
            val = now + datetime.timedelta(seconds=2*v+0.5)
            self.assertEqual(find_nearest_index(array, val), min(2*v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False), 2*v)
            
            self.assertEqual(find_nearest_index(array, val, seq=True), min(2*v+1, length-1))
            self.assertEqual(find_nearest_index(array, val, seek=False, seq=True), 2*v)

            
class TestTruncate(unittest.TestCase):
    def setUp(self):
        self.data = dict(time=range(length), vals=range(length))
    
    def test_limits(self):
        limits = (1, 5)
        self.assertEqual(truncate(limits, self.data), dict(time=range(*limits), vals=range(*limits)))
        
    def test_key(self):
        limits = (0, length)
        self.assertRaises(KeyError, lambda: truncate(limits, self.data, 'foo'))
        
    def test_type(self):
        limits = (True, "foo")
        self.assertRaises(TypeError, lambda: truncate(limits, self.data))
        
    
class TestMovingAverage(unittest.TestCase):
    def test_func(self):
        factor = range(1, round(length/2))
        
        for f in factor:
            data = [1., ]
            data.extend([0., ] * (f-1))
            data = data * round(length/f)
                    
            expected = [1/f, ]*(length-1)
            result = moving_average(data, n=f)
            
            #print("\nData:     {}".format(data))
            #print("Expected: {}".format(expected))
            #print("Result:   {}".format(result))
            
            [self.assertEqual(e, r) for e, r in zip(expected, result)]
    
    
class TestGenerateMask(unittest.TestCase):
    def setUp(self):
        self.data = dict(
            masked=dict(time=np.arange(0, length, 0.1)),
            master=dict(time=np.arange(0, length, 1.0))
        )
        
        now = datetime.datetime.now()
        
        self.time = dict(
            masked=dict(time=[now + datetime.timedelta(seconds=s) for s in np.arange(0, length, 0.1)]),
            master=dict(time=[now + datetime.timedelta(seconds=s) for s in np.arange(0, length, 1.)])
        )
        
        self.pairs = (['masked', 'master'],)
                           
    def test_key(self):
        self.assertRaises(KeyError, lambda: generate_mask(self.pairs, (0,0), self.data, key='foo'))
    
    def test_type(self):
        self.assertRaises(TypeError, lambda: generate_mask(self.pairs, ("", False), self.data))
        
        # Test for inconsitent data/margin type (time or num)
        self.assertRaises(TypeError, lambda: generate_mask(self.pairs, (0, 0), self.time))
        self.assertRaises(TypeError, lambda:
                          generate_mask(self.pairs, (datetime.timedelta(seconds=-0.12), 
                                                             datetime.timedelta(seconds= 0.12)), self.data))
        
    def test_mask_num(self):
        result = generate_mask(self.pairs, (-0.12, 0.12), self.data)
        
        expected = [True, ] * 3
        expected.extend([False, ] * 7)
        expected = np.array(expected * length)[1:]
        
        #print()
        #print("Master:   {}".format(self.data['master']['time']))
        #print("Data:     {}".format(self.data['masked']['time']))
        #print("Expected: {}".format(expected))
        #print("Result:   {}".format(self.data['masked']['mask_master']))
        
        eq = [m==e for m, e in zip(self.data['masked']['mask_master'], expected)]
        
        self.assertEqual(all(eq), True)
        
    def test_mask_time(self):        
        result = generate_mask(self.pairs, (datetime.timedelta(seconds=-0.12), datetime.timedelta(seconds=0.12)), self.time)
        
        expected = [True, ] * 3
        expected.extend([False, ] * 7)
        expected = np.array(expected * length)[1:]
        
        #print()
        #print("Master:   {}".format(self.time['master']['time']))
        #print("Data:     {}".format(self.time['masked']['time']))
        #print("Expected: {}".format(expected))
        #print("Result:   {}".format(self.time['masked']['mask_master']))
        
        eq = [m==e for m, e in zip(self.time['masked']['mask_master'], expected)]
        
        self.assertEqual(all(eq), True)
        
        
class TestCalculateDifference(unittest.TestCase):
    def setUp(self):
        self.data = dict(
            masked=dict(time=np.arange(0, length, 0.1)),
            master=dict(time=np.arange(0, length, 1.0))
        )
        
        now = datetime.datetime.now()
        
        self.time = dict(
            masked=dict(time=[now + datetime.timedelta(seconds=s) for s in np.arange(0, length, 0.1)]),
            master=dict(time=[now + datetime.timedelta(seconds=s) for s in np.arange(0, length, 1.)])
        )
        
        self.pairs = ((['masked', 'time'], ['master', 'time']),)
                           
    def test_key(self):
        self.assertRaises(KeyError, lambda: calculate_differences(self.pairs, self.data, key='foo'))
    
    def test_type(self):
        self.assertRaises(TypeError, lambda: calculate_differences(self.pairs, ("", False), self.data))
        
    def test_diff_num(self):
        result = calculate_differences(self.pairs, self.data)
        
        expected = np.arange(0, 1.0, 0.1).tolist()
        expected = np.array(expected * length)
        
        #print()
        #print("Master:   {}".format(self.data['master']['time']))
        #print("Data:     {}".format(self.data['masked']['time']))
        #print("Expected: {}".format(expected))
        #print("Result:   {}".format(self.data['masked']['time_master_time']))
        
        eq = [np.isclose(m, e) for m, e in zip(self.data['masked']['time_master_time'], expected)]
        
        self.assertEqual(all(eq), True)
        
    def test_diff_time(self):
        result = calculate_differences(self.pairs, self.time)
        
        expected = np.arange(0, 1.0, 0.1)
        expected = [datetime.timedelta(seconds=e) for e in expected]
        expected = np.array(expected * length)
        
        #print()
        #print("Master:   {}".format(self.time['master']['time']))
        #print("Data:     {}".format(self.time['masked']['time']))
        #print("Expected: {}".format(expected))
        #print("Result:   {}".format(self.time['masked']['time_master_time']))
        
        eq = [np.isclose(m.total_seconds(), e.total_seconds()) for m, e in zip(self.time['masked']['time_master_time'], expected)]
        
        self.assertEqual(all(eq), True)
        
    
if __name__ == '__main__':
    unittest.main()
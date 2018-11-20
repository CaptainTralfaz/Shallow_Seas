from src.bucket import Bucket


def test_bucket_fill():
    bucket = Bucket(3)
    bucket.current = 2
    overflow = bucket.fill(4)
    assert overflow == 1, "Bucket overflow is {}, should be 1".format(overflow)
    assert bucket.current == 2, "Current amount is {}, should be 2".format(bucket.current)
    
    bucket = Bucket(3)
    bucket.current = 1
    overflow = bucket.fill(-2)
    assert overflow == -1, "Bucket overflow is {}, should be -1".format(overflow)
    assert bucket.current == 3, "Current amount is {}, should be 3".format(bucket.current)

    
def test_momentum_increase():
    momentum = Bucket(3)
    momentum.current = 2
    
    speed = 1
    
    speed += momentum.fill(2)
    
    assert momentum.current == 0, "should be 0, got {}".format(momentum.current)
    assert speed == 2, "should be 2, got {}".format(speed)


def test_momentum_decrease():
    momentum = Bucket(3)
    momentum.current = 0
    
    speed = 1
    
    speed += momentum.fill(-1)
    
    assert momentum.current == 3, "should be 3, got {}".format(momentum.current)
    assert speed == 0, "should be 3, got {}".format(speed)

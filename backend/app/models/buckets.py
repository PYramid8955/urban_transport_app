from collections import defaultdict

# Efficient bucket queue for Fiduccia–Mattheyses algorithm gains.
class BucketQueue:
    def __init__(self, max_gain=1000, bucket_size=100):
        self.buckets = defaultdict(set)
        self.max_gain = max_gain
        self.bucket_size = bucket_size
        self.highest_non_empty = -1
        self.node_to_bucket = {}  # Track which bucket each node is in
        
    def insert(self, gain, node):
        bucket_id = self._gain_to_bucket(gain)
        self.buckets[bucket_id].add(node)
        self.node_to_bucket[node] = bucket_id
        if bucket_id > self.highest_non_empty:
            self.highest_non_empty = bucket_id
            
    def remove(self, gain, node):
        bucket_id = self.node_to_bucket.get(node)
        if bucket_id is not None and node in self.buckets[bucket_id]:
            self.buckets[bucket_id].remove(node)
            del self.node_to_bucket[node]
            self._update_highest()
            
    def pop_max(self):
        if self.highest_non_empty == -1:
            return None
            
        bucket = self.buckets[self.highest_non_empty]
        if bucket:
            node = bucket.pop()
            gain = self._bucket_to_gain(self.highest_non_empty)  # FIXED: Use current bucket, not +1
            del self.node_to_bucket[node]
            self._update_highest()
            return gain, node
            
        return None
        
    def _gain_to_bucket(self, gain):
        # Map gain to bucket index (handles negative gains)
        bucket_id = int(gain * self.bucket_size) + self.max_gain * self.bucket_size // 2
        return max(0, min(bucket_id, self.max_gain * self.bucket_size - 1))
                         
    def _bucket_to_gain(self, bucket_id):
        return (bucket_id - self.max_gain * self.bucket_size // 2) / self.bucket_size
        
    def _update_highest(self):
        # Find the highest non-empty bucket
        self.highest_non_empty = -1
        for bucket_id in sorted(self.buckets.keys(), reverse=True):
            if self.buckets[bucket_id]:
                self.highest_non_empty = bucket_id
                break
                
    def is_empty(self):
        return self.highest_non_empty == -1
import heapq
from collections import defaultdict, deque

# ---------------- MERGE SORT (For Train Time Sorting) ----------------

def merge_sort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# ---------------- GRAPH ALGORITHM (Dijkstra + Fewest Train DP) ----------------

class TrainGraph:
    def __init__(self):
        self.graph = defaultdict(list)

    def add_route(self, source, destination, cost, train_id):
        self.graph[source].append((destination, cost, train_id))
        self.graph[destination].append((source, cost, train_id))  # assuming bidirectional

    def dijkstra(self, start):
        dist = {node: float('inf') for node in self.graph}
        dist[start] = 0
        prev = {node: None for node in self.graph}
        pq = [(0, start)]
        while pq:
            cost_u, u = heapq.heappop(pq)
            if cost_u > dist[u]:
                continue
            for v, cost_uv, _ in self.graph[u]:
                if dist[u] + cost_uv < dist[v]:
                    dist[v] = dist[u] + cost_uv
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))
        return dist, prev

    def reconstruct_path(self, prev, end):
        path = []
        while end:
            path.append(end)
            end = prev[end]
        return path[::-1]

    def fewest_trains(self, start, end):
        # BFS approach to find fewest train changes (number of hops)
        queue = deque([(start, 0)])
        visited = set()
        while queue:
            node, changes = queue.popleft()
            if node == end:
                return changes
            for neighbor, _, _ in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, changes + 1))
        return -1  # unreachable

# ---------------- PRIORITY QUEUE (VIP Users First) ----------------

class BookingRequest:
    def __init__(self, user_id, is_vip, request_time):
        self.user_id = user_id
        self.is_vip = is_vip
        self.request_time = request_time

    def __lt__(self, other):
        # VIP gets priority. If both same, then earlier request_time wins.
        if self.is_vip != other.is_vip:
            return self.is_vip > other.is_vip
        return self.request_time < other.request_time

def process_booking_requests(requests):
    heapq.heapify(requests)
    return [heapq.heappop(requests) for _ in range(len(requests))]

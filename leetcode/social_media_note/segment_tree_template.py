class SegmentTree:
    """区间加、区间查询、单点赋值；sum模式额外支持第k个计数。

    nums非空，下标从0开始，区间均为闭区间，调用者保证下标合法。
    mode='sum'维护区间和，mode='max'维护区间最大值。
    kth要求每个叶子的值都是非负整数，排名k从1开始。
    """

    def __init__(self, nums, mode="sum"):
        if not nums or mode not in ("sum", "max"):
            raise ValueError("nums必须非空，mode必须是sum或max")
        self.n = len(nums)
        self.mode = mode
        self.identity = 0 if mode == "sum" else float("-inf")
        self.merge = (lambda a, b: a + b) if mode == "sum" else max
        self.tree = [self.identity] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, nums)

    def _pull(self, p):
        self.tree[p] = self.merge(self.tree[p * 2], self.tree[p * 2 + 1])

    def _build(self, p, l, r, nums):
        if l == r:
            self.tree[p] = nums[l]
            return
        mid = (l + r) // 2
        self._build(p * 2, l, mid, nums)
        self._build(p * 2 + 1, mid + 1, r, nums)
        self._pull(p)

    def _apply(self, p, l, r, value):
        # 整段加value：区间和增加长度*value，区间最大值增加value。
        if self.mode == "sum":
            self.tree[p] += (r - l + 1) * value
        else:
            self.tree[p] += value
        self.lazy[p] += value

    def _push(self, p, l, r):
        if l == r or self.lazy[p] == 0:
            return
        mid = (l + r) // 2
        self._apply(p * 2, l, mid, self.lazy[p])
        self._apply(p * 2 + 1, mid + 1, r, self.lazy[p])
        self.lazy[p] = 0

    def add(self, left, right, value):
        """闭区间[left, right]内每个元素增加value。"""
        if left > right:
            return
        self._add(1, 0, self.n - 1, left, right, value)

    def _add(self, p, l, r, ql, qr, value):
        if ql <= l and r <= qr:
            self._apply(p, l, r, value)
            return
        self._push(p, l, r)
        mid = (l + r) // 2
        if ql <= mid:
            self._add(p * 2, l, mid, ql, qr, value)
        if qr > mid:
            self._add(p * 2 + 1, mid + 1, r, ql, qr, value)
        self._pull(p)

    def query(self, left, right):
        """查询区间和或最大值；空区间返回对应的单位元。"""
        if left > right:
            return self.identity
        return self._query(1, 0, self.n - 1, left, right)

    def _query(self, p, l, r, ql, qr):
        if ql <= l and r <= qr:
            return self.tree[p]
        self._push(p, l, r)
        mid = (l + r) // 2
        result = self.identity
        if ql <= mid:
            result = self.merge(result, self._query(p * 2, l, mid, ql, qr))
        if qr > mid:
            result = self.merge(result, self._query(p * 2 + 1, mid + 1, r, ql, qr))
        return result

    def update(self, index, value):
        """单点赋值：将nums[index]改为value，与add的增量含义不同。"""
        self._update(1, 0, self.n - 1, index, value)

    def _update(self, p, l, r, index, value):
        if l == r:
            self.tree[p] = value
            self.lazy[p] = 0
            return
        self._push(p, l, r)
        mid = (l + r) // 2
        if index <= mid:
            self._update(p * 2, l, mid, index, value)
        else:
            self._update(p * 2 + 1, mid + 1, r, index, value)
        self._pull(p)

    def kth(self, k):
        """sum模式：返回第k个计数所在的下标；叶子必须为非负整数。"""
        if self.mode != "sum" or not 1 <= k <= self.tree[1]:
            raise ValueError("kth要求sum模式，且1 <= k <= 总计数")
        return self._kth(1, 0, self.n - 1, k)

    def _kth(self, p, l, r, k):
        if l == r:
            return l
        # 区间加可能还未传给孩子，比较左子树计数前必须下推。
        self._push(p, l, r)
        mid = (l + r) // 2
        left_count = self.tree[p * 2]
        if k <= left_count:
            return self._kth(p * 2, l, mid, k)
        return self._kth(p * 2 + 1, mid + 1, r, k - left_count)

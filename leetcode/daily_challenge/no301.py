
#BFS solution
from collections import deque

class Solution:
    def removeInvalidParentheses(self, s: str) -> list[str]:

        def is_valid(s):
            left_parentheses_cnt = 0

            for c in s:
                if c == "(":
                    left_parentheses_cnt += 1

                elif c == ")":
                    if left_parentheses_cnt > 0:
                        left_parentheses_cnt -= 1
                    else:
                        return False

            return left_parentheses_cnt == 0

        queue = deque([s])
        visited = {s}
        ans = []

        while queue:
            size = len(queue)
            found = False

            for _ in range(size):
                cur = queue.popleft()

                if is_valid(cur):
                    ans.append(cur)
                    found = True
                    continue

                for i, c in enumerate(cur):
                    if c != "(" and c != ")":
                        continue

                    cand = cur[:i] + cur[i + 1:]

                    if cand not in visited:
                        visited.add(cand)
                        queue.append(cand)

            if found:
                break

        return ans

if __name__ == "__main__":
    s = "(a)())()"
    ans = Solution().removeInvalidParentheses(s)
    print(ans)
class Solution:
    def minAddToMakeValid(self, s: str) -> int:
        ans = 0
        left_parethness_cnt = 0
        for i,t in enumerate(s):
            if t ==")":
                if left_parethness_cnt>0:
                    left_parethness_cnt-=1
                else:
                    ans+=1
            elif t == "(":
                left_parethness_cnt+=1
            else:
                continue
        ans+=left_parethness_cnt
        return ans



if __name__ == "__main__":
    s = "())"
    ans = Solution().minAddToMakeValid(s)
    print(ans)
# Shearer-type threshold for the "tree of K_{a,a} blocks" dependency structure:
# each event (clause) lies in k blocks (one per literal); in each block it has a-1 same-side
# mates and a opposite-side neighbours (clauses containing the complementary literal).
import math
def ok(p, a, k, iters=4000):
    mu = 0.0  # effective activity of a non-root vertex (negative)
    for _ in range(iters):
        x = 1 + mu
        if x <= 0: return False
        den = x**(a-1) + x**a - 1          # Z of K_{a-1,a} with activities mu
        if den <= 0: return False
        rho = x**(a-1) / den
        new = -p * rho**(k-1)
        if abs(new - mu) < 1e-15: mu = new; break
        mu = new
    x = 1 + mu; den = x**(a-1) + x**a - 1
    if den <= 0: return False
    rho = x**(a-1)/den
    return 1 - p * rho**k > 0
def thresh(a, k):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo+hi)/2
        if ok(mid, a, k): lo = mid
        else: hi = mid
    return lo
for (k, a) in [(3,2),(4,3),(5,4),(6,5),(7,6)]:
    t = thresh(a, k)
    tree = (a*k-1)**(a*k-1)/(a*k)**(a*k)
    print(f"k={k} literal-bound L={a}: block-tree threshold p*={t:.5f}  vs p=2^-k={2**-k:.5f}  ratio p/p*={2**-k/t:.3f}   (plain {a*k}-regular tree p*={tree:.5f}, ratio {2**-k/tree:.3f})")

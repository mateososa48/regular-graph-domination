/* README item 9, degree 4, case (iii) with all main literals distinct (computer-assisted step).
 * Case (iii), all main literals distinct, every residual blocker of v contains the complement of v's main
 * literal.  Then v is blocked iff  f_v false  OR  P_v  OR  P'_v,  where P_v, P'_v are 2-literal sets
 * (the residual blockers minus ~f_v).  A P-set may contain main literals f_b / ~f_b of OTHER variables
 * (budget: f_b at most 2 further uses, ~f_b at most 1 further use) and free literals (prob 1/2 each).
 * Upper bound:  beta <= 1/16 + 1/16 * sum_{T nonempty} min(1, min_{a in T} (Pr[P_a|T] + Pr[P'_a|T])),
 * T = set of variables whose main literal is TRUE.  Output: max of X = sum_T min(4, min_a s_a(T)) in units 1/4.
 * Result: X <= 33, so beta <= (4 + 33)/64 = 37/64 < 3/5 in this sub-case.
 * Build and run:  gcc -O2 -o case3_enum case3_enum.c && ./case3_enum   (about 3 seconds)
 */
#include <stdio.h>
#include <string.h>
typedef struct { int plus, minus, nfree; } Ty;
static Ty ty[4][32]; static int nty[4];
static int val[4][32][16];          /* val[a][t][T] = 4*Pr[P|T] for type t of index a */
int main(void){
    for (int a = 0; a < 4; a++){
        int n = 0;
        ty[a][n++] = (Ty){0,0,2};
        for (int b = 0; b < 4; b++) if (b != a){ ty[a][n++] = (Ty){1<<b,0,1}; ty[a][n++] = (Ty){0,1<<b,1}; }
        for (int b = 0; b < 4; b++) for (int c = b+1; c < 4; c++) if (b != a && c != a)
            for (int sb = 0; sb < 2; sb++) for (int sc = 0; sc < 2; sc++)
                ty[a][n++] = (Ty){ (sb?0:1<<b) | (sc?0:1<<c), (sb?1<<b:0) | (sc?1<<c:0), 0 };
        nty[a] = n;
        for (int t = 0; t < n; t++) for (int T = 0; T < 16; T++){
            Ty y = ty[a][t];
            int ok = ((y.plus & T) == 0) && ((y.minus & ~T & 15) == 0);   /* f_b false iff b not in T; ~f_b false iff b in T */
            val[a][t][T] = ok ? (4 >> y.nfree) : 0;
        }
    }
    int best = -1; long long cnt = 0;
    int pick[4][2];
    /* enumerate unordered pairs of types per index with budgets */
    int up[4], um[4];
    for (int a0 = 0; a0 < nty[0]; a0++) for (int b0 = a0; b0 < nty[0]; b0++)
    for (int a1 = 0; a1 < nty[1]; a1++) for (int b1 = a1; b1 < nty[1]; b1++){
        int t[4][2] = {{a0,b0},{a1,b1},{0,0},{0,0}};
        memset(up,0,sizeof up); memset(um,0,sizeof um);
        int bad = 0;
        for (int a = 0; a < 2 && !bad; a++) for (int k = 0; k < 2; k++){
            Ty y = ty[a][t[a][k]];
            for (int b = 0; b < 4; b++){ if (y.plus>>b&1) up[b]++; if (y.minus>>b&1) um[b]++; }
        }
        for (int b = 0; b < 4; b++) if (up[b] > 2 || um[b] > 1) bad = 1;
        if (bad) continue;
        int up2[4], um2[4];
        for (int a2 = 0; a2 < nty[2]; a2++) for (int b2 = a2; b2 < nty[2]; b2++){
            memcpy(up2,up,sizeof up); memcpy(um2,um,sizeof um);
            int bad2 = 0;
            int tt[2] = {a2,b2};
            for (int k = 0; k < 2; k++){ Ty y = ty[2][tt[k]];
                for (int b = 0; b < 4; b++){ if (y.plus>>b&1) up2[b]++; if (y.minus>>b&1) um2[b]++; } }
            for (int b = 0; b < 4; b++) if (up2[b] > 2 || um2[b] > 1) bad2 = 1;
            if (bad2) continue;
            for (int a3 = 0; a3 < nty[3]; a3++) for (int b3 = a3; b3 < nty[3]; b3++){
                int up3[4], um3[4]; memcpy(up3,up2,sizeof up); memcpy(um3,um2,sizeof um);
                int bad3 = 0, t3[2] = {a3,b3};
                for (int k = 0; k < 2; k++){ Ty y = ty[3][t3[k]];
                    for (int b = 0; b < 4; b++){ if (y.plus>>b&1) up3[b]++; if (y.minus>>b&1) um3[b]++; } }
                for (int b = 0; b < 4; b++) if (up3[b] > 2 || um3[b] > 1) bad3 = 1;
                if (bad3) continue;
                cnt++;
                int sel[4][2] = {{a0,b0},{a1,b1},{a2,b2},{a3,b3}};
                int X = 0;
                for (int T = 1; T < 16; T++){
                    int m = 4;
                    for (int a = 0; a < 4; a++) if (T>>a&1){
                        int s = val[a][sel[a][0]][T] + val[a][sel[a][1]][T];
                        if (s < m) m = s;
                    }
                    X += m;
                }
                if (X > best){ best = X; memcpy(pick, sel, sizeof pick);
                    printf("new best X=%d  (beta bound %.5f)\n", X, (4.0 + X) / 64.0); fflush(stdout); }
            }
        }
    }
    printf("configurations %lld, max X = %d, beta <= %d/64 = %.5f\n", cnt, best, 4 + best, (4.0 + best) / 64.0);
    for (int a = 0; a < 4; a++) for (int k = 0; k < 2; k++){
        Ty y = ty[a][pick[a][k]];
        printf("index %d P%d: plus=%x minus=%x free=%d\n", a, k, y.plus, y.minus, y.nfree);
    }
    return 0;
}

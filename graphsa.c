/* Simulated annealing over connected D-regular graphs on n vertices (n <= 60, edges <= 128),
 * maximizing  f = i(G) - gamma_e(G)   (i = independent domination number,
 * gamma_e = minimum maximal matching).  f >= 1 is a counterexample to the TxGraffiti
 * inequality i <= gamma_e; we also report gamma(G) for any such graph.
 * Moves: double-edge swaps preserving regularity and connectivity.
 * usage: graphsa D n seed steps T0
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

typedef unsigned __int128 u128;
static inline int pc(u128 x){ return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x>>64)); }
static inline int ctz(u128 x){ uint64_t lo=(uint64_t)x; return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((uint64_t)(x>>64)); }
#define ONE ((u128)1)

static int N; static u128 NB[128]; static u128 ALL; static int MAXC;
static long long nodes;
static int dfs(u128 dom, u128 forb, int c, int K, int indep) {
    nodes++;
    if (dom == ALL) return 1;
    if (c >= K) return 0;
    u128 und = ALL & ~dom;
    int u = pc(und);
    if (c + (u + MAXC - 1) / MAXC > K) return 0;
    int bestc = 1000; u128 bestcand = 0; u128 t = und;
    while (t) { int v = ctz(t); t &= t - 1; u128 cand = NB[v] & ~forb; int cc = pc(cand);
        if (cc < bestc) { bestc = cc; bestcand = cand; if (cc <= 1) break; } }
    if (bestc == 0) return 0;
    u128 cand = bestcand;
    while (cand) { int w = ctz(cand); cand &= cand - 1;
        u128 nf = indep ? (forb | NB[w]) : (forb | (ONE << w));
        if (dfs(dom | NB[w], nf, c + 1, K, indep)) return 1;
        forb |= ONE << w; }
    return 0;
}
static int exists_le(int K, int indep){ return dfs(0,0,0,K,indep); }
static int exact_min(int lo, int indep){ int K = lo; while (!exists_le(K, indep)) K++; return K; }

static int D, n, m;
static int adj[64][64];
static int eu[128], ev[128];

static uint64_t rs;
static inline uint64_t rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double urand(void){ return (rnd() >> 11) * (1.0/9007199254740992.0); }

static void load_vertex_graph(void){
    N = n; ALL = (ONE << n) - 1; MAXC = D + 1;
    for (int v = 0; v < n; v++){ u128 nb = ONE << v; for (int w = 0; w < n; w++) if (adj[v][w]) nb |= ONE << w; NB[v] = nb; }
}
static void load_line_graph(void){
    N = m; ALL = (m == 128) ? ~(u128)0 : ((ONE << m) - 1); MAXC = 2*D - 1;
    for (int a = 0; a < m; a++){ u128 nb = ONE << a;
        for (int b = 0; b < m; b++) if (b != a && (eu[a]==eu[b]||eu[a]==ev[b]||ev[a]==eu[b]||ev[a]==ev[b])) nb |= ONE << b;
        NB[a] = nb; }
}
static void rebuild_edges(void){ m = 0; for (int i = 0; i < n; i++) for (int j = i+1; j < n; j++) if (adj[i][j]) { eu[m]=i; ev[m]=j; m++; } }

static int connected(void){
    int seen[64] = {0}, st[64], sp = 0; seen[0] = 1; st[sp++] = 0; int cnt = 1;
    while (sp){ int v = st[--sp]; for (int w = 0; w < n; w++) if (adj[v][w] && !seen[w]) { seen[w] = 1; cnt++; st[sp++] = w; } }
    return cnt == n;
}
static int random_regular(void){
    for (int tries = 0; tries < 100000; tries++){
        int stubs[64*8], s = 0; memset(adj, 0, sizeof adj);
        for (int v = 0; v < n; v++) for (int r = 0; r < D; r++) stubs[s++] = v;
        for (int i = s - 1; i > 0; i--){ int j = rnd() % (i+1); int t = stubs[i]; stubs[i] = stubs[j]; stubs[j] = t; }
        int ok = 1;
        for (int i = 0; i < s; i += 2){ int a = stubs[i], b = stubs[i+1]; if (a == b || adj[a][b]) { ok = 0; break; } adj[a][b] = adj[b][a] = 1; }
        if (ok && connected()) { rebuild_edges(); return 1; }
    }
    return 0;
}
static int lbe(void){ return (D * n + (4*D - 2) - 1) / (4*D - 2); }
static void eval(int *ge, int *iv){
    load_line_graph(); *ge = exact_min(lbe(), 1);
    load_vertex_graph(); *iv = exact_min((n + D) / (D + 1), 1);
}
static void print_g6(FILE *f){
    /* graph6 for n <= 62 */
    fputc(63 + n, f); int k = 0, x = 0;
    for (int j = 1; j < n; j++) for (int i = 0; i < j; i++){ x = (x << 1) | adj[i][j]; if (++k == 6){ fputc(63 + x, f); k = 0; x = 0; } }
    if (k) { x <<= (6 - k); fputc(63 + x, f); }
    fputc('\n', f);
}

int main(int argc, char **argv){
    D = atoi(argv[1]); n = atoi(argv[2]); rs = 0x9E3779B97F4A7C15ULL ^ ((uint64_t)atoll(argv[3]) * 0xD1B54A32D192ED03ULL);
    long long steps = atoll(argv[4]); double T0 = atof(argv[5]);
    if (!random_regular()){ fprintf(stderr, "no init\n"); return 1; }
    int ge, iv; eval(&ge, &iv);
    double f = iv - ge; double best = f;
    fprintf(stderr, "init ge=%d i=%d\n", ge, iv);
    for (long long s = 0; s < steps; s++){
        double T = T0 * (1.0 - (double)s / steps) + 0.02;
        int e1 = rnd() % m, e2 = rnd() % m; if (e1 == e2) continue;
        int a = eu[e1], b = ev[e1], c = eu[e2], d = ev[e2];
        if (a==c||a==d||b==c||b==d) continue;
        if (rnd() & 1){ int t = c; c = d; d = t; }
        if (adj[a][c] || adj[b][d]) continue;
        adj[a][b]=adj[b][a]=0; adj[c][d]=adj[d][c]=0; adj[a][c]=adj[c][a]=1; adj[b][d]=adj[d][b]=1;
        if (!connected()){ adj[a][c]=adj[c][a]=0; adj[b][d]=adj[d][b]=0; adj[a][b]=adj[b][a]=1; adj[c][d]=adj[d][c]=1; continue; }
        rebuild_edges();
        int nge, niv; eval(&nge, &niv);
        double nf = niv - nge;
        if (nf >= f || urand() < exp((nf - f) / T)){ f = nf; ge = nge; iv = niv;
            if (f > best){ best = f; fprintf(stderr, "step %lld new best f=%g (ge=%d i=%d)\n", s, f, ge, iv); }
            if (f >= 1){
                load_vertex_graph(); int g_le = exists_le(ge, 0);
                printf("FOUND D=%d n=%d ge=%d i=%d gamma<=ge:%s ", D, n, ge, iv, g_le ? "yes" : "NO"); print_g6(stdout); fflush(stdout);
                return 0; }
        } else { adj[a][c]=adj[c][a]=0; adj[b][d]=adj[d][b]=0; adj[a][b]=adj[b][a]=1; adj[c][d]=adj[d][c]=1; rebuild_edges(); }
    }
    fprintf(stderr, "end best f=%g\n", best);
    return 0;
}

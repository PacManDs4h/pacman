// wilson_json.cpp
// Wilson (Loop-Erased Random Walk) + "braid" (réduction des culs-de-sac) => sortie JSON (simplifiée).

#include <bits/stdc++.h>
using namespace std;

enum Dir { N=1, E=2, S=4, W=8 };

struct Maze {
    int Wd, Ht;
    vector<int> walls; // bitmask N/E/S/W : 1 = mur présent

    Maze(int w, int h) : Wd(w), Ht(h), walls(w*h, N|E|S|W) {}
    inline int idx(int x, int y) const { return y*Wd + x; }
    inline bool inBounds(int x, int y) const { return (0<=x && x<Wd && 0<=y && y<Ht); }

    vector<tuple<int,int,int>> neighbors(int i) const {
        int x = i % Wd, y = i / Wd;
        vector<tuple<int,int,int>> nb;
        if (inBounds(x, y-1)) nb.emplace_back(idx(x, y-1), N, S);
        if (inBounds(x+1, y)) nb.emplace_back(idx(x+1, y), E, W);
        if (inBounds(x, y+1)) nb.emplace_back(idx(x, y+1), S, N);
        if (inBounds(x-1, y)) nb.emplace_back(idx(x-1, y), W, E);
        return nb;
    }
    void carveBetween(int a, int b) {
        int ax = a % Wd, ay = a / Wd;
        int bx = b % Wd, by = b / Wd;
        if (bx == ax && by == ay-1) { walls[a] &= ~N; walls[b] &= ~S; }
        else if (bx == ax+1 && by == ay) { walls[a] &= ~E; walls[b] &= ~W; }
        else if (bx == ax && by == ay+1) { walls[a] &= ~S; walls[b] &= ~N; }
        else if (bx == ax-1 && by == ay) { walls[a] &= ~W; walls[b] &= ~E; }
    }
    int degree(int i) const {
        int d = 0;
        if (!(walls[i] & N)) ++d;
        if (!(walls[i] & E)) ++d;
        if (!(walls[i] & S)) ++d;
        if (!(walls[i] & W)) ++d;
        return d;
    }
};

// Wilson : arbre couvrant uniforme
void wilsonGenerate(Maze &M, std::mt19937_64 &rng) {
    const int N = M.Wd * M.Ht;
    vector<char> inTree(N, 0);
    uniform_int_distribution<int> distStart(0, N-1);
    int root = distStart(rng);
    inTree[root] = 1;
    int inCount = 1;

    vector<int> notIn; notIn.reserve(N);
    auto pickOutside = [&]() -> int {
        notIn.clear();
        for (int i=0;i<N;++i) if (!inTree[i]) notIn.push_back(i);
        if (notIn.empty()) return -1;
        uniform_int_distribution<size_t> d(0, notIn.size()-1);
        return notIn[d(rng)];
    };

    while (inCount < N) {
        int start = pickOutside();
        if (start < 0) break;

        vector<int> path; path.reserve(N);
        unordered_map<int,int> pos; pos.reserve(64);
        path.push_back(start); pos[start]=0;

        int cur = start;
        while (!inTree[cur]) {
            auto nb = M.neighbors(cur);
            uniform_int_distribution<size_t> d(0, nb.size()-1);
            auto [nextIdx, dir, opp] = nb[d(rng)];
            cur = nextIdx;

            auto it = pos.find(cur);
            if (it != pos.end()) {
                int keep = it->second;
                for (int k=keep+1;k<(int)path.size();++k) pos.erase(path[k]);
                path.resize(keep+1);
            } else {
                pos[cur] = (int)path.size();
                path.push_back(cur);
            }
        }
        for (int i=0;i+1<(int)path.size();++i) {
            M.carveBetween(path[i], path[i+1]);
            if (!inTree[path[i]]) { inTree[path[i]]=1; ++inCount; }
        }
        int last = path.back();
        if (!inTree[last]) { inTree[last]=1; ++inCount; }
    }
}

// Post-traitement : ouvrir des murs pour réduire les culs-de-sac
void braidDeadEnds(Maze& M, double p, std::mt19937_64& rng) {
    if (p <= 0.0) return;
    const int N = M.Wd * M.Ht;
    vector<int> order(N);
    iota(order.begin(), order.end(), 0);
    shuffle(order.begin(), order.end(), rng);

    uniform_real_distribution<double> U(0.0,1.0);

    for (int i : order) {
        if (M.degree(i) != 1) continue;
        if (U(rng) > p) continue;

        vector<int> candidates;
        int x = i % M.Wd, y = i / M.Wd;
        if (M.inBounds(x, y-1) && (M.walls[i] & N)) candidates.push_back(M.idx(x, y-1));
        if (M.inBounds(x+1, y) && (M.walls[i] & E)) candidates.push_back(M.idx(x+1, y));
        if (M.inBounds(x, y+1) && (M.walls[i] & S)) candidates.push_back(M.idx(x, y+1));
        if (M.inBounds(x-1, y) && (M.walls[i] & W)) candidates.push_back(M.idx(x-1, y));

        if (candidates.empty()) continue;

        auto pick = [&](){
            vector<int> good;
            for (int v : candidates) if (M.degree(v) >= 2) good.push_back(v);
            if (!good.empty()) {
                uniform_int_distribution<size_t> d(0, good.size()-1);
                return good[d(rng)];
            } else {
                uniform_int_distribution<size_t> d(0, candidates.size()-1);
                return candidates[d(rng)];
            }
        };

        int j = pick();
        M.carveBetween(i, j);
    }
}

/* =================== JSON SIMPLIFIÉ : minimal | flat | rle =================== */

static vector<int> flatten_grid(const Maze& m) {
    vector<int> g; g.reserve(m.Wd*m.Ht);
    for (int y=0;y<m.Ht;++y)
        for (int x=0;x<m.Wd;++x)
            g.push_back(m.walls[m.idx(x,y)]);
    return g;
}
static vector<pair<int,int>> rle_encode(const vector<int>& a) {
    vector<pair<int,int>> out;
    if (a.empty()) return out;
    int v = a[0], c = 1;
    for (size_t i=1;i<a.size();++i) {
        if (a[i]==v) ++c;
        else { out.emplace_back(v,c); v=a[i]; c=1; }
    }
    out.emplace_back(v,c);
    return out;
}

enum class JsonMode { Minimal, Flat, RLE };

// Minimal : lisible & complet (w,h,seed,braid,enc,grid[])
static void writeJSON_minimal(const Maze& m, const string& path,
                              uint64_t seed, double braid, bool pretty)
{
    ofstream f;
    ostream* op = nullptr;
    if (path.empty() || path=="-") op=&cout; else { f.open(path, ios::binary); op=&f; }
    if (!*op) { cerr<<"Impossible d’ouvrir "<<path<<"\n"; exit(1); }
    auto& o = *op;
    auto nl=[&](){ if(pretty) o<<'\n'; };
    auto ind=[&](int k){ if(pretty) while(k--) o<<"  "; };

    vector<int> grid = flatten_grid(m);

    o << "{"; nl();
    ind(1); o << "\"w\": " << m.Wd << ","; nl();
    ind(1); o << "\"h\": " << m.Ht << ","; nl();
    ind(1); o << "\"seed\": " << seed << ","; nl();
    ind(1); o << fixed << setprecision(6) << "\"braid\": " << braid << ","; nl();
    ind(1); o << "\"enc\": \"walls bitmask N=1,E=2,S=4,W=8 (1 = mur present)\","; nl();
    ind(1); o << "\"grid\": [";
    if (pretty) nl();
    for (int i=0;i<(int)grid.size();++i) {
        if (pretty) ind(2);
        o << grid[i];
        if (i+1<(int)grid.size()) o << ",";
        if (pretty) nl();
    }
    ind(1); o << "]"; nl();
    o << "}";
    if (pretty) o<<'\n';
}

// Flat : ultra simple & compact
static void writeJSON_flat(const Maze& m, const string& path, bool pretty)
{
    ofstream f;
    ostream* op = nullptr;
    if (path.empty() || path=="-") op=&cout; else { f.open(path, ios::binary); op=&f; }
    if (!*op) { cerr<<"Impossible d’ouvrir "<<path<<"\n"; exit(1); }
    auto& o = *op;
    vector<int> grid = flatten_grid(m);

    if (!pretty) {
        o << "{\"w\":"<<m.Wd<<",\"h\":"<<m.Ht<<",\"grid\":[";
        for (int i=0;i<(int)grid.size();++i){ o<<grid[i]; if(i+1<(int)grid.size()) o<<","; }
        o << "]}";
        return;
    }
    // pretty
    o << "{\n  \"w\": "<<m.Wd<<",\n  \"h\": "<<m.Ht<<",\n  \"grid\": [\n";
    for (int i=0;i<(int)grid.size();++i){
        o << "    " << grid[i] << (i+1<(int)grid.size() ? "," : "") << "\n";
    }
    o << "  ]\n}\n";
}

// RLE : très compact pour stocker/transférer
static void writeJSON_rle(const Maze& m, const string& path, bool pretty)
{
    ofstream f;
    ostream* op = nullptr;
    if (path.empty() || path=="-") op=&cout; else { f.open(path, ios::binary); op=&f; }
    if (!*op) { cerr<<"Impossible d’ouvrir "<<path<<"\n"; exit(1); }
    auto& o = *op;

    vector<int> grid = flatten_grid(m);
    auto runs = rle_encode(grid);

    if (!pretty) {
        o << "{\"w\":"<<m.Wd<<",\"h\":"<<m.Ht<<",\"rle\":[";
        for (size_t i=0;i<runs.size();++i){
            o << "["<<runs[i].first<<","<<runs[i].second<<"]";
            if (i+1<runs.size()) o << ",";
        }
        o << "]}";
        return;
    }
    // pretty
    o << "{\n  \"w\": "<<m.Wd<<",\n  \"h\": "<<m.Ht<<",\n  \"rle\": [\n";
    for (size_t i=0;i<runs.size();++i){
        o << "    ["<<runs[i].first<<","<<runs[i].second<<"]"
          << (i+1<runs.size()? ",":"") << "\n";
    }
    o << "  ]\n}\n";
}

/*** ------------------------------ main ------------------------------ ***/
int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <largeur> <hauteur> [seed] "
             << "--braid <0..1> --json <fichier.json|-> [--pretty] [--json-format minimal|flat|rle]\n";
        cerr << "  (mettre '-' pour stdout)\n";
        return 1;
    }
    int Wd = stoi(argv[1]), Ht = stoi(argv[2]);
    if (Wd<=0 || Ht<=0) { cerr << "Dimensions invalides.\n"; return 1; }

    uint64_t seed;
    int argi = 3;
    if (argi < argc && string(argv[argi]).rfind("--",0)!=0) {
        seed = stoull(argv[argi++]);
    } else {
        seed = chrono::high_resolution_clock::now().time_since_epoch().count()
             ^ (uint64_t)uintptr_t(new int)
             ^ (uint64_t)random_device{}();
    }
    mt19937_64 rng(seed);

    double braidP = 0.7;
    string jsonFile;
    bool pretty = false;
    JsonMode mode = JsonMode::Minimal;

    while (argi < argc) {
        string opt = argv[argi++];
        if (opt == "--braid") {
            if (argi >= argc) { cerr << "--braid <0..1>\n"; return 1; }
            braidP = stod(argv[argi++]);
            braidP = max(0.0, min(1.0, braidP));
        } else if (opt == "--json") {
            if (argi >= argc) { cerr << "--json <fichier|->\n"; return 1; }
            jsonFile = argv[argi++];
        } else if (opt == "--pretty") {
            pretty = true;
        } else if (opt == "--json-format") {
            if (argi >= argc) { cerr << "--json-format <minimal|flat|rle>\n"; return 1; }
            string v = argv[argi++];
            if (v=="minimal") mode=JsonMode::Minimal;
            else if (v=="flat") mode=JsonMode::Flat;
            else if (v=="rle") mode=JsonMode::RLE;
            else { cerr<<"format inconnu: "<<v<<"\n"; return 1; }
        } else {
            cerr << "Option inconnue: " << opt << "\n"; return 1;
        }
    }

    if (jsonFile.empty()) {
        cerr << "Sortie JSON requise. Utilisez --json <fichier.json | ->\n";
        return 1;
    }

    Maze m(Wd, Ht);
    wilsonGenerate(m, rng);
    braidDeadEnds(m, braidP, rng);

    // Écrit vers fichier (ou stdout si jsonFile == "-")
    if (mode==JsonMode::Minimal) {
        writeJSON_minimal(m, jsonFile == "-" ? string() : jsonFile, seed, braidP, pretty);
    } else if (mode==JsonMode::Flat) {
        writeJSON_flat(m, jsonFile == "-" ? string() : jsonFile, pretty);
    } else {
        writeJSON_rle(m, jsonFile == "-" ? string() : jsonFile, pretty);
    }

    if (jsonFile != "-")
        cerr << "JSON écrit dans: " << jsonFile
             << " | seed="<<seed<<" | braid="<<braidP
             << " | format="<<(mode==JsonMode::Minimal?"minimal":(mode==JsonMode::Flat?"flat":"rle"))
             << "\n";
    return 0;
}

// wilson_bmp.cpp
// Wilson (Loop-Erased Random Walk) + "braid" (suppression de culs-de-sac) + sortie BMP uniquement.

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
        // nb d’ouvertures (donc 4 - nb de murs)
        int d = 0;
        if (!(walls[i] & N)) ++d;
        if (!(walls[i] & E)) ++d;
        if (!(walls[i] & S)) ++d;
        if (!(walls[i] & W)) ++d;
        return d;
    }
};

// Wilson
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

/* --------- Post-traitement : "braid" (suppression de culs-de-sac) ----------
   Pour chaque cellule de degré 1 (cul-de-sac), avec proba p, on ouvre un mur
   supplémentaire vers un voisin (mur encore présent), ce qui crée une boucle.
*/
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

        // Liste de voisins avec lesquels il y a encore un mur (candidats à ouvrir)
        vector<int> candidates;
        int x = i % M.Wd, y = i / M.Wd;
        // Nord
        if (M.inBounds(x, y-1) && (M.walls[i] & N)) candidates.push_back(M.idx(x, y-1));
        // Est
        if (M.inBounds(x+1, y) && (M.walls[i] & E)) candidates.push_back(M.idx(x+1, y));
        // Sud
        if (M.inBounds(x, y+1) && (M.walls[i] & S)) candidates.push_back(M.idx(x, y+1));
        // Ouest
        if (M.inBounds(x-1, y) && (M.walls[i] & W)) candidates.push_back(M.idx(x-1, y));

        if (candidates.empty()) continue;

        // Heuristique simple : si possible, ouvrir vers un voisin qui n’est PAS un cul-de-sac,
        // pour éviter créer un "couloir inutile". Sinon, n’importe lequel.
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

/* --------- BMP 24 bits (sans libs) ---------- */
static void writeBMP(const string& filename, int W, int H, const vector<unsigned char>& rgb) {
    int rowSize = ((24*W + 31)/32)*4;
    int dataSize = rowSize * H;
    int fileSize = 54 + dataSize;

    vector<unsigned char> header(54, 0);
    header[0]='B'; header[1]='M';
    *reinterpret_cast<uint32_t*>(&header[2])  = fileSize;
    *reinterpret_cast<uint32_t*>(&header[10]) = 54;
    *reinterpret_cast<uint32_t*>(&header[14]) = 40;
    *reinterpret_cast<int32_t*>(&header[18])  = W;
    *reinterpret_cast<int32_t*>(&header[22])  = H;
    *reinterpret_cast<uint16_t*>(&header[26]) = 1;
    *reinterpret_cast<uint16_t*>(&header[28]) = 24;
    *reinterpret_cast<uint32_t*>(&header[34]) = dataSize;

    ofstream f(filename, ios::binary);
    f.write((char*)header.data(), header.size());
    vector<unsigned char> row(rowSize, 0);
    for (int y=H-1; y>=0; --y) {
        const unsigned char* src = &rgb[y*W*3];
        memcpy(row.data(), src, W*3);
        f.write((char*)row.data(), rowSize);
    }
}

void renderBMP(const Maze& m, const string& out, int cellSize, int wall, int margin,
               unsigned char Rw=0, unsigned char Gw=0, unsigned char Bw=0,
               unsigned char Rp=200, unsigned char Gp=200, unsigned char Bp=200) {
    int W = margin*2 + m.Wd*cellSize + (m.Wd+1)*wall;
    int H = margin*2 + m.Ht*cellSize + (m.Ht+1)*wall;

    vector<unsigned char> img(W*H*3, 0);
    auto setPix = [&](int x,int y,unsigned char r,unsigned char g,unsigned char b){
        if (0<=x && x<W && 0<=y && y<H) {
            int p = (y*W + x)*3;
            img[p]=r; img[p+1]=g; img[p+2]=b;
        }
    };
    auto fillRect = [&](int x,int y,int ww,int hh,unsigned char r,unsigned char g,unsigned char b){
        for (int yy=y; yy<y+hh; ++yy)
            for (int xx=x; xx<x+ww; ++xx) setPix(xx,yy,r,g,b);
    };

    // Fond = murs
    fillRect(0,0,W,H,Rw,Gw,Bw);

    int y0 = margin + wall;
    for (int cy=0; cy<m.Ht; ++cy) {
        int x0 = margin + wall;
        for (int cx=0; cx<m.Wd; ++cx) {
            int i = m.idx(cx,cy);
            // chambre
            fillRect(x0, y0, cellSize, cellSize, Rp,Gp,Bp);
            // ouverture Est
            if (!(m.walls[i] & E)) fillRect(x0+cellSize, y0, wall, cellSize, Rp,Gp,Bp);
            // ouverture Sud
            if (!(m.walls[i] & S)) fillRect(x0, y0+cellSize, cellSize, wall, Rp,Gp,Bp);

            x0 += cellSize + wall;
        }
        y0 += cellSize + wall;
    }

    writeBMP(out, W, H, img);
}

/* --------------------------- main --------------------------- */
int main(int argc, char** argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <largeur> <hauteur> [seed] --braid <taux 0..1> --bmp <fichier> <cellSize> <wall> [margin]\n";
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

    double braidP = 0.7; // défaut : 70%
    string bmpFile; int cellSize=20, wall=3, margin=10;

    // parse options
    while (argi < argc) {
        string opt = argv[argi++];
        if (opt == "--braid") {
            if (argi >= argc) { cerr << "--braid <taux>\n"; return 1; }
            braidP = stod(argv[argi++]);
            if (braidP < 0.0) braidP = 0.0;
            if (braidP > 1.0) braidP = 1.0;
        } else if (opt == "--bmp") {
            if (argi+2 >= argc) {
                cerr << "--bmp <fichier> <cellSize> <wall> [margin]\n"; return 1;
            }
            bmpFile  = argv[argi++];
            cellSize = stoi(argv[argi++]);
            wall     = stoi(argv[argi++]);
            if (argi < argc && string(argv[argi]).rfind("--",0)!=0)
                margin = stoi(argv[argi++]);
        } else {
            cerr << "Option inconnue: " << opt << "\n"; return 1;
        }
    }

    if (bmpFile.empty()) {
        cerr << "Sortie BMP requise. Utilisez --bmp <fichier> <cellSize> <wall> [margin]\n";
        return 1;
    }

    Maze m(Wd, Ht);
    wilsonGenerate(m, rng);
    braidDeadEnds(m, braidP, rng);     // <<<< post-traitement anti culs-de-sac
    renderBMP(m, bmpFile, cellSize, wall, margin);

    cout << "Image ecrite: " << bmpFile << "  | braid=" << braidP
         << "  | cellSize=" << cellSize << "  | wall=" << wall << "\n";
    return 0;
}

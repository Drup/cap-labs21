#include "printlib.h"

int main() {
    
    int n,v;
    bool u;
    n=6;
    u=12>n;
    println_int(1<n && u);
    return 0;
}

// EXPECTED
// 1

#include "printlib.h"

int main() {
    
    bool b;
    b = false;
    println_int(b);
    b = true;
    println_int(b);
    println_int(true);
    println_int(false);
    return 0;
}

// EXPECTED
// 0
// 1
// 1
// 0

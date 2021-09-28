#include "printlib.h"

int main() {
    bool x;
    if (x) {
        println_int(1);
    } else {
        println_int(0);
    }
    x = !x;
    if (x) {
        println_int(1);
    } else {
        println_int(0);
    }
    return 0;
}

// EXPECTED
// 0
// 1
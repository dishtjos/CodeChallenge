#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <stdbool.h>
#include <string.h>


struct header {
    uint32_t sig;        // Magic Signature of 32 bits to identify the binary ("0xcafef00d")
    uint8_t numDevices;  // Number of smart devices on the network
    uint8_t hash[32];    // A SHA256 Hash of all binary entries
    uint64_t timestamp;  // Timestamp of when binary was generated
};

struct entry {
    char name[256];       // The name of the device
    uint64_t mac : 48;    // The mac address of the device
    uint64_t majVer : 8;  // The major version of the firmware the X in X.Y
    uint64_t minVer : 8;  // The minor version of the firmware the Y in X.Y
};

void calculate_sha256(
    _In_ char* bytes, 
    _In_ int num_bytes, 
    _Out_ char* hash
);

bool compare_sha256(
    _In_ uint8_t* hash1, 
    _In_ uint8_t* hash2
);

bool is_machine_little_endian();

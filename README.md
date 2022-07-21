# CodeChallenge

Use GitHub to version control your development and send back a link to the repository with your final solution.
Develop a command line tool which would take as input the file attached to this email and would generate a binary file which would adhere to the following format:


The format of the HEADER should be:
struct header {

    uint32_t sig;        // Magic Signature of 32 bits to identify the binary ("0xcafef00d")

    uint8_t numDevices;  // Number of smart devices on the network

    uint8_t hash[32];    // A SHA256 Hash of all binary entries

    uin64_t timestamp;   // Timestamp of when binary was generated

}

The format of each ENTRY should be:
struct entry {

    char name[256];     // The name of the device

    uint64_t mac:48;    // The mac address of the device

    uint64_t majVer:8;  // The major version of the firmware the X in X.Y

    uint64_t minVer:8;  // The minor version of the firmware the Y in X.Y

}

 

Develop a command line tool which would take the binary file from #2 and verify the hash in the header is correct and will print a list of device names with corresponding mac addresses to stdout.

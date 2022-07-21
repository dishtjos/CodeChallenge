#include <sys/stat.h>
#include <fcntl.h>
#include "openssl/sha.h"
#include "bin_parser.h"

void calculate_sha256(char* bytes, int num_bytes, char* hash) {
    SHA256_CTX sha256;

    SHA256_Init(&sha256);
    SHA256_Update(&sha256, bytes, num_bytes);
    SHA256_Final(hash, &sha256);
}

bool compare_sha256(uint8_t* hash1, uint8_t* hash2) {
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        if (hash1[i] != hash2[i]) {
            return false;
        }
    }
    return true;
}

bool is_machine_little_endian() {
    uint32_t test_num32 = 0x10000001;
    uint64_t test_num64 = 0x1000000000000001;
    uint8_t* test_ptr;
    switch (sizeof(void*)) {
    case 4:
        test_ptr = &test_num32;
    case 8:
        test_ptr = &test_num64;
    default:
        test_ptr = &test_num64;
    }
    if (test_ptr[0] == 0x01) {
        return true;
    }
    return false;
}

int main(int argc, char* argv[]) {
    unsigned int total_file_bytes = 0, num_entry_bytes = 0;
    unsigned char hash[SHA256_DIGEST_LENGTH] = {0};
    struct header file_header = {0};
    struct entry *file_entry = NULL;
    char * file_contents = NULL;
    uint8_t* entry_bytes = NULL;
    uint8_t* byte_ptr = NULL;
    bool is_hash_matching = false;
    uint64_t mac_address = 0;

    // get filename from command line input
    if (argc < 2) {
        printf("ERROR: Input bin filename is not specified.\n");
        goto Exit;
    }
    const char* filename = argv[1];

    // read given binary file and store in buffer
    int fd = open(filename, O_RDONLY);
    struct stat sb;

    if (-1 == fd || -1 == stat(filename, &sb)) {
        printf("ERROR: Can not open input file.\n");
        goto Exit;
    }
    file_contents = malloc(sb.st_size);
    read(fd, file_contents, sb.st_size);

    // check if binary file size is sufficient to copy header bytes
    total_file_bytes = sb.st_size;
    if (total_file_bytes < sizeof(file_header)) {
        printf("ERROR: Given bin file is invalid.\n");
        goto Exit;
    }

    // extract header bytes from buffer
    memcpy(&file_header, file_contents, sizeof(file_header));

    // check if extracted num of devices field is correct
    if (total_file_bytes < sizeof(file_header) + (file_header.numDevices*sizeof(struct entry))) {
        printf("ERROR: Given bin file is invalid.\n");
        goto Exit;
    }

    // extract entry bytes from buffer
    num_entry_bytes = total_file_bytes - sizeof(file_header);
    entry_bytes = (uint8_t*)calloc(num_entry_bytes, sizeof(uint8_t));
    memcpy(entry_bytes, file_contents + sizeof(file_header), num_entry_bytes);

    // calculate hash of entry bytes
    calculate_sha256(entry_bytes, num_entry_bytes, hash);

    // compare entry byte hash
    is_hash_matching = compare_sha256(hash, file_header.hash);
    if (is_hash_matching != true) {
        printf("ERROR: Hash values are not matching.\n");
        goto Exit;
    }

    // print device name and mac
    file_entry = (struct entry*)entry_bytes;
    for (int i = 0; i < file_header.numDevices; i++) {
        printf("\nDevice name        : %s\n", file_entry[i].name);
        mac_address = file_entry[i].mac;
        byte_ptr = &mac_address;
        if (is_machine_little_endian()) {
            printf("Device MAC Address : %02x:%02x:%02x:%02x:%02x:%02x\n", \
                byte_ptr[5], byte_ptr[4], byte_ptr[3], byte_ptr[2], byte_ptr[1], byte_ptr[0]);
        }
        else {
            printf("Device MAC Address : %02x:%02x:%02x:%02x:%02x:%02x\n", \
                byte_ptr[2], byte_ptr[3], byte_ptr[4], byte_ptr[5], byte_ptr[6], byte_ptr[7]);
        }
    }

Exit:
    free(file_contents);
    free(entry_bytes);
    return 0;
}
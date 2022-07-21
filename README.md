# CodeChallenge

## Introduction
Develop a command line tool which would take as input the file attached to this email and would generate a binary file which would adhere to the following format:

HEADER->ENTRY-1->ENTRY-2-> ... ->ENTRY-N

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

## bin_generator
### Prerequisite:
- python 3.x (please follow instruction on: https://www.python.org/downloads/)
- jsonschema (run command: pip install jsonschema)

### How to use:
`python bin_generator.py -in <input_json_with_path> -out <output_file_name>`
>e.g. python bin_generator.py -in input.json -out out1.bin
```
python bin_generator.py --help
usage: bin_generator.py [-h] -in INPUT [-out OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -in INPUT, --input INPUT
                        Input JSON file path
  -out OUTPUT, --output OUTPUT
                        Output bin file path
```

## bin_parser
### Prerequisite:
- gcc (Rev3, Built by MSYS2 project) 12.1.0
- Visual Studio 2022 (Optional - to use .sln file for local build)
- OpenSSL library version 1.1.0  (https://wiki.openssl.org/index.php/Binaries)

### How to use:
`bin_parser.exe <bin_file_path>`
>e.g.: bin_parser.exe C:\Users\dishtjos\output.bin

### Sample output:
`C:\Users\dishtjos>bin_parser.exe C:\Users\dishtjos\output.bin`
```
Device name        : thermostat
Device MAC Address : 9f:4b:22:79:12:cb

Device name        : doorbell
Device MAC Address : f6:dd:3d:6e:ae:13

Device name        : camera
Device MAC Address : 61:30:66:a6:55:61

Device name        : light
Device MAC Address : 96:2b:f6:c7:e9:c9

Device name        : motor
Device MAC Address : 00:00:de:ad:be:ef
```

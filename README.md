# Flow Log Parser

Script to parse flow log data, map records to tags based on a lookup table and count tags.

## Features
- Parses flow log files (Version 2 only).
- Maps records to tags based on port and protocol.
- Outputs statistics for tags and port/protocol combinations.
- Handles case-insensitive matching, tags can map to more than one port/protocol combinations.
- Applies memory map, supports large files.

## Requirements
- Python 3.7
- No external dependencies (uses standard library only).

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/hanjiang498/FlowLogParser.git
   cd FlowLogParser
    ```
   
## Usage

1. **Prepare Input Files**：
   - Place your flow log file（e.g., `flow_logs_sample.txt`）and lookup table file （e.g., `lookup_table_sample.csv`）in the project/data directory.
   - Ensure the lookup table file is in the following format (CSV format):
     ```csv
     dstport,protocol,tag
     443,tcp,sv_P2
     25,tcp,sv_P1
     ```
   - The flow log file should follow this format:
     ```
     2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
     ```

2. **Run the Program**：
   - Execute the following command in the terminal:
     ```bash
     python src/main.py
     ```
     or if the default python version is not python3, use following:
     ```bash
     python3 src/main.py
     ```

3. **Check the Output**：
   - After execution，an `output_time.txt` file will be generated in project/output directory, containing two sections of statistics:
     - **Tag Statistics**：
       ```
       Tag Counts:
       Tag,Count
       sv_P2,1
       sv_P1,1
       Untagged,0
       ```
     - **Port/Protocol Statistics:**：
       ```
       Port/Protocol Combination Counts:
       Port,Protocol,Count
       443,tcp,1
       25,tcp,1
       ```
       
## Tests and Performance Analysis
### Functional Tests
1. **Basic Functionality**:
   - Verified correct mapping of flow logs to tags using provided lookup tables.
   - Confirmed correct output format for tag counts and port/protocol statistics.

2. **Malformed Input**:
   - Tested with malformed flow log entries (e.g., missing fields, invalid data).
   - The flow log should contain: <br> version, account ID, interface ID, source address, dest address, dest port, source port, protocol,  packets, bytes, start time, end time, action log status.
   - script skips malformed lines without crashing.

3. **Empty Files**:
   - Verified handling of empty flow log and lookup table files.
   - script generates a valid output file indicating no data was processed.

4. **Case Insensitivity**:
   - Confirmed protocol matching is case insensitive (e.g., `TCP` matches `tcp`).

5. **Multiple Tags for a Port/Protocol**:
   - Verified logs matching multiple tags update all relevant counts.

### Performance Tests
1. **File Size Scaling**:
   - Processed logs of increasing size:
     - 10 MB: Completed in under 2 seconds using single-threaded `mmap`.

2. **Comparison: `mmap` vs. Regular File I/O**:
   - `mmap` showed ~10% faster processing for large files.

3. **Parallel Processing**:
   - Considered import parallel processing with thread pool, but the management overhead (e.g., thread/process switching, result merging) may outweigh the benefits because the file size can be only 10MB maximum.

### Edge Case Tests
1. Logs with very large numeric fields (e.g., extremely high packet counts).
2. Lookup tables with thousands of entries (e.g., 10,000 mappings).
3. Logs with a mix of supported and unsupported protocols.

### Observations
- For files smaller than **10 MB**, single-threaded processing with `mmap` is sufficient.
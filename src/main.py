import csv
from collections import defaultdict, Counter
import mmap
import os
from datetime import datetime


def load_lookup_table(lookup_file):
    """
    Load the lookup table from a CSV file.

    Args:
        lookup_file (str): Path to the lookup table file.

    Returns:
        dict: A dictionary mapping (dstport, protocol) to a list of tags.
    """
    lookup_table = defaultdict(list)
    with open(lookup_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            dstport = row['dstport'].strip()
            protocol = row['protocol'].strip().lower()
            tag = row['tag'].strip()
            lookup_table[(dstport, protocol)].append(tag)
    return lookup_table


def parse_flow_logs_mmap(flow_file, lookup_table, output_file):
    """
    Parse the flow log file using mmap and map records to tags based on the lookup table.

    Args:
        flow_file (str): Path to the flow log file.
        lookup_table (dict): Mapping of (dstport, protocol) to tags.
        output_file (str): Path to the output file.
    """
    tag_counts = Counter()
    port_protocol_counts = Counter()
    untagged_count = 0

    protocol_map = {"6": "tcp", "17": "udp", "1": "icmp"}

    with open(flow_file, "r+b") as file:
        mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        for line in iter(mmapped_file.readline, b""):
            line = line.decode('utf-8').strip()
            parts = line.split()
            if len(parts) < 14:
                continue  # Skip malformed lines

            dstport = parts[5].strip()
            protocol_number = parts[7].strip()
            # lower case to make sure case-insensitive
            protocol = protocol_map.get(protocol_number, "unknown").lower()

            # Check lookup table for matching tags
            tags = lookup_table.get((dstport, protocol))
            if tags:
                tag_counts.update(tags)
            else:
                untagged_count += 1

            # Count port/protocol combinations
            port_protocol_counts.update([(dstport, protocol)])

    # Write results to the output file
    with open(output_file, "w") as file:
        # Tag counts
        file.write("Tag Counts:\n")
        file.write("Tag,Count\n")
        for tag, count in tag_counts.items():
            file.write(f"{tag},{count}\n")
        file.write(f"Untagged,{untagged_count}\n\n")

        # Port/Protocol combination counts
        file.write("Port/Protocol Combination Counts:\n")
        file.write("Port,Protocol,Count\n")
        for (port, protocol), count in port_protocol_counts.items():
            file.write(f"{port},{protocol},{count}\n")


def main():
    """
    Main function to coordinate the flow log parsing and result generation.
    """
    data_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    flow_file = os.path.join(data_folder, "flow_logs_sample.txt")
    lookup_file = os.path.join(data_folder, "lookup_table_sample.csv")

    output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f"output_{timestamp}.txt")

    lookup_table = load_lookup_table(lookup_file)
    parse_flow_logs_mmap(flow_file, lookup_table, output_file)


if __name__ == "__main__":
    main()

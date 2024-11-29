# Marc2Text2024
A Python script for processing MARC files (.mrc and .marc), cleaning data, handling encoding issues, and logging errors for failed records. The script ensures data quality and generates outputs for successfully processed records while maintaining a detailed log for troubleshooting.

## Features

- Processes MARC files (`.mrc` and `.marc`) in the current directory.
- Cleans MARC8 data and validates record subfields.
- Logs details of failed records, including raw data, for debugging.
- Exports cleaned records to a designated output folder.
- Moves processed files to categorized folders (`processed` or `failed`).
- Generates detailed logs (`marc_processing.log`) and error reports (`failed_records.log`).

## Folder Structure

The script organizes files as follows:

- `output/`: Successfully processed records are saved here.
- `processed/`: Files that were successfully processed are moved here.
- `failed/`: Files with errors are moved here for review.
- Logs:
  - `marc_processing.log`: Detailed logs for the processing operation.
  - `failed_records.log`: Specific information on failed records.
  - `raw_failed_records.marc`: Raw MARC data for failed records.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/kuanding/Marc2Text2024.git
   ```
2. Navigate to the directory:
   ```bash
   cd Marc2Text2024
   ```
3. Install dependencies:
   ```bash
   pip install pymarc
   ```

## Usage

1. Place the MARC files (`.mrc` or `.marc`) in the script's directory.
2. Run the script:
   ```bash
   python Marc2Text2024.py
   ```
3. Check the `output/`, `processed/`, and `failed/` directories for results.

## Logging and Debugging

- Review `marc_processing.log` for general process information.
- Check `failed_records.log` for specific issues with failed records.
- Inspect `raw_failed_records.marc` for raw data of problematic records.

## Error Handling

The script includes robust error handling:
- Invalid MARC8 sequences are cleaned or skipped.
- Failed records are logged and exported for analysis.
- Files with errors are automatically moved to the `failed/` folder.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

[Mick Huang](https://github.com/kuanding)

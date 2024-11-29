import os
import glob
import pymarc
import shutil
import time
import logging
import traceback
from pymarc.marc8 import marc8_to_unicode

# Configure logging
logging.basicConfig(
    filename='marc_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

error_log_path = "failed_records.log"
raw_failed_data_path = "raw_failed_records.marc"

def log_failed_record(record, filename, reason, raw_data=None, index=None):
    """
    Log details of failed records including unique ID, the reason for failure, and raw data.
    """
    unique_id = record['001'] if record and isinstance(record, pymarc.Record) and '001' in record else "Unknown ID"
    index_info = f" (Index: {index})" if index is not None else ""
    raw_data_str = raw_data.decode('utf-8', errors='replace') if raw_data else "Raw data unavailable"

    with open(error_log_path, 'a', encoding='utf-8') as error_log:
        error_log.write(f"File: {filename}{index_info}, Record ID: {unique_id}, Reason: {reason}\n")
        error_log.write(f"Raw Data: {raw_data_str}\n")
        error_log.write("-" * 80 + "\n")
    logging.error(f"Failed Record - File: {filename}{index_info}, Record ID: {unique_id}, Reason: {reason}")

def export_raw_failed_record(raw_data, filename, index):
    """
    Append raw data of a failed record to a raw data export file.
    """
    try:
        with open(raw_failed_data_path, 'ab') as raw_file:
            raw_file.write(f"File: {filename}, Record Index: {index}\n".encode('utf-8'))
            raw_file.write(raw_data)
            raw_file.write(b"\n" + b"-" * 80 + b"\n")
        logging.info(f"Exported raw data of failed record from file {filename} (Index: {index}) to {raw_failed_data_path}")
    except Exception as export_error:
        logging.error(f"Failed to export raw data for record in file {filename} (Index: {index}): {export_error}")
        log_debug_info(export_error)

def log_debug_info(error):
    """
    Log detailed debug information for troubleshooting.
    """
    debug_info = traceback.format_exc()
    logging.error(f"Debug Info:\n{debug_info}")

def clean_marc8_data(raw_data):
    """
    Attempt to clean or fix MARC8 data with invalid characters.
    Returns cleaned data or None if unrecoverable.
    """
    try:
        # Attempt to decode MARC8, ignoring invalid sequences
        return marc8_to_unicode(raw_data, hide_utf8_warnings=True)
    except Exception as e:
        logging.error(f"Error cleaning MARC8 data: {e}")
        return None  # Return None for unrecoverable data

def validate_and_clean_subfields(field):
    """
    Validate and clean subfields in a MARC field.
    """
    if hasattr(field, 'subfields'):
        valid_subfields = []
        for subfield in field.subfields:
            try:
                if subfield and hasattr(subfield, 'code') and hasattr(subfield, 'value'):
                    valid_subfields.append(subfield)
                else:
                    logging.warning(f"Invalid subfield detected and skipped: {subfield}")
            except Exception as e:
                logging.error(f"Error validating subfield: {e}")
        field.subfields = valid_subfields

def clean_record_fields(record):
    """
    Clean all fields of a MARC record for malformed subfields and invalid MARC8 issues.
    """
    for field in record.get_fields():
        validate_and_clean_subfields(field)
    return record

def process_marc_files():
    # Define folder paths relative to the script location
    base_folder = os.getcwd()
    output_folder = os.path.join(base_folder, 'output')
    processed_folder = os.path.join(base_folder, 'processed')
    failed_folder = os.path.join(base_folder, 'failed')

    # Ensure output, processed, and failed folders exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)
    os.makedirs(failed_folder, exist_ok=True)

    # Ensure the raw failed data file is cleared at the start
    if os.path.exists(raw_failed_data_path):
        os.remove(raw_failed_data_path)

    start_time = time.time()  # Start the timer
    total_records_processed = 0  # Counter for total successful records
    total_records_failed = 0  # Counter for total failed records
    total_files_processed = 0  # Counter for total files processed

    # Clear the error log at the start
    if os.path.exists(error_log_path):
        os.remove(error_log_path)

    # Loop through all MARC files with extensions .mrc and .marc in the base folder
    for file_extension in ['*.mrc', '*.marc']:
        for filename in glob.glob(os.path.join(base_folder, file_extension)):
            total_files_processed += 1
            file_has_errors = False  # Flag to track if any record failed in the current file
            try:
                logging.info(f"Processing file: {filename}")

                # Process the MARC file
                with open(filename, 'rb') as fh:
                    reader = pymarc.MARCReader(fh, to_unicode=True, force_utf8=False)

                    # Create a corresponding output file
                    output_filename = os.path.join(
                        output_folder, os.path.splitext(os.path.basename(filename))[0] + '.txt'
                    )
                    with open(output_filename, 'a', encoding='utf-8') as output_file:
                        # Loop through MARC records
                        record_index = 0
                        for record in reader:
                            record_index += 1
                            try:
                                record = clean_record_fields(record)  # Clean the record fields
                                output_file.write(str(record))
                                output_file.write('\n\n')
                                total_records_processed += 1
                                record_id = record['001'] if '001' in record else "Unknown ID"
                                logging.info(f"Processed record {record_index} from file: {filename}, Record ID: {record_id}")
                            except Exception as record_error:
                                # Log and export raw data of malformed record
                                raw_data = reader.current_chunk
                                export_raw_failed_record(raw_data, filename, record_index)
                                log_failed_record(None, filename, str(record_error), raw_data=raw_data, index=record_index)
                                log_debug_info(record_error)
                                total_records_failed += 1
                                file_has_errors = True

                # Move the file to the appropriate folder based on whether errors occurred
                if file_has_errors:
                    shutil.move(filename, os.path.join(failed_folder, os.path.basename(filename)))
                    logging.info(f"File moved to failed folder: {filename}")
                else:
                    shutil.move(filename, os.path.join(processed_folder, os.path.basename(filename)))
                    logging.info(f"File processed and moved to processed folder: {filename}")

            except Exception as e:
                # Move the failed file to the 'failed' folder
                try:
                    shutil.move(filename, os.path.join(failed_folder, os.path.basename(filename)))
                    logging.info(f"File moved to failed folder: {filename}")
                except Exception as move_error:
                    logging.error(f"Failed to move file {filename} to failed folder: {move_error}")
                logging.error(f"Error processing file {filename}: {e}")
                log_debug_info(e)

    end_time = time.time()  # Stop the timer

    # Calculate the total process time
    total_time = end_time - start_time

    # Print and log the summary
    summary_message = (f"Total files processed: {total_files_processed}\n"
                       f"Total records processed: {total_records_processed}\n"
                       f"Total records failed: {total_records_failed}\n"
                       f"Total processing time: {total_time:.2f} seconds")
    logging.info(summary_message)

if __name__ == "__main__":
    process_marc_files()

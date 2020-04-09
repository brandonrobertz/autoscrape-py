import logging
from multiprocessing import Pool
import os
import pickle

try:
    import plyvel
    # TODO: replace with warcio
    import warc
except ModuleNotFoundError:
    pass


logger = logging.getLogger('AUTOSCRAPE')


def _warc_record_sane(record):
    if record.type != "response":
        return False
    if "WARC-Target-URI" not in record:
        return False
    return True


def _warc_records(filename):
    records = []
    try:
        for record in warc.open(filename):
            records.append(record)
    except Exception as e:
        logger.error("[!] Error opening WARC file %s" % (filename))
        logger.error(e)
    return records


def _process_warcfile(filepath, filter_domain):
    found = 0
    if not filepath.endswith(".warc.gz"):
        return []
    logger.debug(" - Parsing %s" % (filepath))
    record_number = -1
    results = []
    for record in _warc_records(filepath):
        if not _warc_record_sane(record):
            continue
        record_number += 1
        uri = record["WARC-Target-URI"]
        if filter_domain and filter_domain not in uri:
            continue
        logger.debug("URI: %s" % (uri))
        found += 1
        uri_bytes = bytes(uri, "utf-8")
        value = pickle.dumps((filepath, record_number))
        results.append((uri_bytes, value))
    if found:
        logger.debug(" - Found %s records" % (found))
    return results


def build_warc_index(db=None, warc_directory=None, filter_domain=None):
    """
    Read through all WARC files in warc_directory and build
    an index: URL => filename, record_number
    """
    blank = True
    for rec in db.iterator():
        blank = False
        break
    if not blank:
        logger.debug("[.] Already loaded WARC index.")
        return
    logger.info("[.] Building WARC index. This might take a while...")
    _, _, filenames = list(os.walk(warc_directory))[0]
    filepaths = [(os.path.join(warc_directory, n), filter_domain) for n in filenames]
    print(filepaths[0])

    with Pool(8) as f:
        results_groups = f.starmap(_process_warcfile, filepaths)
    for results in results_groups:
        for uri_bytes, value in results:
            db.put(uri_bytes, value)

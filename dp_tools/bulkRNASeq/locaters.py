""" Tools for finding specific paths 

These should rely on configuratble files to accommodate changing directory structures.
For now, the regexes will be hardcoded.

Such Locators SHOULD:
  - have find function that returns the path
  - search starting at root data directory
  - any RE patterns should be relative to the search_path
"""
import os
from pathlib import Path
from typing import List, Protocol, Tuple, runtime_checkable
import re
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def _rIterDir(p: Path) -> List[Path]:
    return [f for f in p.rglob("*")]


@runtime_checkable
class Locator(Protocol):
    def find(self, **kwargs) -> Path:
        """ Find a specific path """
        ...


class MultiQCDir:

    EXACT_PATH_FORMAT = os.path.join("{rel_dir}", "{mqc_label}_multiqc_report")

    def __init__(self, search_root: Path):
        self.search_root = search_root

    def find(self, rel_dir: Path, mqc_label: str) -> Path:
        found = list()
        # replace needed for regex to interpret regex escape characters AFTER interpretting python escape characters
        # (i.e. accomodate windows using the same separator as the escape char)
        pattern = self.EXACT_PATH_FORMAT.format(rel_dir=str(rel_dir), mqc_label=mqc_label).replace(
        "\\", r"\\"
    )
        log.debug(
            f"Locating multiQC direcotry {type(self).__name__} with pattern: {pattern}"
        )

        putative_found = self.search_root / pattern
        assert putative_found.exists(), f"Target does not exist. Expected: {putative_found}. Pattern: {pattern}"
        found.append(putative_found)

        # Here is where additional validation should occur if the main found resource is a path (e.g. the RSEM stat folder)
        assert (
            len(found) == 1
        ), f"One and only find target should occur. Found: {found}. Pattern: {pattern}"
        return found[0]

class FastqcReport:
    EXACT_PATH_FORMAT = {
        "Raw": {
            "Forward": os.path.join(
                "00-RawData", "FastQC_Reports", "{sample_name}_R1_raw_fastqc.{ext}"
            ),
            "Reverse": os.path.join(
                "00-RawData", "FastQC_Reports", "{sample_name}_R2_raw_fastqc.{ext}"
            ),
        },
        "Trimmed": {
            "Forward": os.path.join(
                "01-TG_Preproc", "FastQC_Reports", "{sample_name}_R1_trimmed_fastqc.{ext}"
            ),
            "Reverse": os.path.join(
                "01-TG_Preproc", "FastQC_Reports", "{sample_name}_R2_trimmed_fastqc.{ext}"
            ),
        },
    }

    def __init__(self, search_root: Path):
        self.search_root = search_root

    def find(self, sample_name: str, type: Tuple[str, str], ext: str) -> Path:
        found = list()
        # replace needed for regex to interpret regex escape characters AFTER interpretting python escape characters
        # (i.e. accomodate windows using the same separator as the escape char)
        pattern = (
            self.EXACT_PATH_FORMAT[type[0]][type[1]]
            .format(sample_name=sample_name, ext=ext)
            .replace("\\", r"\\")
        )
        log.debug(f"Locating raw fastqgz file {sample_name} with pattern: {pattern}")

        putative_found = self.search_root / pattern
        assert putative_found.exists(), f"Target does not exist. Expected: {putative_found}. Pattern: {pattern}"
        found.append(putative_found)

        # Here is where additional validation should occur if the main found resource is a path (e.g. the RSEM stat folder)
        assert (
            len(found) == 1
        ), f"One and only find target should occur. Found: {found}. Pattern: {pattern}"
        return found[0]

class Runsheet:
    # replace needed for regex to interpret regex escape characters AFTER interpretting python escape characters
    # (i.e. accomodate windows using the same separator as the escape char)
    EXACT_PATH_FORMAT = os.path.join(
        "Metadata",
        "AST_autogen_template_RNASeq_RCP_{datasystem_name}_RNASeq_runsheet.csv",
    ).replace("\\", r"\\")

    def __init__(self, search_root: Path):
        self.search_root = search_root

    def find(self, datasystem_name: str) -> Path:
        found = list()
        pattern = self.EXACT_PATH_FORMAT.format(datasystem_name=datasystem_name)
        log.debug(
            f"Locating {type(self).__name__} file {datasystem_name} with pattern: {pattern}"
        )

        putative_found = self.search_root / pattern
        assert putative_found.exists(), f"Target does not exist. Expected: {putative_found}. Pattern: {pattern}"
        found.append(putative_found)

        # Here is where additional validation should occur if the main found resource is a path (e.g. the RSEM stat folder)
        assert (
            len(found) == 1
        ), f"One and only find target should occur. Found: {found}. Pattern: {pattern}"
        return found[0]

class Fastq:
    EXACT_PATH_FORMAT = {
        "Raw": {
            "Forward": os.path.join(
                "00-RawData", "Fastq", "{sample_name}_R1_raw.fastq.gz"
            ),
            "Reverse": os.path.join(
                "00-RawData", "Fastq", "{sample_name}_R2_raw.fastq.gz"
            ),
        },
        "Trimmed": {
            "Forward": os.path.join(
                "01-TG_Preproc", "Fastq", "{sample_name}_R1_trimmed.fastq.gz"
            ),
            "Reverse": os.path.join(
                "01-TG_Preproc", "Fastq", "{sample_name}_R2_trimmed.fastq.gz"
            ),
        },
    }

    def __init__(self, search_root: Path):
        self.search_root = search_root

    def find(self, sample_name: str, type: Tuple[str, str]) -> Path:
        found = list()
        # replace needed for regex to interpret regex escape characters AFTER interpretting python escape characters
        # (i.e. accomodate windows using the same separator as the escape char)
        pattern = (
            self.EXACT_PATH_FORMAT[type[0]][type[1]]
            .format(sample_name=sample_name)
            .replace("\\", r"\\")
        )
        log.debug(f"Locating raw fastqgz file {sample_name} with pattern: {pattern}")

        putative_found = self.search_root / pattern
        assert putative_found.exists(), f"Target does not exist. Expected: {putative_found}. Pattern: {pattern}"
        found.append(putative_found)

        # for i, p in enumerate(_rIterDir(self.search_root)):
        #     if re.match(pattern, str(p.relative_to(self.search_root))):
        #         found.append(p)

        # Here is where additional validation should occur if the main found resource is a path (e.g. the RSEM stat folder)
        assert (
            len(found) == 1
        ), f"One and only find target should occur. Found: {found}. Pattern: {pattern}"
        return found[0]


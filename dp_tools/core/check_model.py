#########################################################################
# FLAG (A validation report message)
#########################################################################
import abc
from dataclasses import dataclass, field
import enum
import re
from typing import (
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
)
import logging
from dp_tools.core.entity_model import (
    TemplateComponent,
    TemplateDataset,
    TemplateSample,
)

log = logging.getLogger(__name__)

from dp_tools.core.model_commons import strict_type_checks

ALLOWED_DEV_EXCEPTIONS = (
    Exception  # Hooking into this with monkeypatch can be handy for testing
)


class FlagCode(enum.Enum):
    """ Maps a flag code to a severity level. """

    DEV_HANDLED = 90  # should be used when an error occurs due to developer related mistakes, rather than from the correctly loaded data
    DEV_UNHANDLED = 91  # should never be used directly, instead this should catch unhandled exceptions in the validate function
    HALT1 = 80
    HALT2 = 80
    HALT3 = 80
    HALT4 = 80
    HALT5 = 80
    RED1 = 50
    RED2 = 50
    RED3 = 50
    RED4 = 50
    RED5 = 50
    YELLOW1 = 30
    YELLOW2 = 30
    YELLOW3 = 30
    YELLOW4 = 30
    YELLOW5 = 30
    GREEN = 20
    INFO = 10


@dataclass
class Check(abc.ABC):

    description: str
    id: str
    flag_desc: Dict[int, str]
    validate_func: Optional[Callable]
    # flags associated with this check
    flags: List["Flag"] = field(default_factory=list)
    config: Dict = field(default_factory=dict)
    allChecks: ClassVar[
        List["Check"]
    ] = list()  # note this is a class attribute list, tracking all checks

    def __post_init__(self):
        # format description with config
        # All templated fields MUST be in config
        # All items in config are NOT required
        # (however, they should be supplied to make the description complete)
        self._proto_description = self.description
        self.description = self.description.format(**self.config)

        # ensure checkID is valid
        assert re.match(
            r"^(COMPONENT|SAMPLE|DATASET)_\D*_\d\d\d\d$", self.id
        ), "Valid Check ID format: SCOPE_WORD_dddd where d is any digit. SCOPE must be either 'COMPONENT','SAMPLE' or 'DATASET'"

        # ensure check is unique
        assert self.id not in [
            check.id for check in self.allChecks
        ], "CheckID already used, try another ID"

        # add to tracked allChecks
        self.allChecks.append(self)

        # add flag description for unhandled developer exception flags
        self.flag_desc[
            FlagCode.DEV_UNHANDLED
        ] = "An unhandled exception occured in {function}: {e}"

    def validate(self, *args, **kwargs):
        try:
            return self.validate_func(self, *args, **kwargs)
        except ALLOWED_DEV_EXCEPTIONS as e:
            log.critical(
                f"Developer exception raised during a validation function for check: {self}"
            )
            return Flag(
                code=FlagCode.DEV_UNHANDLED,
                message_args={"function": self.validate_func, "e": e},
                check=self,
            )

    def copy_with_new_config(self, id: str, config: dict) -> "Check":
        return Check(
            id=id,
            config=config,
            description=self._proto_description,
            validate_func=self.validate_func,
            flag_desc=self.flag_desc,
        )


@dataclass
class Flag:

    code: FlagCode
    check: Check
    message_args: dict = field(default_factory=dict)
    message: str = field(init=False)

    # must ensure all flags are correct before continuing
    def __post_init__(self):

        # retrieve proto message
        pre_format_msg = self.check.flag_desc[self.code]

        # populate message with message_args
        self.message = pre_format_msg.format(**self.message_args)

        # check types before final addition and init
        strict_type_checks(self)
        # add to check flags records
        self.check.flags.append(self)


class VVProtocol(abc.ABC):
    """ A abstract protocol for VV """

    def __init__(self, dataset):
        # check on init that dataset is of the right type
        assert isinstance(
            dataset, self.expected_dataset_class
        ), "dataset MUST be of type 'BulkRNASeqDataset' for this protocol"
        self.dataset = dataset
        self._flags = {"dataset": dict(), "sample": dict(), "component": dict()}

    @property
    def flags(self):
        return self._flags

    @abc.abstractproperty
    @property
    def expected_dataset_class(self):
        return self.expected_dataset_class

    def validate_all(self):
        self._flags["dataset"].update(self.validate_dataset())
        self._flags["sample"].update(self.validate_samples())
        self._flags["component"].update(self.validate_components())

    @abc.abstractmethod
    def validate_dataset(self) -> Dict[TemplateDataset, List[Flag]]:
        ...

    @abc.abstractmethod
    def validate_samples(self) -> Dict[TemplateSample, List[Flag]]:
        ...

    @abc.abstractmethod
    def validate_components(self) -> Dict[TemplateComponent, List[Flag]]:
        ...
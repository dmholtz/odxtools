# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from typing import List, Optional
from xml.etree import ElementTree

from ..odxlink import OdxDocFragment
from ..odxtypes import DataType
from ..progcode import ProgCode
from .compudefaultvalue import CompuDefaultValue
from .compuscale import CompuScale


@dataclass
class CompuPhysToInternal:
    compu_scales: List[CompuScale]
    prog_code: Optional[ProgCode]
    compu_default_value: Optional[CompuDefaultValue]

    @staticmethod
    def compu_phys_to_internal_from_et(et_element: ElementTree.Element,
                                       doc_frags: List[OdxDocFragment], *, internal_type: DataType,
                                       physical_type: DataType) -> "CompuPhysToInternal":
        compu_scales = [
            CompuScale.compuscale_from_et(
                cse, doc_frags, internal_type=internal_type, physical_type=physical_type)
            for cse in et_element.iterfind("COMPU-SCALES/COMPU-SCALE")
        ]

        prog_code = None
        if (pce := et_element.find("PROG-CODE")) is not None:
            prog_code = ProgCode.from_et(pce, doc_frags)

        compu_default_value = None
        if (cdve := et_element.find("COMPU-DEFAULT-VALUE")) is not None:
            compu_default_value = CompuDefaultValue.from_et(cdve, doc_frags)

        return CompuPhysToInternal(
            compu_scales=compu_scales, prog_code=prog_code, compu_default_value=compu_default_value)

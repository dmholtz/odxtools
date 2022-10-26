# SPDX-License-Identifier: MIT
# Copyright (c) 2022 MBition GmbH

import inspect
import os
from typing import NamedTuple, cast
import unittest
from xml.etree import ElementTree
import jinja2

import odxtools
from odxtools.utils import short_name_as_id
from odxtools.audience import AdditionalAudience, Audience
from odxtools.compumethods import CompuScale, Limit, LinearCompuMethod, TexttableCompuMethod
from odxtools.dataobjectproperty import DataObjectProperty
from odxtools.diagcodedtypes import StandardLengthType
from odxtools.diaglayer import DiagLayer
from odxtools.functionalclass import FunctionalClass
from odxtools.nameditemlist import NamedItemList
from odxtools.odxtypes import DataType
from odxtools.physicaltype import PhysicalType
from odxtools.singleecujob import read_single_ecu_job_from_odx, SingleEcuJob, ProgCode, InputParam, OutputParam, NegOutputParam
from odxtools.write_pdx_file import jinja2_odxraise_helper
from odxtools.odxlink import OdxLinkId, OdxLinkRef, OdxLinkDatabase, OdxDocFragment

doc_frags = [ OdxDocFragment("UnitTest", "WinneThePoh") ]

class TestSingleEcuJob(unittest.TestCase):

    def setUp(self) -> None:
        """Create three objects:

        * self.singleecujob_object: SingleEcuJob - job to be tested
        * self.context: NamedTuple - elements referenced by the SingleEcuJob
        * self.singleecujob_odx: string - odx description of self.singleecujob_object
        """
        super().setUp()

        class Context(NamedTuple):
            """odx elements referenced by the tested single ECU job, i.e., elements needed in the `odxlinks` when resolving references"""
            extensiveTask: FunctionalClass
            specialAudience: AdditionalAudience
            inputDOP: DataObjectProperty
            outputDOP: DataObjectProperty
            negOutputDOP: DataObjectProperty

        self.context = Context(

            extensiveTask=FunctionalClass(
                odx_link_id=OdxLinkId("ID.extensiveTask", doc_frags), short_name="extensiveTask"),

            specialAudience=AdditionalAudience(
                odx_link_id=OdxLinkId("ID.specialAudience", doc_frags), short_name="specialAudience"),

            inputDOP=DataObjectProperty(
                odx_link_id=OdxLinkId("ID.inputDOP", doc_frags),
                short_name="inputDOP",
                diag_coded_type=StandardLengthType(
                    DataType.A_INT32, bit_length=1),
                physical_type=PhysicalType(DataType.A_UNICODE2STRING),
                compu_method=TexttableCompuMethod(
                    internal_to_phys=[
                        CompuScale("yes", lower_limit=Limit(
                            0), compu_const="Yes!"),
                        CompuScale("no", lower_limit=Limit(
                            1), compu_const="No!"),
                    ],
                    internal_type=DataType.A_UINT32
                )
            ),

            outputDOP=DataObjectProperty(
                odx_link_id=OdxLinkId("ID.outputDOP", doc_frags),
                short_name="outputDOP",
                diag_coded_type=StandardLengthType(
                    DataType.A_INT32, bit_length=1),
                physical_type=PhysicalType(DataType.A_UNICODE2STRING),
                compu_method=LinearCompuMethod(1, -1,
                                               internal_type=DataType.A_UINT32, physical_type=DataType.A_UINT32)
            ),

            negOutputDOP=DataObjectProperty(
                odx_link_id=OdxLinkId("ID.negOutputDOP", doc_frags),
                short_name="negOutputDOP",
                diag_coded_type=StandardLengthType(
                    DataType.A_INT32, bit_length=1),
                physical_type=PhysicalType(DataType.A_UNICODE2STRING),
                compu_method=LinearCompuMethod(1, -1,
                                               internal_type=DataType.A_UINT32, physical_type=DataType.A_UINT32)
            )
        )

        input_params=[
            InputParam(
                short_name="inputParam",
                physical_default_value="Yes!",
                dop_base_ref=OdxLinkRef.from_id(self.context.inputDOP.odx_link_id)
            )
        ]
        output_params=[
            OutputParam(
                odx_link_id=OdxLinkId("ID.outputParam", doc_frags),
                semantic="DATA",
                short_name="outputParam",
                long_name="The Output Param",
                description="<p>The one and only output of this job.</p>",
                dop_base_ref=OdxLinkRef.from_id(self.context.outputDOP.odx_link_id)
            )
        ]
        neg_output_params=[
            NegOutputParam(
                short_name="NegativeOutputParam",
                description="<p>The one and only output of this job.</p>",
                dop_base_ref=OdxLinkRef.from_id(self.context.negOutputDOP.odx_link_id)
            )
        ]

        self.singleecujob_object = SingleEcuJob(
            odx_link_id=OdxLinkId("ID.JumpStart", doc_frags),
            short_name="JumpStart",
            functional_class_refs=[OdxLinkRef.from_id(self.context.extensiveTask.odx_link_id)],
            audience=Audience(
                enabled_audience_refs=[OdxLinkRef.from_id(self.context.specialAudience.odx_link_id)]
            ),
            prog_codes=[
                ProgCode(
                    code_file="abc.jar",
                    encryption="RSA512",
                    syntax="JAR",
                    revision="0.12.34",
                    entrypoint="CalledClass",
                    library_refs=[
                        OdxLinkRef("my.favourite.lib", doc_frags)
                    ]
                )
            ],
            input_params=input_params,
            output_params=output_params,
            neg_output_params=neg_output_params,
        )

        self.singleecujob_odx = f"""
            <SINGLE-ECU-JOB ID="{self.singleecujob_object.odx_link_id.local_id}">
                <SHORT-NAME>{self.singleecujob_object.short_name}</SHORT-NAME>
                <FUNCT-CLASS-REFS>
                    <FUNCT-CLASS-REF ID-REF="{self.singleecujob_object.functional_class_refs[0].ref_id}"/>
                </FUNCT-CLASS-REFS>
                <AUDIENCE>
                    <ENABLED-AUDIENCE-REFS>
                        <ENABLED-AUDIENCE-REF ID-REF="{cast(Audience, self.singleecujob_object.audience).enabled_audience_refs[0].ref_id}"/>
                    </ENABLED-AUDIENCE-REFS>
                </AUDIENCE>
                <PROG-CODES>
                    <PROG-CODE>
                        <CODE-FILE>{self.singleecujob_object.prog_codes[0].code_file}</CODE-FILE>
                        <ENCRYPTION>{self.singleecujob_object.prog_codes[0].encryption}</ENCRYPTION>
                        <SYNTAX>{self.singleecujob_object.prog_codes[0].syntax}</SYNTAX>
                        <REVISION>{self.singleecujob_object.prog_codes[0].revision}</REVISION>
                        <ENTRYPOINT>{self.singleecujob_object.prog_codes[0].entrypoint}</ENTRYPOINT>
                        <LIBRARY-REFS>
                            <LIBRARY-REF ID-REF="{self.singleecujob_object.prog_codes[0].library_refs[0].ref_id}"/>
                        </LIBRARY-REFS>
                    </PROG-CODE>
                </PROG-CODES>
                <INPUT-PARAMS>
                    <INPUT-PARAM>
                        <SHORT-NAME>{input_params[0].short_name}</SHORT-NAME>
                        <PHYSICAL-DEFAULT-VALUE>{input_params[0].physical_default_value}</PHYSICAL-DEFAULT-VALUE>
                        <DOP-BASE-REF ID-REF="{input_params[0].dop_base_ref.ref_id}"/>
                    </INPUT-PARAM>
                </INPUT-PARAMS>
                <OUTPUT-PARAMS>
                    <OUTPUT-PARAM ID="{output_params[0].odx_link_id.local_id}" SEMANTIC="{output_params[0].semantic}">
                        <SHORT-NAME>{output_params[0].short_name}</SHORT-NAME>
                        <LONG-NAME>{output_params[0].long_name}</LONG-NAME>
                        <DESC>\n{output_params[0].description}\n</DESC>
                        <DOP-BASE-REF ID-REF="{output_params[0].dop_base_ref.ref_id}"/>
                    </OUTPUT-PARAM>
                </OUTPUT-PARAMS>
                <NEG-OUTPUT-PARAMS>
                    <NEG-OUTPUT-PARAM>
                        <SHORT-NAME>{neg_output_params[0].short_name}</SHORT-NAME>
                        <DESC>\n{neg_output_params[0].description}\n</DESC>
                        <DOP-BASE-REF ID-REF="{neg_output_params[0].dop_base_ref.ref_id}"/>
                    </NEG-OUTPUT-PARAM>
                </NEG-OUTPUT-PARAMS>
            </SINGLE-ECU-JOB>
        """

    def test_read_odx(self):
        expected = self.singleecujob_object
        sample_single_ecu_job_odx = self.singleecujob_odx
        et_element = ElementTree.fromstring(sample_single_ecu_job_odx)
        sej = read_single_ecu_job_from_odx(et_element, doc_frags=doc_frags)
        self.assertEqual(expected.prog_codes, sej.prog_codes)
        self.assertEqual(expected.output_params, sej.output_params)
        self.assertEqual(expected.neg_output_params,
                         sej.neg_output_params)

        self.assertEqual(expected, sej)

    def test_write_odx(self):
        # Setup jinja environment
        __module_filename = inspect.getsourcefile(odxtools)
        assert isinstance(__module_filename, str)
        stub_dir = os.path.sep.join([os.path.dirname(__module_filename),
                                     "pdx_stub"])
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(stub_dir))
        jinja_env.globals['odxraise'] = jinja2_odxraise_helper
        jinja_env.filters["odxtools_collapse_xml_attribute"] = (
            lambda x: " " + x.strip() if x.strip() else "")

        # Small template
        template = jinja_env.from_string("""
            {%- import('macros/printSingleEcuJob.tpl') as psej %}
            {{psej.printSingleEcuJob(singleecujob)}}
        """)

        rawodx: str = template.render(singleecujob=self.singleecujob_object)

        # Remove whitespace
        actual = rawodx.replace(" ", "")
        expected = self.singleecujob_odx.replace(" ", "")

        # Assert equality of outputted string
        self.assertEqual(expected, actual)

        # Assert equality of objects
        # This tests the idempotency of read-write
        sej = read_single_ecu_job_from_odx(ElementTree.fromstring(rawodx), doc_frags=doc_frags)
        self.assertEqual(self.singleecujob_object, sej)

    def test_default_lists(self):
        """Test that empty lists are assigned to list-attributes if no explicit value is passed."""
        sej = SingleEcuJob(
            odx_link_id=OdxLinkId("ID.SomeID", doc_frags),
            short_name="SN.SomeShortName",
            prog_codes=[
                ProgCode(
                    code_file="abc.jar",
                    syntax="abc",
                    revision="12.34"
                )
            ]
        )
        self.assertEqual(sej.functional_class_refs, [])
        self.assertEqual(sej.input_params, NamedItemList(short_name_as_id, []))
        self.assertEqual(sej.output_params, NamedItemList(short_name_as_id, []))
        self.assertEqual(sej.neg_output_params, NamedItemList(short_name_as_id, []))
        self.assertEqual(sej.prog_codes[0].library_refs, [])

    def test_resolve_references(self):
        dl = DiagLayer(variant_type="BASE-VARIANT",
                       odx_link_id=OdxLinkId("ID.bv", doc_frags),
                       short_name="bv",
                       single_ecu_jobs=[self.singleecujob_object])
        odxlinks = OdxLinkDatabase()
        odxlinks.update({val.odx_link_id: val for val in self.context})

        dl._resolve_references(odxlinks)

        self.assertEqual(self.context.extensiveTask,
                         self.singleecujob_object.functional_classes.extensiveTask)
        self.assertEqual(self.context.specialAudience,
                         self.singleecujob_object.audience.enabled_audiences[0])

        self.assertEqual(self.context.inputDOP,
                         self.singleecujob_object.input_params[0].dop)
        self.assertEqual(self.context.outputDOP,
                         self.singleecujob_object.output_params[0].dop)
        self.assertEqual(self.context.negOutputDOP,
                         self.singleecujob_object.neg_output_params[0].dop)


if __name__ == '__main__':
    unittest.main()

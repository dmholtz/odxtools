{#- -*- mode: sgml; tab-width: 1; indent-tabs-mode: nil -*-
 #
 # SPDX-License-Identifier: MIT
 # Copyright (c) 2022 MBition GmbH
-#}

{%- import('macros/printAudience.tpl') as paud %}

{%- macro printService(service) -%}
{%- if service.semantic is not none %}
{%-  set semattrib = " SEMANTIC=\""+service.semantic+"\"" -%}
{%- else %}
{%-  set semattrib = " SEMANTIC=\"UNKNOWN\"" -%}
{%- endif -%}
<DIAG-SERVICE ID="{{service.odx_link_id.local_id}}" {{semattrib}}>
 <SHORT-NAME>{{service.short_name}}</SHORT-NAME>
{%- if service.long_name and service.long_name.strip() %}
 <LONG-NAME>{{service.long_name|e}}</LONG-NAME>
{%- endif %}
{%- if service.description and service.description.strip() %}
 <DESC>
 {{service.description}}
 </DESC>
{%- endif %}
{%- if service.functional_class_refs %}
 <FUNCT-CLASS-REFS>
{%- for ref in service.functional_class_refs %}
  <FUNCT-CLASS-REF ID-REF="{{ref.ref_id}}" />
{%- endfor %}
 </FUNCT-CLASS-REFS>
{%- endif%}
{%- if service.audience %}
 {{ paud.printAudience(service.audience)|indent(1) }}
{%- endif%}
 <REQUEST-REF ID-REF="{{service.request_ref.ref_id}}"/>
{%- if service.pos_res_refs %}
 <POS-RESPONSE-REFS>
{%- for ref in service.pos_res_refs %}
  <POS-RESPONSE-REF ID-REF="{{ref.ref_id}}" />
{%- endfor %}
 </POS-RESPONSE-REFS>
{%- endif%}
{%- if service.neg_res_refs %}
 <NEG-RESPONSE-REFS>
{%- for ref in service.neg_res_refs %}
  <NEG-RESPONSE-REF ID-REF="{{ref.ref_id}}" />
{%- endfor %}
 </NEG-RESPONSE-REFS>
{%- endif%}
</DIAG-SERVICE>
{%- endmacro -%}

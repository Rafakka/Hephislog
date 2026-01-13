# MUSIC FLOW

## PURPOSE:

This flow processes a music-related URL, extracts lyrics and chords, and produces a structured JSON representation suitable
for downstream use.

## HIGH-LEVEL-FLOW (Agent-Oriented)

system.input_received

-> SnifferAgent (1)
system.external_input

-> GatekeeperAgent
system.input_to_be_identified

-> IdentifierAgent
system.input_identified

-> UniversalExtractorAgent
system.extraction.completed

-> SnifferAgent (2)
system.smells.to.advisor

-> RawMaterialAdvisorAgent
system.advisor.to.html.cleaner

-> HtmlCleanerAgent
system.cleaner.to.sniffer

-> SnifferAgent (3)
system.smells.to.decisionagent

-> DecisionAgent
intent.organize.music

-> OrganizerAgent
music.organized

-> NormalizerAgent
music.normalized

-> UniversalPackerAgent
music.pipeline_finished

-> FinalizerAgent
system.run.completed

-> ReportAgent

---

## Notes:
 
**SnifferAgent** appears multiple times in this flow.
Each appearance represents a different confidence stage in domain interference, allowing the DecisionAgentto select the correct
domain based on accumulated signals.

## EVENT TIMELINE

1.system.input_received
2.system.external_input
3.system.input_to_be_identified
4.system.input_identified
5.system.extraction.completed
6.system.smells.to.advisor
7.system.advisor.to.html.cleaner
8.system.cleaner.to.sniffer
9.system.smells.to.decisionagent
10.intent.organize.music
11.music.organized
12.music.normalized
13.music.pipeline_finished
14.system.run.completed

## AGENTS AND RESPONSABILITIES

### SnifferAgent

    This agent sniffs and scents data, it evaluates and annotates incoming data with probabilitics domain signals, 
    it has three phases where:

    1. Sniffs and scents the first assumptions of what can be the data.
    2. Sniffs again after extraction of data, and make scents weaker or stronger.
    3. Sniffs the third time to advise strongly of what can be based on all previews scents and sniffs.

### GatekeeperAgent

    This agent is simple, it fowards validated input into the system event pipeline.

### IdentifierAgent

    This agent tries to identify based on shape of the data and smells it was scented by SnifferAgent.

### UniversalExtractorAgent

    This agent tries to extract data into a parseable data shape, based on scents by SnifferAgent, 
    and the advise of type by IdentifierAgent.

### RawMaterialAdvisorAgent

    This agent advises in how to clean the data, none, light and heavy cleaning.

### HtmlCleanerAgent

    This is a especific agent that performs structural and semantic cleanup of HTML into flow-consumable data.

### DecisionAgent

    This agent decides where it lies the 'domain' of the data, based on scent (the third scenting session of SnifferAgent).

### OrganizerAgent

    This agent organizes data matching lyrics lines and chord lines.

### NormalizerAgent

    This agent canonizes data shape though nested music schemas.

### UniversalPackerAgent

    This agent is an agnostic agent that serializes validated domain data into a standardized JSON output format.

### FinalizerAgent

    This agent saves the json and closes the flow.

### ReportAgent

    This agent trigger when flow stops, if he completes successifully or not. It always give information about the current flow,
    it reports what happened that stopped the flow.

## SCHEMAS

- ChordLineSchema
- ChordSectionSchema
- ChordSheetSchema

## PERSISTENCE & OUTPUT

- Outputs are written to the data/music/directory
- Filenames are derived from sanitized titles
- JSON output is domain-stable and schema-valited

## FAILURE MODES & GUARDS

- Missing or invalid input
- Extraction failure
- Empty organized sections
- Schema validation erros

Each failure emits a corresponding events and terminates the flow safetly.

---

## DESIGN NOTES

- Event-driven, loosely coupled agents
- Domain interference though progressive scenting
- Schema enforcement occurs only after organization
- Packer remains domain-agnostic by design
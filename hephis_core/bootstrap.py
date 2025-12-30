
from hephis_core.agents.confidence_agent import ConfidenceAgent
from hephis_core.agents.sniffer_agent import SnifferAgent
from hephis_core.agents.gatekeeper_agent import GatekeeperAgent
from hephis_core.agents.identifier_agent import IdentifierAgent
from hephis_core.agents.universal_extractor_agent import UniversalExtractorAgent
from hephis_core.agents.decision_agent import DecisionAgent
from hephis_core.agents.normalizer_agent import NormalizerAgent
from hephis_core.agents.organizer_agent import OrganizerAgent
from hephis_core.agents.universal_packer_agent import UniversalPackerAgent
from hephis_core.agents.universal_retriever_agent import UniversalRetrieverAgent
from hephis_core.agents.finalizer_agent import FinalizerAgent
from hephis_core.agents.reporter_agent import ReporterAgent

print("BOOSTRAP CALLED")

def bootstrap_agents():
    ReporterAgent(rules=REPORTER_RULES)
    ConfidenceAgent()
    SnifferAgent()    
    GatekeeperAgent()
    IdentifierAgent()
    UniversalExtractorAgent()
    DecisionAgent()
    NormalizerAgent()
    OrganizerAgent()
    UniversalPackerAgent()
    UniversalRetrieverAgent()
    FinalizerAgent()
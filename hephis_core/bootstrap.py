from hephis_core.services.detectors.raw_detectors import RAW_DOMAIN_DETECTOR
from hephis_core.agents.confidence_agent import ConfidenceAgent
from hephis_core.agents.sniffer_agent import SnifferAgent
from hephis_core.agents.url_fetcher_agent import UrlFetcherAgent
from hephis_core.agents.garbage_analiser_agent import GarbageAnaliserAgent
from hephis_core.agents.garbage_cleaner_agent import GarbageCleanerAgent
from hephis_core.agents.gatekeeper_agent import GatekeeperAgent
from hephis_core.agents.cores.identifier_core import IdentifierCore
from hephis_core.agents.identifier_agent import IdentifierAgent
from hephis_core.agents.universal_extractor_agent import UniversalExtractorAgent
from hephis_core.agents.raw_material_advisor_agent import RawMaterialAdvisorAgent
from hephis_core.agents.html_cleaner_agent import HtmlCleanerAgent
from hephis_core.agents.decision_agent import DecisionAgent
from hephis_core.agents.normalizer_agent import NormalizerAgent
from hephis_core.agents.organizer_agent import OrganizerAgent
from hephis_core.agents.recipe_writer_agent import RecipeWriterAgent
from hephis_core.agents.universal_packer_agent import UniversalPackerAgent
from hephis_core.agents.universal_retriever_agent import UniversalRetrieverAgent
from hephis_core.agents.finalizer_agent import FinalizerAgent
from hephis_core.agents.reporter_agent import ReporterAgent
from hephis_core.agents.reporter_rules import REPORTER_RULES

print("BOOSTRAP CALLED")

def bootstrap_agents():

    identifier_core = IdentifierCore(detectors=RAW_DOMAIN_DETECTOR)

    agents = [
        ConfidenceAgent(),
        SnifferAgent(),
        UrlFetcherAgent(),
        GarbageAnaliserAgent(),
        GarbageCleanerAgent(),
        GatekeeperAgent(),
        IdentifierAgent(identifier_core=identifier_core),
        UniversalExtractorAgent(),
        RawMaterialAdvisorAgent(),
        HtmlCleanerAgent(),
        DecisionAgent(),
        OrganizerAgent(),
        RecipeWriterAgent(),
        NormalizerAgent(),
        UniversalPackerAgent(),
        FinalizerAgent(),
        ReporterAgent(rules=REPORTER_RULES),
        UniversalRetrieverAgent(),
        ]
    
    return agents
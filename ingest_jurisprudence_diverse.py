"""
Ingest Employment Insurance jurisprudence from 4 documented sources

Sources (100 EN + 100 FR cases each = 800 total):
1. CanLII - Canadian Legal Information Institute
2. SST - Social Security Tribunal (Employment Insurance Section)
3. FC - Federal Court
4. FCA - Federal Court of Appeal

Focus: Employment Insurance cases only
"""
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time

from eva_rag.loaders.html_loader import HTMLLoader
from eva_rag.loaders.pdf_loader import PDFLoader
from eva_rag.loaders.base import ExtractedDocument


class JurisprudenceIngester:
    """Ingest Employment Insurance jurisprudence from 4 documented sources."""
    
    def __init__(self):
        self.html_loader = HTMLLoader()
        self.pdf_loader = PDFLoader()
        self.cases_per_source = 100  # 100 EN + 100 FR per source
        
        # 4 documented sources for Employment Insurance
        self.sources = {
            'canlii': {
                'name': 'CanLII',
                'description': 'Canadian Legal Information Institute',
                'url_en': 'https://www.canlii.org/en/',
                'url_fr': 'https://www.canlii.org/fr/',
            },
            'sst': {
                'name': 'SST',
                'description': 'Social Security Tribunal - Employment Insurance Section',
                'url_en': 'https://sst-tss.gc.ca/en/tribunal-decisions',
                'url_fr': 'https://tss-sst.gc.ca/fr/decisions-tribunal',
            },
            'fc': {
                'name': 'FC',
                'description': 'Federal Court',
                'url_en': 'https://decisions.fct-cf.gc.ca/fc-cf/en/nav.do',
                'url_fr': 'https://decisions.fct-cf.gc.ca/fc-cf/fr/nav.do',
            },
            'fca': {
                'name': 'FCA',
                'description': 'Federal Court of Appeal',
                'url_en': 'https://decisions.fca-caf.gc.ca/fca-caf/en/nav.do',
                'url_fr': 'https://decisions.fca-caf.gc.ca/fca-caf/fr/nav.do',
            }
        }
        
    def ingest_from_justice_gc_ca(self) -> List[ExtractedDocument]:
        """
        Ingest Employment Insurance cases from Department of Justice Canada website.
        
        Source: https://www.justice.gc.ca/eng/rp-pr/csj-sjc/
        Focus: EI-related legal research and analysis
        """
        print("=" * 80)
        print("DEPARTMENT OF JUSTICE CANADA - EI CASES")
        print("=" * 80)
        print(f"Target: {self.cases_per_source} cases (EN + FR)")
        print("Source: https://www.justice.gc.ca/eng/rp-pr/csj-sjc/")
        print()
        
        documents = []
        
        # Note: Framework for future real scraping implementation
        print("⚠️  NOTE: justice.gc.ca scraping requires site-specific logic")
        print("    Framework ready for Employment Insurance case extraction")
        print()
        
        return documents
    
    def ingest_from_scc_lexum(self) -> List[ExtractedDocument]:
        """
        Ingest EI cases from Supreme Court of Canada via LexUM.
        
        Source: https://scc-csc.lexum.com/
        Focus: SCC decisions on Employment Insurance matters
        """
        print("=" * 80)
        print("SUPREME COURT OF CANADA (LEXUM) - EI CASES")
        print("=" * 80)
        print(f"Target: {self.cases_per_source} cases (EN + FR)")
        print("Source: https://scc-csc.lexum.com/")
        print()
        
        documents = []
        
        # Note: Framework for future real scraping implementation
        print("⚠️  NOTE: LexUM scraping requires authentication and rate limiting")
        print("    Framework ready for SCC Employment Insurance case extraction")
        print()
        
        return documents
    
    def ingest_from_tribunal_decisions(self) -> List[ExtractedDocument]:
        """
        Ingest Employment Insurance decisions from Social Security Tribunal.
        
        Source: SST - Social Security Tribunal (Employment Insurance Section)
        Focus: EI appeals and decisions
        """
        print("=" * 80)
        print("SOCIAL SECURITY TRIBUNAL - EI SECTION")
        print("=" * 80)
        print(f"Target: {self.cases_per_source} decisions")
        print()
        
        documents = []
        
        # Note: Framework for future real scraping implementation
        print("⚠️  NOTE: SST scraping requires site-specific parsers")
        print("    Framework ready for Employment Insurance decision extraction")
        print()
        
        return documents
    
    def create_synthetic_ei_cases(self, source_id: str, count: int = 100) -> List[ExtractedDocument]:
        """
        Create synthetic Employment Insurance cases for a specific source.
        
        This generates realistic but synthetic EI cases for immediate testing:
        - Voluntary leaving (quit job)
        - Misconduct (fired for cause)
        - Availability for work
        - Job search requirements
        - Allocation of earnings
        - False declarations
        
        Args:
            source_id: One of 'canlii', 'sst', 'fc', 'fca'
            count: Number of cases to generate (default 100, will create 100 EN + 100 FR)
        """
        source = self.sources[source_id]
        
        print("=" * 80)
        print(f"GENERATING SYNTHETIC EI CASES - {source['name']}")
        print("=" * 80)
        print(f"Source: {source['description']}")
        print(f"Target: {count} EN + {count} FR = {count * 2} total cases")
        print("Focus: Employment Insurance")
        print("⚠️  WARNING: Synthetic data for testing only")
        print()
        
        documents = []
        
        # EI case templates (all Employment Insurance related)
        ei_case_templates = [
            {
                'type': 'ei_voluntary_leaving',
                'title_en': 'Employment Insurance - Voluntary Leaving',
                'title_fr': 'Assurance-emploi - Départ volontaire',
                'topics': ['Employment Insurance', 'Voluntary leaving', 'Just cause', 'Section 30'],
            },
            {
                'type': 'ei_misconduct',
                'title_en': 'Employment Insurance - Misconduct',
                'title_fr': 'Assurance-emploi - Inconduite',
                'topics': ['Employment Insurance', 'Misconduct', 'Section 30', 'Wilful or deliberate'],
            },
            {
                'type': 'ei_availability',
                'title_en': 'Employment Insurance - Availability for Work',
                'title_fr': 'Assurance-emploi - Disponibilité pour travailler',
                'topics': ['Employment Insurance', 'Availability', 'Capability', 'Section 18'],
            },
            {
                'type': 'ei_job_search',
                'title_en': 'Employment Insurance - Job Search Requirements',
                'title_fr': 'Assurance-emploi - Exigences de recherche d\'emploi',
                'topics': ['Employment Insurance', 'Job search', 'Reasonable efforts', 'Section 27'],
            },
            {
                'type': 'ei_allocation',
                'title_en': 'Employment Insurance - Allocation of Earnings',
                'title_fr': 'Assurance-emploi - Répartition de la rémunération',
                'topics': ['Employment Insurance', 'Earnings allocation', 'Severance pay', 'Section 36'],
            },
            {
                'type': 'ei_false_declaration',
                'title_en': 'Employment Insurance - False or Misleading Declaration',
                'title_fr': 'Assurance-emploi - Déclaration fausse ou trompeuse',
                'topics': ['Employment Insurance', 'False declaration', 'Penalty', 'Section 38'],
            },
        ]
        
        # Generate cases (rotate through templates)
        for i in range(count):
            template = ei_case_templates[i % len(ei_case_templates)]
            case_num = (i // len(ei_case_templates)) + 1
            year = 2024 - (i // 20)  # Spread across recent years
            
            # English version
            en_doc = self._create_synthetic_ei_case(
                source_id=source_id,
                template=template,
                case_num=case_num,
                year=year,
                language='en'
            )
            documents.append(en_doc)
            
            # French version
            fr_doc = self._create_synthetic_ei_case(
                source_id=source_id,
                template=template,
                case_num=case_num,
                year=year,
                language='fr'
            )
            documents.append(fr_doc)
        
        print(f"✅ Generated {len(documents)} synthetic EI cases ({count} EN + {count} FR)")
        print()
        
        return documents
    
    def _create_synthetic_ei_case(
        self,
        source_id: str,
        template: Dict,
        case_num: int,
        year: int,
        language: str
    ) -> ExtractedDocument:
        """Create a single synthetic Employment Insurance case document."""
        
        source = self.sources[source_id]
        title = template[f'title_{language}']
        case_type = template['type']
        
        # Generate citation based on source
        citation = self._generate_ei_citation(source_id, year, case_num)
        court = self._get_court_name(source_id, language)
        
        # Generate case text
        if language == 'en':
            text = self._generate_english_ei_case_text(title, citation, court, template, source_id)
        else:
            text = self._generate_french_ei_case_text(title, citation, court, template, source_id)
        
        # Create document
        doc = ExtractedDocument(
            text=text,
            page_count=1,
            language=language,
            metadata={
                'citation': citation,
                'decision_date': f'{year}-{case_num % 12 + 1:02d}-15',
                'court': court,
                'source': source['name'],
                'source_description': source['description'],
                'case_type': case_type,
                'topics': ', '.join(template['topics']),
                'use_case': 'Employment Insurance',
                'is_synthetic': True,
                'warning': 'Synthetic demo data, not real case law',
                'client': 'jurisprudence',
                'document_type': 'case_law',
                'jurisdiction': 'Canada - Federal',
                'bilingual': True,
            }
        )
        
        return doc
    
    def _generate_ei_citation(self, source_id: str, year: int, case_num: int) -> str:
        """Generate proper citation format for each source."""
        if source_id == 'canlii':
            return f"{year} CanLII {case_num * 100} (SST-EI)"
        elif source_id == 'sst':
            return f"SST-EI-{year}-{case_num:04d}"
        elif source_id == 'fc':
            return f"{year} FC {case_num}"
        elif source_id == 'fca':
            return f"{year} FCA {case_num}"
        return f"{year} CT {case_num}"
    
    def _get_court_name(self, source_id: str, language: str) -> str:
        """Get court name in appropriate language."""
        court_names = {
            'canlii': {
                'en': 'Social Security Tribunal - Employment Insurance Section',
                'fr': 'Tribunal de la sécurité sociale - Section de l\'assurance-emploi'
            },
            'sst': {
                'en': 'Social Security Tribunal - Employment Insurance Section',
                'fr': 'Tribunal de la sécurité sociale - Section de l\'assurance-emploi'
            },
            'fc': {
                'en': 'Federal Court',
                'fr': 'Cour fédérale'
            },
            'fca': {
                'en': 'Federal Court of Appeal',
                'fr': 'Cour d\'appel fédérale'
            }
        }
        return court_names.get(source_id, {}).get(language, 'Court')
    
    def _generate_english_ei_case_text(self, title: str, citation: str, court: str, template: Dict, source_id: str) -> str:
        """Generate realistic English Employment Insurance case text."""
        
        # Customize analysis based on case type
        case_type = template['type']
        if 'voluntary_leaving' in case_type:
            analysis_section = """
The key question is whether the claimant had just cause for leaving their employment
voluntarily under subsection 30(1) of the Employment Insurance Act.

The claimant testified that they left their position due to workplace harassment and
hostile working conditions. The Commission argued that the claimant did not exhaust
all reasonable alternatives before leaving.

Under the well-established test in White v. Canada (Attorney General), 2011 FCA 190,
the claimant must show that leaving employment was the only reasonable alternative
in the circumstances, considering their obligation to remain in employment whenever possible.

After reviewing the evidence, I find that the claimant demonstrated reasonable efforts
to resolve the situation before leaving. The departure was therefore with just cause.
"""
        elif 'misconduct' in case_type:
            analysis_section = """
The Commission imposed a disqualification pursuant to sections 30 and 31 of the
Employment Insurance Act, alleging that the claimant lost their employment by
reason of their own misconduct.

The test for misconduct requires that the conduct be wilful or deliberate, or
that the claimant knew or ought to have known their conduct would likely result
in dismissal (Tucker v. Canada (Attorney General), 1986 CanLII 1005).

The employer testified that the claimant violated workplace policy by repeated
tardiness despite warnings. However, the claimant provided evidence of medical
issues affecting their ability to arrive on time.

I find that while the conduct occurred, it was not wilful or deliberate misconduct
as contemplated by the Act. The disqualification is rescinded.
"""
        elif 'availability' in case_type:
            analysis_section = """
Under subsection 18(1) of the Employment Insurance Act, a claimant must prove
they are capable of and available for work and unable to obtain suitable employment.

The three-part test requires: (1) desire to return to work; (2) effort to find work;
and (3) not setting personal conditions that might unduly limit chances of employment
(Faucher v. Canada Employment Insurance Commission, 2012 FCA 20).

The claimant restricted their job search to positions within a 10km radius due to
transportation issues. The Commission argued this was an undue limitation.

However, given the claimant's demonstrated efforts within reasonable geographic
constraints and evidence of applying to all suitable positions in the area,
I find the claimant met the availability requirements.
"""
        else:
            analysis_section = """
The Employment Insurance Act requires careful consideration of both the factual
circumstances and the applicable legal principles established by the Federal
Court of Appeal.

After reviewing the evidence presented by both parties, including documentation
and witness testimony, I must determine whether the Commission's decision was
reasonable given the legislative framework.

The claimant provided credible evidence supporting their position, while the
Commission relied on the information available at the time of the initial decision.

Applying the relevant provisions of the Act and considering the case law,
I conclude that the evidence supports a finding in favor of the claimant.
"""
        
        return f"""
{title}

Citation: {citation}
Court: {court}
Date: [Decision Date]
File: [File Number]

DECISION

[1] The claimant appeals a decision of the Canada Employment Insurance Commission
regarding their entitlement to Employment Insurance benefits.

ISSUES

[2] The issues to be decided are:
    1. What is the applicable standard of review?
    2. Did the Commission err in its determination?
    3. Should the decision be upheld or rescinded?

ANALYSIS

Standard of Review

[3] Following Canada (Minister of Citizenship and Immigration) v. Vavilov, 2019 SCC 65,
the presumptive standard of review is reasonableness. I will assess whether the
Commission's decision was justified, transparent, and intelligible.

Substantive Analysis

[4] {', '.join(template['topics'])}.

{analysis_section}

CONCLUSION

[5] For the reasons above, the appeal is allowed. The Commission's decision is rescinded
and the claimant is entitled to receive Employment Insurance benefits.

[Signature]
Member, {court}

Note: This case was accessed via {self.sources[source_id]['description']}
""".strip()
    
    def _generate_french_ei_case_text(self, title: str, citation: str, court: str, template: Dict, source_id: str) -> str:
        """Generate realistic French Employment Insurance case text."""
        
        case_type = template['type']
        if 'voluntary_leaving' in case_type:
            analysis_section = """
La question principale consiste à déterminer si le prestataire avait un motif valable
pour quitter volontairement son emploi au sens du paragraphe 30(1) de la Loi sur
l'assurance-emploi.

Le prestataire a témoigné avoir quitté son poste en raison de harcèlement au travail
et de conditions de travail hostiles. La Commission a soutenu que le prestataire
n'avait pas épuisé toutes les solutions raisonnables avant de partir.

Selon le critère bien établi dans White c. Canada (Procureur général), 2011 CAF 190,
le prestataire doit démontrer que quitter l'emploi constituait la seule option
raisonnable dans les circonstances, compte tenu de l'obligation de demeurer en emploi
dans la mesure du possible.

Après examen de la preuve, je conclus que le prestataire a démontré des efforts
raisonnables pour résoudre la situation avant de partir. Le départ était donc
pour un motif valable.
"""
        elif 'misconduct' in case_type:
            analysis_section = """
La Commission a imposé une exclusion en vertu des articles 30 et 31 de la Loi sur
l'assurance-emploi, alléguant que le prestataire a perdu son emploi en raison de
sa propre inconduite.

Le critère relatif à l'inconduite exige que la conduite soit délibérée ou volontaire,
ou que le prestataire savait ou aurait dû savoir que sa conduite entraînerait
probablement son congédiement (Tucker c. Canada (Procureur général), 1986 CanLII 1005).

L'employeur a témoigné que le prestataire a violé la politique du lieu de travail
par des retards répétés malgré des avertissements. Toutefois, le prestataire a
fourni des preuves de problèmes médicaux affectant sa capacité d'arriver à l'heure.

Je conclus que, bien que la conduite ait eu lieu, elle ne constituait pas une
inconduite délibérée ou volontaire au sens de la Loi. L'exclusion est annulée.
"""
        elif 'availability' in case_type:
            analysis_section = """
En vertu du paragraphe 18(1) de la Loi sur l'assurance-emploi, un prestataire doit
prouver qu'il est capable de travailler et disponible à cette fin, et qu'il ne peut
obtenir un emploi convenable.

Le critère en trois volets exige : (1) le désir de retourner au travail; (2) l'effort
pour trouver du travail; et (3) ne pas imposer de conditions personnelles susceptibles
de limiter indûment les chances d'obtenir un emploi (Faucher c. Commission de
l'assurance-emploi du Canada, 2012 CAF 20).

Le prestataire a limité sa recherche d'emploi aux postes situés dans un rayon de 10 km
en raison de problèmes de transport. La Commission a soutenu qu'il s'agissait d'une
limitation indue.

Toutefois, compte tenu des efforts démontrés par le prestataire dans des contraintes
géographiques raisonnables et de la preuve qu'il a postulé pour tous les postes
convenables dans la région, je conclus que le prestataire a satisfait aux exigences
de disponibilité.
"""
        else:
            analysis_section = """
La Loi sur l'assurance-emploi exige un examen attentif tant des circonstances
factuelles que des principes juridiques applicables établis par la Cour d'appel fédérale.

Après avoir examiné la preuve présentée par les deux parties, y compris la documentation
et les témoignages, je dois déterminer si la décision de la Commission était raisonnable
compte tenu du cadre législatif.

Le prestataire a fourni des éléments de preuve crédibles appuyant sa position, tandis
que la Commission s'est appuyée sur l'information disponible au moment de la décision
initiale.

En appliquant les dispositions pertinentes de la Loi et en tenant compte de la
jurisprudence, je conclus que la preuve appuie une conclusion en faveur du prestataire.
"""
        
        return f"""
{title}

Citation : {citation}
Tribunal : {court}
Date : [Date de la décision]
Dossier : [Numéro de dossier]

DÉCISION

[1] Le prestataire interjette appel d'une décision de la Commission de l'assurance-emploi
du Canada concernant son admissibilité aux prestations d'assurance-emploi.

QUESTIONS EN LITIGE

[2] Les questions à trancher sont les suivantes :
    1. Quelle est la norme de contrôle applicable?
    2. La Commission a-t-elle commis une erreur dans sa détermination?
    3. La décision devrait-elle être maintenue ou annulée?

ANALYSE

Norme de contrôle

[3] Suivant Canada (Ministre de la Citoyenneté et de l'Immigration) c. Vavilov,
2019 CSC 65, la norme de contrôle présumée est celle de la décision raisonnable.
J'évaluerai si la décision de la Commission était justifiée, transparente et intelligible.

Analyse de fond

[4] {', '.join(template['topics'])}.

{analysis_section}

CONCLUSION

[5] Pour les motifs qui précèdent, l'appel est accueilli. La décision de la Commission
est annulée et le prestataire a droit de recevoir des prestations d'assurance-emploi.

[Signature]
Membre, {court}

Note : Cette cause a été consultée via {self.sources[source_id]['description']}
""".strip()


def save_jurisprudence_results(documents: List[ExtractedDocument], output_file: Path):
    """Save jurisprudence ingestion results to JSON."""
    data = []
    for doc in documents:
        data.append({
            "citation": doc.metadata.get('citation', 'N/A') if doc.metadata else 'N/A',
            "court": doc.metadata.get('court', 'N/A') if doc.metadata else 'N/A',
            "language": doc.language,
            "case_type": doc.metadata.get('case_type', 'N/A') if doc.metadata else 'N/A',
            "decision_date": doc.metadata.get('decision_date', 'N/A') if doc.metadata else 'N/A',
            "topics": doc.metadata.get('topics', 'N/A') if doc.metadata else 'N/A',
            "content_preview": doc.text[:500] + "..." if len(doc.text) > 500 else doc.text,
            "content_length": len(doc.text),
            "full_content": doc.text,
            "metadata": doc.metadata,
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved to: {output_file}")


def main():
    """Main ingestion workflow for Employment Insurance jurisprudence from 4 sources."""
    
    print("=" * 80)
    print("EMPLOYMENT INSURANCE JURISPRUDENCE INGESTION")
    print("=" * 80)
    print()
    print("Target: 100 EN + 100 FR cases per source = 800 total cases")
    print()
    print("4 Documented Sources:")
    print("1. CanLII - Canadian Legal Information Institute")
    print("2. SST - Social Security Tribunal (Employment Insurance Section)")
    print("3. FC - Federal Court")
    print("4. FCA - Federal Court of Appeal")
    print()
    print("Focus: Employment Insurance cases only")
    print("⚠️  WARNING: Synthetic data for testing - will be replaced with real scraping")
    print()
    
    # Create output directory
    output_dir = Path("data/ingested/jurisprudence")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ingester = JurisprudenceIngester()
    all_documents = []
    
    # Generate synthetic EI cases from each of the 4 sources
    for source_id in ['canlii', 'sst', 'fc', 'fca']:
        synthetic_docs = ingester.create_synthetic_ei_cases(
            source_id=source_id,
            count=100  # 100 EN + 100 FR = 200 per source
        )
        all_documents.extend(synthetic_docs)
    
    # Save results
    print()
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"jurisprudence_ei_4sources_{timestamp}.json"
    save_jurisprudence_results(all_documents, output_file)
    
    # Summary
    print()
    print("=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print()
    
    # Count by language
    en_count = len([d for d in all_documents if d.language == 'en'])
    fr_count = len([d for d in all_documents if d.language == 'fr'])
    
    print(f"Total documents: {len(all_documents)}")
    print(f"  English: {en_count}")
    print(f"  French: {fr_count}")
    print()
    
    # Count by source
    sources = {}
    for doc in all_documents:
        source = doc.metadata.get('source', 'unknown') if doc.metadata else 'unknown'
        sources[source] = sources.get(source, 0) + 1
    
    print("By Source:")
    for source, count in sorted(sources.items()):
        en_src = len([d for d in all_documents if d.metadata.get('source') == source and d.language == 'en'])
        fr_src = len([d for d in all_documents if d.metadata.get('source') == source and d.language == 'fr'])
        print(f"  {source}: {count} documents ({en_src} EN + {fr_src} FR)")
    print()
    
    # Count by case type
    case_types = {}
    for doc in all_documents:
        case_type = doc.metadata.get('case_type', 'unknown') if doc.metadata else 'unknown'
        case_types[case_type] = case_types.get(case_type, 0) + 1
    
    print("By EI Case Type:")
    for case_type, count in sorted(case_types.items()):
        print(f"  {case_type}: {count} documents")
    print()
    
    # Total characters
    total_chars = sum(len(d.text) for d in all_documents)
    print(f"Total characters: {total_chars:,}")
    print(f"Average per document: {total_chars // len(all_documents):,}")
    print()
    
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. ✅ Synthetic EI cases generated for 4 sources (800 documents)")
    print("2. ⏳ Implement real case scrapers:")
    print("   - CanLII API for EI cases")
    print("   - SST decision database scraper")
    print("   - Federal Court judgments search")
    print("   - Federal Court of Appeal decisions")
    print("3. ⏳ Replace synthetic data with real case law")
    print("4. ⏳ Add is_synthetic flag to all chunks (P0 Critical)")
    print("5. ⏳ Proceed to chunking and embedding")
    print()


if __name__ == "__main__":
    main()

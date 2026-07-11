from codecraft.models.concept import ConceptTaxonomy
from codecraft.domains.registry import DomainRegistry
from codecraft.engines.templates import EXERCISE_TEMPLATES
from codecraft.scanner.concept_extractor import ConceptExtractor
import inspect, re

all_c = set(c.name for c in ConceptTaxonomy.all())
templated = set(EXERCISE_TEMPLATES.keys())

# G2: uncovered by domains
all_domain_c = set()
for d in DomainRegistry.all():
    for c in d.supported_concepts():
        all_domain_c.add(c)
uncovered = all_c - all_domain_c
print(f"G2: {len(uncovered)} concepts uncovered by domains")
for c in sorted(uncovered):
    print(f"  - {c}")

# G3: orphan
orphan = all_domain_c - all_c
print(f"\nG3: orphan concepts (in domains but not taxonomy): {sorted(orphan)}")

# G4: missing detectors
src = inspect.getsource(ConceptExtractor)
detected = set()
for m in re.findall(r"_add\(['\"](\w+)['\"]", src):
    detected.add(m)

tot_undetected = len(all_c - detected)
print(f"\nG4: {tot_undetected}/{len(all_c)} concepts need detectors")
for c in sorted(all_c - detected):
    print(f"  - {c}")

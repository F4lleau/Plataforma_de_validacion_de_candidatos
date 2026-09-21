from copy import deepcopy
import hashlib
import json
from pathlib import Path

# Immutable deployed content; each acceptance also keeps its own exact snapshot.
_DOCUMENTS = json.loads(
    (Path(__file__).resolve().parents[1] / "legal" / "documents.json").read_text()
)


class LegalDocumentRepository:
    def documents(self):
        documents = deepcopy(_DOCUMENTS)
        for document in documents.values():
            encoded = json.dumps(document, ensure_ascii=False, sort_keys=True).encode()
            document["sha256"] = hashlib.sha256(encoded).hexdigest()
        return documents

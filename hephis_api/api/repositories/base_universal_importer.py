

class BaseImporter:
    """
    BaseImporter defines the *pipeline steps* for importing any type of data.

    Child classes MUST override:
        - fetch()
        - organize()
        - normalize()
        - map_to_model()

    Child classes SHOULD NOT override:
        - run()
        - pack()

    This preserves the workflow order while letting each importer
    specialize how the steps are performed.
    """

    # 🔹 STEP 1 — Get raw input (HTML, JSON, text, etc.)
    def fetch(self, source):
        raise NotImplementedError("Child importer must implement fetch()")

    # 🔹 STEP 2 — Convert raw input into a structured intermediate format
    def organize(self, raw_data):
        raise NotImplementedError("Child importer must implement organize()")

    # 🔹 STEP 3 — Normalize the structured data according to your Core logic
    def normalize(self, organized_data):
        raise NotImplementedError("Child importer must implement normalize()")

    # 🔹 STEP 4 — Convert normalized data into a Pydantic schema model
    def map_to_model(self, normalized_data):
        raise NotImplementedError("Child importer must implement map_to_model()")

    # 🔹 STEP 5 — Use Universal Packer from HephisCore
    def pack(self, model, domain: str):
        """
        Packs the validated model using the universal packer.
        Domain = name of subfolder (e.g., 'music', 'recipes').
        """
        from hephis_core.services.packers.universal_packer import pack_data
        return pack_data(domain, model)

    # 🔥 MASTER PIPELINE — CHILD CLASSES DO NOT OVERRIDE THIS
    def run(self, source: str, domain: str):
        """
        Executes the full import pipeline and returns structured results.
        """

        # 1 — Fetch raw content
        raw = self.fetch(source)

        # 2 — Organize the raw content
        organized = self.organize(raw)

        # 3 — Normalize that organized content
        normalized = self.normalize(organized)

        # 4 — Convert normalized dict into a Pydantic model
        model = self.map_to_model(normalized)

        # 5 — Pack the model and save JSON to disk
        packed = self.pack(model, domain)

        # Final API return
        return {
            "success": True,
            "raw": raw,
            "organized": organized,
            "normalized": normalized,
            "model": model.model_dump(),
            "packed": packed,
        }
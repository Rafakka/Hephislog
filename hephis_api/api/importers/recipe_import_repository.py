
class RecipeImporter(BaseImporter):

    def fetch(self, url):
        from hephis_core.infra.sources.t_g_scraper import fetch_and_extract

        raw = fetch_and_extract(url)

        if raw is None:
            return {
                "title": "Unknown",
                "ingredients": [],
                "steps": [],
                "info": {},
                "url": url
            }

        raw["url"] = url
        return raw


    def organize(self, raw):
        return raw


    def normalize(self, organized):
        from hephis_core.modules.recipe_normalizer.normalizer import recipe_normalizer
        return recipe_normalizer(organized)

    def map_to_model(self, normalized):
        from hephis_core.schemas.panaceia_schemas import RecipeSchema
        return RecipeSchema(**normalized["data"])

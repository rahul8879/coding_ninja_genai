
import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "versions"

class PromptRegistry:
    def __init__(self):
        self._cache: dict= {}
        self._load_all()

    def _load_all(self):
        """
        On startup — load all YAML files from versions/ into cache.
        If a file is malformed, log error and skip. Don't crash the app.
        """
        yaml_files = list(PROMPTS_DIR.glob("*.yaml"))


        for filepath in yaml_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    version = data.get("version")
                    self._cache[version] = data
            except Exception as e:
                print('something goes wrong here')

    def get(self, version: str) -> dict:
        """
        Fetch prompt data by version name.
        Raises KeyError if version doesn't exist — caller handles it.
        """
        if version not in self._cache:
            available = list(self._cache.keys())
            raise KeyError(
                f"Prompt version '{version}' not found. Available: {available}"
            )
        return self._cache[version]

    def get_template(self, version: str) -> str:
        """
        Directly return the template string for a given version.
        This is what LangChain PromptTemplate will consume.
        """
        return self.get(version)["template"]

    def list_versions(self) -> list[str]:
        """
        Returns all loaded version names.
        Useful for a /versions endpoint later.
        """
        return list(self._cache.keys())


prompt_registry = PromptRegistry()

    
from docxtpl import DocxTemplate
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from src.logger_config import get_logger

logger = get_logger(__name__)


class WordPresenter:
    """
    Génère des rapports Word à partir de templates docxtpl.

    Cette classe orchestre la génération de documents Word en:
    1. Chargeant un template Word existant
    2. Préparant le contexte avec métadonnées et données de tableaux
    3. Rendant le template avec docxtpl
    4. Sauvegardant le document généré
    """

    def __init__(self, template_path: str, output_path: str):
        """
        Initialise le présentateur Word.

        Args:
            template_path: Chemin vers le template Word (.docx)
            output_path: Chemin où sauvegarder le rapport généré

        Raises:
            FileNotFoundError: Si le template n'existe pas
        """
        self.template_path = Path(template_path)
        self.output_path = Path(output_path)

        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {self.template_path}. "
                f"Please create a Word template with docxtpl tags."
            )

        logger.info(f"WordPresenter initialized with template: {self.template_path}")

    def render_report(
        self, context: Dict[str, Any], metadata: Dict[str, Any] = None
    ) -> None:
        """
        Génère un rapport Word à partir du template.

        Args:
            context: Dictionnaire avec toutes les données pour le template
                    (tables principalement)
            metadata: Métadonnées additionnelles (date, période de test, turbines)

        Raises:
            Exception: Si la génération du document échoue
        """
        logger.info(f"Rendering Word report from template: {self.template_path}")

        try:
            # Créer le contexte complet avec métadonnées
            full_context = self._prepare_context(context, metadata)

            # Charger et rendre le template
            doc = DocxTemplate(self.template_path)
            doc.render(full_context)

            # Créer le dossier output si nécessaire
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Sauvegarder le document
            doc.save(self.output_path)

            logger.info(f"✅ Report successfully saved to: {self.output_path}")

        except Exception as e:
            logger.error(f"❌ Failed to generate Word report: {e}")
            raise

    def _prepare_context(
        self, context: Dict[str, Any], metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Prépare le contexte complet pour le template avec métadonnées.

        Args:
            context: Données de tables
            metadata: Métadonnées (test_start, test_end, turbines)

        Returns:
            Contexte complet pour docxtpl
        """
        breakpoint()  # Debug: Vérifier le contexte initial et les métadonnées
        full_context = context.copy()

        # Ajouter la date de génération
        full_context["generation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Ajouter les métadonnées si fournies
        if metadata:
            # Période de test
            if "test_start" in metadata:
                test_start = metadata["test_start"]
                # Formater si c'est un datetime
                if hasattr(test_start, "strftime"):
                    test_start = test_start.strftime("%Y-%m-%d %H:%M:%S")
                full_context["test_start"] = test_start

            if "test_end" in metadata:
                test_end = metadata["test_end"]
                # Formater si c'est un datetime
                if hasattr(test_end, "strftime"):
                    test_end = test_end.strftime("%Y-%m-%d %H:%M:%S")
                full_context["test_end"] = test_end

            # Liste des turbines analysées
            if "turbines" in metadata:
                turbines = metadata["turbines"]
                if isinstance(turbines, list):
                    turbine_list = ", ".join(turbines)
                    full_context["turbine_list"] = turbine_list
                    full_context["turbine_count"] = len(turbines)

            # Autres métadonnées
            full_context.update(metadata)

        logger.info(
            f"Context prepared with {len(full_context)} keys "
            f"(generation_date: {full_context['generation_date']})"
        )

        return full_context

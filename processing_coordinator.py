from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
"""Module processing_coordinator.py - Classe ProcessingCoordinator."""

import logging
from pathlib import Path

from read_patch_step import ReadPatchStep
from detect_target_step import DetectTargetStep
from analyze_patch_step import AnalyzePatchStep
from correct_patch_step import CorrectPatchStep
from processing_pipeline import ProcessingPipeline
from apply_patch_step import ApplyPatchStep

class ProcessingCoordinator:
    """Responsable de coordonner le flux de traitement des patches"""
    
    def __init__(self, config, components: Dict):
        self.config = config
        self.logger = logging.getLogger('smart_patch_processor.coordinator')
        self.detector = components['detector']
        self.analyzer = components['analyzer']
        self.corrector = components['corrector']
        self.applicator = components['applicator']
        self.rollback_manager = components.get('rollback_manager')
        self.previewer = components.get('previewer')
    
    def coordinate_single_patch(self, patch_path: Path, target_file: Optional[Path] = None):
        """Coordonne le traitement d'un patch unique"""
        pipeline = ProcessingPipeline()
        pipeline.add_step(ReadPatchStep(patch_path))
        pipeline.add_step(DetectTargetStep(self.detector, target_file))
        pipeline.add_step(AnalyzePatchStep(self.analyzer))
        pipeline.add_step(CorrectPatchStep(self.corrector))
        pipeline.add_step(ApplyPatchStep(self.applicator))
        return pipeline.execute()

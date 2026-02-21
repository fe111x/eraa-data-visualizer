"""Laden und Validieren der config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    data_dir: str = "data"
    output_dir: str = "output"
    output_subdirs: dict[str, str] = Field(
        default_factory=lambda: {
            "adequacy": "adequacy",
            "dispatch": "dispatch",
            "net_position": "net_position",
            "prices": "prices",
            "storage": "storage",
        }
    )


class DimensionsConfig(BaseModel):
    n_climate_years: int = 36
    n_samples_per_climate_year: int = 10
    target_years: list[int] = Field(default_factory=lambda: [2025, 2028, 2030, 2033])


class TechnologyConfig(BaseModel):
    generation: list[str] = Field(default_factory=list)
    storage: list[str] = Field(default_factory=list)


class HtmlConfig(BaseModel):
    full_html: bool = True
    include_plotlyjs: bool | str = True


class VisualizationConfig(BaseModel):
    template: str = "plotly_white"
    color_map_technology: str = "Set3"
    figure_width: int = 1200
    figure_height: int = 600
    html: HtmlConfig = Field(default_factory=HtmlConfig)
    boxplot_percentiles: list[int] = Field(default_factory=lambda: [5, 25, 50, 75, 95])
    heatmap_max_timesteps: int = 8760


class SchemaConfig(BaseModel):
    adequacy: dict[str, str] = Field(default_factory=dict)
    dispatch: dict[str, str] = Field(default_factory=dict)
    net_position: dict[str, str] = Field(default_factory=dict)
    prices: dict[str, str] = Field(default_factory=dict)
    storage: dict[str, str] = Field(default_factory=dict)


class Config(BaseModel):
    paths: PathsConfig = Field(default_factory=PathsConfig)
    dimensions: DimensionsConfig = Field(default_factory=DimensionsConfig)
    technology: TechnologyConfig = Field(default_factory=TechnologyConfig)
    study_zones: list[str] = Field(default_factory=list)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    schema: SchemaConfig = Field(default_factory=SchemaConfig)

    @classmethod
    def load(cls, path: str | Path = "config.yaml") -> "Config":
        p = Path(path)
        if not p.exists():
            return cls()
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls.model_validate(data)

    def output_path(self, category: str, filename: str) -> Path:
        base = Path(self.paths.output_dir)
        sub = self.paths.output_subdirs.get(category, category)
        out = base / sub
        out.mkdir(parents=True, exist_ok=True)
        return out / filename

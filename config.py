from typing import Dict, List

from pydantic import BaseModel, BaseSettings, PyObject


class TrainConfig(BaseModel):
    source_url: str
    label_column: str
    allow_validation_failure: bool
    ohe_columns: list
    test_size: float


class DeployConfig(BaseModel):
    challenger_model_tag: str
    champion_model_tag: str
    label_column: str
    deploy_model_name: str


class AppConfig(BaseSettings):
    # Project
    project_name: str = "cicd-flow"
    archive_source: str = "v3io:///bigdata/cicd-flow.zip"
    git_repo: str = "git://github.com/igz-us-sales/igz-cicd-flow"
    git_branch: str = "master"
    secrets_file: str = "secrets.env"
    artifact_path: str = "s3://igz-artifacts/projects/{{run.project}}/artifacts"

    # CI/CD environments
    environments: List[str] = ["development", "staging", "master"]

    # Artifacts
    challenger_model_tag: str = "challenger"
    champion_model_tag: str = "champion"
    yaml_export_dir: str = "artifacts"

    # Workflow parameters
    source_url: str = "./data/heart.csv"
    label_column: str = "target"
    allow_validation_failure: bool = True
    ohe_columns: List[str] = ["sex", "cp", "slope", "thal", "restecg"]
    test_size: float = 0.1
    deploy_model_name: str = "model"
    deploy_condition_metric: str = "evaluation_accuracy"
    force_deploy: bool = False

    # Workflow config schemas
    workflows: Dict[str, PyObject] = {"train": TrainConfig, "deploy": DeployConfig}

    @property
    def git_source(self):
        return f"{self.git_repo}#{self.git_branch}"

    def get_workflow_config(self, workflow_name: str) -> dict:
        return self.workflows[workflow_name](**self.dict()).dict()

# Semantic Scholar datasets
import httpx
from app.internal.base_model import PtBaseModel

BASE_S2_URL = "https://api.semanticscholar.org/datasets/v1/release/"


def get_latest_release() -> str:
    with httpx.Client() as client:
        response = client.get(BASE_S2_URL)
    releases = response.json()
    latest_release = releases[-1]
    return latest_release


class Dataset(PtBaseModel):
    name: str
    description: str
    README: str


class DatasetsResult(PtBaseModel):
    release_id: str
    README: str
    datasets: list[Dataset]


def get_datasets_for_release(release: str) -> DatasetsResult:
    with httpx.Client() as client:
        url = f"{BASE_S2_URL}{release}"
        print(url)
        response = client.get(url)
    datasets_raw = response.json()
    parsed = DatasetsResult.model_validate(datasets_raw)
    return parsed


if __name__ == "__main__":
    latest_release = get_latest_release()
    datasets = get_datasets_for_release(latest_release)
    print(datasets)

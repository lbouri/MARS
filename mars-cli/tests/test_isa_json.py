from mars_lib.isa_json import (
    reduce_isa_json_for_target_repo,
    load_isa_json,
    update_investigation,
)
from mars_lib.target_repo import TargetRepository, TARGET_REPO_KEY
import pytest
from pydantic import ValidationError
from mars_lib.models.isa_json import Data, Material, Assay, Person, IsaJson
from mars_lib.models.repository_response import RepositoryResponse
import json


def test_load_isa_json():
    # Should test the validation process of the ISA JSON file where root level = investigation.
    valid_isa_json01 = load_isa_json(
        "../test-data/ISA-BH2023-ALL/isa-bh2023-all.json", True
    )
    assert len(valid_isa_json01.studies) == 1
    assert valid_isa_json01.studies[0].identifier == "BH2023"

    # Should test the validation process of the ISA JSON file where root has 'investigation' as key.
    valid_isa_json02 = load_isa_json("../test-data/biosamples-input-isa.json", False)
    assert len(valid_isa_json02.studies) == 1
    assert valid_isa_json02.studies[0].title == "Arabidopsis thaliana"

    with pytest.raises(ValidationError):
        load_isa_json("./tests/fixtures/invalid_investigation.json", True)


def test_reduce_isa_json_for_target_repo():
    good_isa_json = load_isa_json(
        "../test-data/ISA-BH2023-ALL/isa-bh2023-all.json", True
    )

    filtered_isa_json = reduce_isa_json_for_target_repo(
        good_isa_json, TargetRepository.ENA
    )

    good_isa_json_study = good_isa_json.studies[0]

    filtered_isa_json_study = filtered_isa_json.studies[0]

    assert len(good_isa_json_study.assays) == 5
    assert len(filtered_isa_json_study.assays) == 1


def test_reduce_isa_json_for_biosamples():
    good_isa_json = load_isa_json(
        "../test-data/ISA-BH2023-ALL/isa-bh2023-all.json", True
    )

    filtered_isa_json = reduce_isa_json_for_target_repo(
        good_isa_json, TargetRepository.BIOSAMPLES
    )

    assert len(filtered_isa_json.studies[0].assays) == 0


def test_data_type_validator():
    valid_data_json = {"@id": "data_001", "name": "data 1", "type": "Image File"}

    invalid_data_json = {
        "@id": "data_001",
        "name": "data 1",
        "type": "Custom File",  # This is not a valid data type
    }

    assert Data.model_validate(valid_data_json)

    with pytest.raises(ValidationError):
        Data.model_validate(invalid_data_json)


def test_material_type_validator():
    valid_material_json = {
        "@id": "material_001",
        "name": "material 1",
        "type": "Extract Name",
    }

    invalid_material_json = {
        "@id": "material_002",
        "name": "material 2",
        "type": "Custom Material",  # This is not a valid material type
    }

    assert Material.model_validate(valid_material_json)

    with pytest.raises(ValidationError):
        Material.model_validate(invalid_material_json)


def test_target_repo_comment_validator():
    valid_assay_json = {
        "@id": "assay_001",
        "comments": [
            {
                "@id": "comment_001",
                "name": "target repository",
                "value": TargetRepository.ENA,
            }
        ],
    }

    invalid_assay_json = {
        "@id": "assay_002",
        "comments": [
            {
                "@id": "comment_002",
                "name": "target repository",
                "value": "my special repo",
            }
        ],
    }

    second_invalid_assay_json = {"@id": "assay_003", "comments": []}

    third_invalid_assay_json = {
        "@id": "assay_004",
        "comments": [
            {
                "@id": "comment_003",
                "name": "target repository",
                "value": TargetRepository.ENA,
            },
            {
                "@id": "comment_004",
                "name": "target repository",
                "value": TargetRepository.METABOLIGHTS,
            },
        ],
    }

    assert Assay.model_validate(valid_assay_json)
    with pytest.raises(
        ValidationError, match="Invalid 'target repository' value: 'my special repo'"
    ):
        Assay.model_validate(invalid_assay_json)

    with pytest.raises(ValidationError, match="'target repository' comment is missing"):
        Assay.model_validate(second_invalid_assay_json)

    with pytest.raises(
        ValidationError, match="Multiple 'target repository' comments found"
    ):
        Assay.model_validate(third_invalid_assay_json)

    def test_person_phone_nr_validator():
        valid_person_json = {
            "@id": "person_001",
            "phone_nr": "+49123456789",
        }

        invalid_person_json = {
            "@id": "person_002",
            "phone_nr": "123456789",
        }

        assert Person.model_validate(valid_person_json)

        with pytest.raises(ValidationError, match="Invalid number format"):
            Person.model_validate(invalid_person_json)


def test_update_study_materials_no_accession_categories():
    # This file has no characteristics for accessions
    json_path = "../test-data/biosamples-original-isa-no-accesion-char.json"
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    validated_isa_json = IsaJson.model_validate(json_data)

    respose_file_path = "tests/fixtures/json_responses/biosamples_success_reponse.json"
    repo_response = RepositoryResponse.from_json_file(respose_file_path)

    updated_investigation = update_investigation(
        validated_isa_json.investigation, repo_response
    )

    # Check the accession number of the source
    # Accession characteristic is of type String
    assert (
        updated_investigation.studies[0].materials.sources[0].characteristics[-1].value
        == repo_response.accessions[0].value
    )

    # Check the accession number of the sample
    # Accession characteristic is of type String
    assert (
        updated_investigation.studies[0].materials.samples[0].characteristics[-1].value
        == repo_response.accessions[1].value
    )


def test_update_study_materials_with_accession_categories():
    # This file has no characteristics for accessions
    json_path = "../test-data/biosamples-original-isa.json"
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    validated_isa_json = IsaJson.model_validate(json_data)

    respose_file_path = "tests/fixtures/json_responses/biosamples_success_reponse.json"
    repo_response = RepositoryResponse.from_json_file(respose_file_path)

    updated_investigation = update_investigation(
        validated_isa_json.investigation, repo_response
    )
    # Check the accession number of the source
    # Accession characteristic is of type OntologyAnnotation
    assert (
        updated_investigation.studies[0]
        .materials.sources[0]
        .characteristics[-1]
        .value.annotationValue
        == repo_response.accessions[0].value
    )

    # Check the accession number of the sample
    # Accession characteristic is of type String
    assert (
        updated_investigation.studies[0].materials.samples[0].characteristics[-1].value
        == repo_response.accessions[1].value
    )

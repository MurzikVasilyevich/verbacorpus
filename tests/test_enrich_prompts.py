from enrich.prompts import pass_a_prompt, pass_b_prompt, PASS_A_SCHEMA, PASS_B_SCHEMA
from enrich.schema import load_taxonomy


def test_pass_a_prompt_contains_all_keys_and_path():
    tax = load_taxonomy()
    p = pass_a_prompt("/tmp/in/batch_0001.json", tax)
    for key in tax:
        assert key in p
    assert "/tmp/in/batch_0001.json" in p
    assert "1" in p and "3" in p              # multi-label range mentioned
    assert "idiom_expressive" in p


def test_pass_b_prompt_has_examples_and_path():
    p = pass_b_prompt("/tmp/in/batch_0001.json")
    assert "/tmp/in/batch_0001.json" in p
    assert "богато" in p                       # at least one glossed example
    assert "modern_text" in p


def test_schemas_are_arrays_of_objects():
    assert PASS_A_SCHEMA["type"] == "array"
    assert set(PASS_A_SCHEMA["items"]["required"]) == {"id", "categories", "explanation_clean"}
    assert set(PASS_B_SCHEMA["items"]["required"]) == {"id", "modern_text"}
